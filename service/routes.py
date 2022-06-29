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
# DELETE A PROMO
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
# LIST ALL PROMO
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promos():
    """Returns all of the Promos"""
    app.logger.info("Request for promo list")
    promotions = []
    type = request.args.get("type")
    name = request.args.get("name")
    if type:
        promotions = Promotion.find_by_type(type)
    elif name:
        promotions = Promotion.find_by_name(name)
    else:
        promotions = Promotion.all()

    results = [promo.serialize() for promo in promotions]
    app.logger.info("Returning %d promotions", len(results))
    return jsonify(results), status.HTTP_200_OK

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
