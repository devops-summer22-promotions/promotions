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
    # @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """ Returns all of the Promotions """
        app.logger.info('Request to list Promotions...')
        promotions = []
        app.logger.info('About to parse arguments')
        # args = promotion_args.parse_args()
        args = {}
        args["name"] = request.args.get("name")
        args["type"] = request.args.get("type")
        args["discount"] = request.args.get("discount")
        args["customer"] = request.args.get("customer")
        args["start_date"] = request.args.get("start_date")
        args["end_date"] = request.args.get("end_date")
        app.logger.info('Parsed args successfully')
        app.logger.info("args = %s", args)
        # promotions = Promotion.all()
        promotions = []
        filtered = False

        if args['type']:
            filtered = True
            query_type = args['type']
            # flask-restx request parsing is not working, so manually check this enum for bad argument
            if query_type not in ['BUY_ONE_GET_ONE', 'PERCENT_DISCOUNT', 'FREE_SHIPPING', 'VIP', 'UNKNOWN']:
                return "Bad query argument for type", status.HTTP_400_BAD_REQUEST
            app.logger.info("type = %s", query_type)
            promotions += Promotion.find_by_type(query_type)

        if args['name']:
            filtered = True
            query_name = args['name']
            app.logger.info("name contains %s", query_name)
            promotions += Promotion.find_by_name(query_name)

        if args['discount']:
            filtered = True
            query_discount = args['discount']
            app.logger.info("discount = %s", query_discount)
            promotions += Promotion.find_by_discount(query_discount)

        if args['customer']:
            filtered = True
            query_customer = args['customer']
            app.logger.info("customer = %s", query_customer)
            promotions += Promotion.find_by_customer(query_customer)

        if args['start_date']:
            filtered = True
            query_start_date = args['start_date']
            app.logger.info("start_date = %s", query_start_date)
            promotions += Promotion.find_by_start_date(query_start_date)

        if args['end_date']:
            filtered = True
            query_end_date = args['end_date']
            app.logger.info("end_date = %s", query_end_date)
            promotions += Promotion.find_by_end_date(query_end_date)

        app.logger.info(f"promotions: \n{promotions}")

        # kludgy check for no match on query
        # if len(promotions) == 1 and filtered:
        #     test_serialize = promotions[0].serialize()
        #     if all([True for item in list(test_serialize.values()) if item is None]):
        #         return "No results found for query string", status.HTTP_404_NOT_FOUND

        if promotions == []:
            if filtered:
                return "No results found for query string", status.HTTP_404_NOT_FOUND
            else:
                # if we didn't have any filters, just return all promotions in the database
                promotions = Promotion.all()
        else:
            # remove dupes if multiple filters found the same promotions in the database
            promotions = list(set(promotions))

        results = [promo.serialize() for promo in promotions]
        if not isinstance(results, list):
            results = [results]
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
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
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


######################################################################
#  PATH: /promotions/{id}/cancel
######################################################################
@api.route('/promotions/<promo_id>/cancel')
@api.param('promo_id', 'The Promotion identifier')
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


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)

def check_duplicate(p1, p2):
    """
    Checks to see if two Promotions are duplicates.
    Promotions are defined to be duplicates if they have the same
    name and type.
    """
    if (p1.name == p2.name) and (p1.type == p2.type):
        return True
    return False
