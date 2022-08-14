"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, render_template, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from .utils import error_handlers, status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, PromoType, DataValidationError

# Import Flask application
from . import app, api

CONTENT_TYPE_JSON = "application/json"

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# DEFINE THE MODEL
######################################################################


create_model = api.model('Promotion', {
    'name': fields.String(required=True,
                          description='The name of the Promotion'),
    'type': fields.String(enum=PromoType._member_names_,
                          description='The type of the Promotion'),
    'discount': fields.Integer(required=False,
                               description='The percent discount represented as an integer'),
    'customer': fields.Integer(required=False,
                               description='The specific customer ID associated with a promotion, if applicable'),
    'start_date': fields.Date(required=True,
                              description='The date on which the promotion starts (at midnight)'),
    'end_date': fields.Date(required=True,
                            description='The date on which the promotion ends (at midnight)')
})

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True, # change to 'id' if this doesn't work; '_id' might be a couchdb thing
                             description='The unique ID assigned internally by the service')
    }
)


######################################################################
# PARSE REQUEST ARGUMENTS
######################################################################


promotion_args = reqparse.RequestParser()
promotion_args.add_argument('name', type=str, required=False, help='List Promotions by name')
promotion_args.add_argument('type', type=str, required=False, help='List Promotions by type')
promotion_args.add_argument('discount', type=int, required=False, help='List Promotions by percent discount')
promotion_args.add_argument('customer', type=int, required=False, help='List Promotions by associated customer ID')
promotion_args.add_argument('start_date', type=str, required=False, help='List Promotions by start date')
promotion_args.add_argument('end_date', type=str, required=False, help='List Promotions by end date')


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route('/promotions/<int:promo_id>')
@api.param('promo_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion/{id} - Returns a Promotion with the id
    PUT /promotion/{id} - Update a Promotion with the id
    DELETE /promotion/{id} -  Deletes a Promotion with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    #------------------------------------------------------------------
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promo_id):
        """
        Retrieve a single Promotion

        This endpoint will return a Promotion based on its ID
        """
        app.logger.info("Request to Retrieve a promotion with ID [%s]", promo_id)
        promo = Promotion.find(promo_id)
        if not promo:
            api.abort(status.HTTP_404_NOT_FOUND, "Promotion with ID [%s] not found.".format(promo_id))
        return promo.serialize(), status.HTTP_200_OK

        # if promo is None:
        #     app.logger.info("Promotion with ID [%s] not found.", promo_id)
        #     api.abort(status.HTTP_404_NOT_FOUND, f"Promotion {promo_id} not found.")

        # else:
        #     message = promo.serialize()
        #     location_url = api.url_for(PromotionResource, promo_id=promo.id, _external=True)
        #     app.logger.info("Promotion with ID [%s] found.", promo.id)
        #     return jsonify(message), status.HTTP_200_OK, {"Location": location_url}

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    #------------------------------------------------------------------
    @api.doc('update_promotions')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promo_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info('Request to Update a promotion with ID [%s]', promo_id)
        promo = Promotion.find(promo_id)
        if not promo:
            api.abort(status.HTTP_404_NOT_FOUND, "Promotion with ID '{}' was not found.".format(promo_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        promo.deserialize(data)
        promo.id = promo_id
        promo.update()
        app.logger.info("Promotion with ID [%s] updated.", promo.id)
        return promo.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PROMOTION
    #------------------------------------------------------------------
    @api.doc('delete_promotions')
    @api.response(204, 'Promotion deleted')
    def delete(self, promo_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the ID specified in the path
        """
        app.logger.info('Request to Delete a promotion with ID [%s]', promo_id)
        promo = Promotion.find(promo_id)
        if promo:
            promo.delete()
            app.logger.info('Promotion with ID [%s] was deleted', promo_id)

        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """
    #------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    #------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """ Returns all of the Promotions """
        app.logger.info('Request to list Promotions...')
        promotions = []
        app.logger.info('About to parse arguments')
        args = promotion_args.parse_args()
        app.logger.info('Parsed args successfully')
        # app.logger.info("args = %s", args)
        promotions = Promotion.all()

        if args['type']:
            query_type = args['type']
            app.logger.info("type = %s", query_type)
            promotions = filter(lambda x: (
                query_type == str(x.type.name)), promotions)

        if args['name']:
            query_name = args['name']
            app.logger.info("name contains %s", query_name)
            promotions = filter(lambda x: (query_name in x.name), promotions)

        if args['discount']:
            query_discount = args['discount']
            app.logger.info("discount = %s", query_discount)
            promotions = filter(lambda x: (
                int(query_discount) == x.discount), promotions)

        if args['customer']:
            query_customer = args['customer']
            app.logger.info("customer = %s", query_customer)
            promotions = filter(lambda x: (
                int(query_customer) == x.customer), promotions)

        if args['start_date']:
            query_start_date = args['start_date']
            app.logger.info("start_date = %s", query_start_date)
            promotions = filter(lambda x: query_start_date ==
                                '{:%Y-%m-%d}'.format(x.start_date), promotions)

        if args['end_date']:
            query_end_date = args['end_date']
            app.logger.info("end_date = %s", query_end_date)
            promotions = filter(lambda x: query_end_date ==
                                '{:%Y-%m-%d}'.format(x.end_date), promotions)

        results = [promo.serialize() for promo in promotions]
        app.logger.info("Returning %d promotions", len(results))
        return results, status.HTTP_200_OK


    #------------------------------------------------------------------
    # ADD A NEW PROMOTION
    #------------------------------------------------------------------
    @api.doc('create_promotion')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Pet
        This endpoint will create a Pet based the data in the body that is posted
        """
        app.logger.info("Request to create a Promotion")
        promo = Promotion()
        app.logger.debug('Payload = %s', api.payload)
        promo.deserialize(api.payload)
        # check for empty string fields and convert to null type
        if promo.customer == "":
            promo.customer = None
        if promo.discount == "":
            promo.discount = None
        # check to see if this is a duplicate
        named_promos = Promotion.find_by_name(promo.name)
        if (named_promos != []):
            for other_promo in named_promos:
                if check_duplicate(promo, other_promo):
                    api.abort(status.HTTP_409_CONFLICT,
                        "Attempt to create duplicate Promotion")
        promo.create()
        message = promo.serialize()
        location_url = api.url_for(PromotionResource, promo_id=promo.id, _external=True)

        app.logger.info("Promotion with ID [%s] created.", promo.id)
        return promo.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

    # #------------------------------------------------------------------
    # # DELETE ALL PETS (for testing only)
    # #------------------------------------------------------------------
    # @api.doc('delete_all_promotions')
    # @api.response(204, 'All Promotions deleted')
    # def delete(self):
    #     """
    #     Delete all Promotions

    #     This endpoint will delete all Promotions only if the system is under test
    #     """
    #     app.logger.info('Request to Delete all promotions...')
    #     # NO NEED FOR THIS IN HOMEWORK - CAN JUST CLEAR THE DATABASE TABLE
    #     if "TESTING" in app.config and app.config["TESTING"]:
    #         Promotion.remove_all()
    #         app.logger.info("Removed all Pets from the database")
    #     else:
    #         app.logger.warning("Request to clear database while system not under test")

    #     return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions/{id}/cancel
######################################################################
@api.route('/promotions/<promo_id>/cancel')
@api.param('pet_id', 'The Pet identifier')
class CancelResource(Resource):
    """ Cancel action on a Promotion """
    @api.doc('cancel_promotion')
    @api.response(404, 'Promotion not found')
    @api.response(409, 'The Promotion is not available to be cancelled')
    def put(self, promo_id):
        """
        Cancel a Promotion early

        This endpoint will set the end date of Promotion with ID `promo_id` to its start date.
        A Promotion with equal start and end dates is semantically considered canceled.
        """
        app.logger.info("Request to cancel a Promotion with id: %s", promo_id)
        # attempt to locate Promotion for early cancellation
        promotion = Promotion.find(promo_id)
        if not promotion:
            api.abort(status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promo_id}' was not found.")
        # set the information
        promotion.end_date = promotion.start_date
        promotion.update()
        app.logger.info("Promotion with ID [%s] has been canceled.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK





#######################
# ORIGINAL CODE BELOW #
#######################

# ######################################################################
# # ADD A NEW PROMOTION
# ######################################################################


# @app.route("/promotions", methods=["POST"])
# def create_promo():
#     """
#     Creates a Promotion
#     This endpoint will create a Promotion based the data in the body that is posted
#     """
#     app.logger.info("Request to create a promotion")
#     check_content_type(CONTENT_TYPE_JSON)
#     promo = Promotion()
#     promo.deserialize(request.get_json())

#     # check whether customer id is an integer
#     if promo.customer == "":
#         promo.customer = None

#     if promo.customer != None:
#         try:
#             id = int(promo.customer)
#         except:
#             app.logger.info(
#                 "Customer ID [%s] is not a number.", promo.customer)
#             abort(status.HTTP_400_BAD_REQUEST,
#                   f"Customer ID {promo.customer} should be a number.")

#     # check to see if this is a duplicate
#     named_promos = Promotion.find_by_name(promo.name)
#     if (named_promos != []):
#         for other_promo in named_promos:
#             if check_duplicate(promo, other_promo):
#                 abort(status.HTTP_409_CONFLICT,
#                       "Attempt to create duplicate Promotion")
#     promo.create()
#     message = promo.serialize()
#     location_url = url_for("create_promo", promo_id=promo.id, _external=True)

#     app.logger.info("Promotion with ID [%s] created.", promo.id)
#     return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


# ######################################################################
# # FIND A PROMOTION BY ID
# ######################################################################


# @app.route("/promotions/<promo_id>", methods=["GET"])
# def find_promo(promo_id):
#     """
#     Finds a Promotion
#     This endpoint will find a Promotion by id
#     """
#     app.logger.info("Request to find a promotion")

#     # check wether the id is a number
#     try:
#         id = int(promo_id)
#     except:
#         app.logger.info("Promotion ID [%s] is not a number.", promo_id)
#         abort(status.HTTP_400_BAD_REQUEST,
#               f"Promotion ID {promo_id} should be a number.")

#     # check whether the id is in range
#     if int(promo_id) > 2147483647 or int(promo_id) < 0:
#         app.logger.info("Promotion ID [%s] is out of range.", promo_id)
#         abort(status.HTTP_400_BAD_REQUEST,
#               f"Promotion ID {promo_id} is out of range.")

#     promo = Promotion.find(promo_id)

#     if promo is None:
#         app.logger.info("Promotion with ID [%s] not found.", promo_id)
#         abort(status.HTTP_404_NOT_FOUND, f"Promotion {promo_id} not found.")

#     else:
#         message = promo.serialize()
#         location_url = url_for("find_promo", promo_id=promo.id, _external=True)
#         app.logger.info("Promotion with ID [%s] found.", promo.id)
#         return jsonify(message), status.HTTP_200_OK, {"Location": location_url}


# ######################################################################
# # DELETE A PROMOTION
# ######################################################################


# @app.route("/promotions/<promo_id>", methods=["DELETE"])
# def delete_promo(promo_id):
#     """
#     Delete a Promo

#     This endpoint will delete a promotion based the id specified in the path
#     """
#     app.logger.info("Request to delete promo with id: %s", promo_id)
#     promo = Promotion.find(promo_id)
#     print(promo)
#     if promo:
#         promo.delete()

#     app.logger.info("Promo with ID [%s] delete complete.", promo_id)
#     return "", status.HTTP_204_NO_CONTENT

# ######################################################################
# # LIST ALL PROMOTIONS
# ######################################################################


# @app.route("/promotions", methods=["GET"])
# def list_promos():
#     """Returns all of the Promos"""
#     app.logger.info("Request for promo list")
#     promotions = []

#     # check whether query condition is supported
#     for key in request.args.keys():
#         if not (key in ["type", "name", "discount", "customer", "start_date", "end_date"]):
#             abort(status.HTTP_400_BAD_REQUEST,
#                   f"unsupported query condition: {key}")

#     promotions = Promotion.all()

#     query_type = request.args.get('type')
#     if query_type != None:
#         app.logger.info("type = %s", query_type)
#         promotions = filter(lambda x: (
#             query_type == str(x.type.name)), promotions)

#     query_name = request.args.get('name')
#     if query_name != None:
#         app.logger.info("name contains %s", query_name)
#         promotions = filter(lambda x: (query_name in x.name), promotions)

#     query_discount = request.args.get('discount')
#     if query_discount != None:
#         app.logger.info("discount = %s", query_discount)
#         promotions = filter(lambda x: (
#             int(query_discount) == x.discount), promotions)

#     query_customer = request.args.get('customer')
#     if query_customer != None:
#         app.logger.info("customer = %s", query_customer)
#         promotions = filter(lambda x: (
#             int(query_customer) == x.customer), promotions)

#     query_start_date = request.args.get('start_date')
#     if query_start_date != None:
#         app.logger.info("start_date = %s", query_start_date)
#         promotions = filter(lambda x: query_start_date ==
#                             '{:%Y-%m-%d}'.format(x.start_date), promotions)

#     query_end_date = request.args.get('end_date')
#     if query_end_date != None:
#         app.logger.info("end_date = %s", query_end_date)
#         promotions = filter(lambda x: query_end_date ==
#                             '{:%Y-%m-%d}'.format(x.end_date), promotions)

#     results = [promo.serialize() for promo in promotions]
#     app.logger.info("Returning %d promotions", len(results))
#     return jsonify(results), status.HTTP_200_OK

# ######################################################################
# # UPDATE AN EXISTING PROMOTION
# ######################################################################


# @app.route("/promotions/<promo_id>", methods=["PUT"])
# def update_promotions(promo_id):
#     """
#     Update a Promotion

#     This endpoint will update a Promotion based the body that is posted
#     """
#     app.logger.info("Request to update promotion with id: %s", promo_id)
#     check_content_type(CONTENT_TYPE_JSON)

#     # check wether the id is a number
#     # try:
#     #     id = int(promo_id)
#     # except:
#     #     app.logger.info("Promotion ID [%s] is not a number.", promo_id)
#     #     abort(status.HTTP_400_BAD_REQUEST,
#     #           f"Promotion ID {promo_id} should be a number.")

#     # # check whether the id is in range
#     # if int(promo_id) > 2147483647 or int(promo_id) < 0:
#     #     app.logger.info("Promotion ID [%s] is out of range.", promo_id)
#     #     abort(status.HTTP_400_BAD_REQUEST,
#     #           f"Promotion ID {promo_id} is out of range.")
#     data = request.get_json()
#     app.logger.info(data)

#     promotion = Promotion.find(promo_id)
#     if not promotion:
#         abort(status.HTTP_404_NOT_FOUND,
#               f"Promotion with id '{promo_id}' was not found.")

#     data = request.get_json()
#     app.logger.info(data)

#     promotion.deserialize(request.get_json())
#     promotion.id = promo_id
#     promotion.update()

#     app.logger.info("Promotion with ID [%s] updated.", promotion.id)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# EARLY CANCEL AN EXISTING PROMOTION
######################################################################


# @app.route("/promotions/<promo_id>/cancel", methods=["PUT"])
# def early_cancel_promotion(promo_id):
#     """
#     Cancel a Promotion early

#     This endpoint will set the end date of Promotion with ID `promo_id` to its start date.
#     A Promotion with equal start and end dates is semantically considered canceled.
#     """
#     app.logger.info("Request to cancel a Promotion with id: %s", promo_id)
#     # attempt to locate Promotion for early cancellation
#     promotion = Promotion.find(promo_id)
#     if not promotion:
#         abort(status.HTTP_404_NOT_FOUND,
#               f"Promotion with id '{promo_id}' was not found.")
#     # set the information
#     promotion.end_date = promotion.start_date
#     promotion.update()
#     app.logger.info("Promotion with ID [%s] has been canceled.", promotion.id)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)

# Flask-RESTX only works with JSON content
# def check_content_type(media_type):
#     """Checks that the media type is correct"""
#     content_type = request.headers.get("Content-Type")
#     if content_type and content_type == media_type:
#         return
#     app.logger.error("Invalid Content-Type: %s", content_type)
#     api.abort(
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#         "Content-Type must be {}".format(media_type),
#     )


def check_duplicate(p1, p2):
    """
    Checks to see if two Promotions are duplicates.
    Promotions are defined to be duplicates if they have the same
    name and type.
    """
    if (p1.name == p2.name) and (p1.type == p2.type):
        return True
    return False
