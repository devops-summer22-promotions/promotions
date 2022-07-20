"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from .utils import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, DataValidationError

# Import Flask application
from . import app

CONTENT_TYPE_JSON = "application/json"

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Promotion REST API Service",
            version="1.0",
            paths=url_for("list_promos", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# ADD A NEW PROMOTION
######################################################################


@app.route("/promotions", methods=["POST"])
def create_promo():
    """
    Creates a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a promotion")
    check_content_type(CONTENT_TYPE_JSON)
    promo = Promotion()
    promo.deserialize(request.get_json())
    # check to see if this is a duplicate
    named_promos = Promotion.find_by_name(promo.name)
    if (named_promos != []):
        for other_promo in named_promos:
            if check_duplicate(promo, other_promo):
                abort(status.HTTP_409_CONFLICT, "Attempt to create duplicate Promotion")
    promo.create()
    message = promo.serialize()
    location_url = url_for("create_promo", promo_id=promo.id, _external=True)

    app.logger.info("Promotion with ID [%s] created.", promo.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# FIND A PROMOTION BY ID
######################################################################


@app.route("/promotions/<promo_id>", methods=["GET"])
def find_promo(promo_id):
    """
    Finds a Promotion
    This endpoint will find a Promotion by id
    """
    app.logger.info("Request to find a promotion")

    # check wether the id is a number
    try:
        id = int(promo_id)
    except:
        app.logger.info("Promotion ID [%s] is not a number.", promo_id)
        abort(status.HTTP_400_BAD_REQUEST, f"Promotion ID {promo_id} should be a number.")

    # check whether the id is in range
    if int(promo_id) > 2147483647 or int(promo_id) < 0:
        app.logger.info("Promotion ID [%s] is out of range.", promo_id)
        abort(status.HTTP_400_BAD_REQUEST, f"Promotion ID {promo_id} is out of range.")
    
    promo = Promotion.find(promo_id)

    if promo is None:
        app.logger.info("Promotion with ID [%s] not found.", promo_id)
        abort(status.HTTP_404_NOT_FOUND, f"Promotion {promo_id} not found.")

    else:
        message = promo.serialize()
        location_url = url_for("find_promo", promo_id=promo.id, _external=True)
        app.logger.info("Promotion with ID [%s] found.", promo.id)
        return jsonify(message), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# DELETE A PROMOTION
######################################################################


@app.route("/promotions/<promo_id>", methods=["DELETE"])
def delete_promo(promo_id):
    """
    Delete a Promo

    This endpoint will delete a promotion based the id specified in the path
    """
    app.logger.info("Request to delete promo with id: %s", promo_id)
    promo = Promotion.find(promo_id)
    print(promo)
    if promo:
        promo.delete()

    app.logger.info("Promo with ID [%s] delete complete.", promo_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# LIST ALL PROMOTIONS
######################################################################


@app.route("/promotions", methods=["GET"])
def list_promos():
    """Returns all of the Promos"""
    app.logger.info("Request for promo list")
    promotions = []

    # check whether query condition is supported
    for key in request.args.keys():
        if not (key in ["type", "name", "discount", "customer", "start_date", "end_date"]):
            abort(status.HTTP_400_BAD_REQUEST, f"unsupported query condition: {key}")

    promotions = Promotion.all()

    query_type = request.args.get('type')
    if query_type != None:
        app.logger.info("type = %s", query_type)
        promotions = filter(lambda x: (query_type == str(x.type.name)), promotions)

    query_name = request.args.get('name')
    if query_name != None:
        app.logger.info("name contains %s", query_name)
        promotions = filter(lambda x: (query_name in x.name), promotions)

    query_discount = request.args.get('discount')
    if query_discount != None:
        app.logger.info("discount = %s", query_discount)
        promotions = filter(lambda x: (int(query_discount) == x.discount), promotions)
    
    query_customer = request.args.get('customer')
    if query_customer != None:
        app.logger.info("customer = %s", query_customer)
        promotions = filter(lambda x: (int(query_customer) == x.customer), promotions)

    query_start_date = request.args.get('start_date')
    if query_start_date != None:
        app.logger.info("start_date = %s", query_start_date)
        promotions = filter(lambda x: query_start_date == '{:%Y-%m-%d}'.format(x.start_date), promotions)

    query_end_date = request.args.get('end_date')
    if query_end_date != None:
        app.logger.info("end_date = %s", query_end_date)
        promotions = filter(lambda x: query_end_date == '{:%Y-%m-%d}'.format(x.end_date), promotions)

    results = [promo.serialize() for promo in promotions]
    app.logger.info("Returning %d promotions", len(results))
    return jsonify(results), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<promo_id>", methods=["PUT"])
def update_promotions(promo_id):
    """
    Update a Promotion

    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to update promotion with id: %s", promo_id)
    check_content_type(CONTENT_TYPE_JSON)

    promotion = Promotion.find(promo_id)
    if not promotion:
        abort(status.HTTP_404_NOT_FOUND, f"Promotion with id '{promo_id}' was not found.")

    promotion.deserialize(request.get_json())
    promotion.id = promo_id
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# EARLY CANCEL AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<promo_id>/cancel", methods=["PUT"])
def early_cancel_promotion(promo_id):
    """
    Cancel a Promotion early

    This endpoint will set the end date of Promotion with ID `promo_id` to its start date.
    A Promotion with equal start and end dates is semantically considered canceled.
    """
    app.logger.info("Request to cancel a Promotion with id: %s", promo_id)
    # attempt to locate Promotion for early cancellation
    promotion = Promotion.find(promo_id)
    if not promotion:
        abort(status.HTTP_404_NOT_FOUND, f"Promotion with id '{promo_id}' was not found.")
    # set the information
    promotion.end_date = promotion.start_date
    promotion.update()
    app.logger.info("Promotion with ID [%s] has been canceled.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

def check_duplicate(p1, p2):
    """
    Checks to see if two Promotions are duplicates.
    Promotions are defined to be duplicates if they have the same
    name and type.
    """
    if (p1.name == p2.name) and (p1.type == p2.type):
        return True
    return False
