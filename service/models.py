"""
Models for Promotion

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class PromoType(Enum):
    """Enumeration of valid Promotion types"""

    BUY_ONE_GET_ONE = 0
    PERCENT_DISCOUNT = 1
    FREE_SHIPPING = 2
    VIP = 3 # can potentially interact w/ customer ID from customers team
    # etc., as desired
    UNKNOWN = 9


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    type = db.Column(db.Enum(PromoType), nullable=False, server_default=(PromoType.UNKNOWN.name))
    discount = db.Column(db.Integer, nullable=True, default=None) # could be a float, or just assume "whole point" percentage discounts as here (and convert later when necessary); null for non-PERCENT_DISCOUNT promos
    customer = db.Column(db.Integer, nullable=True, default=None) # e.g. for a VIP promotion / promos only applicable to a specific customer -- null by default
    start_date = db.Column(db.Date(), nullable=False) # date that promotion becomes effective
    end_date = db.Column(db.Date(), nullable=False) # date after which promotion is no longer effective

    def __repr__(self):
        return "<Promotion %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        serialized = {"id": self.id,
                      "name": self.name,
                      "type": self.type.name,
                      "discount": self.discount,
                      "customer": self.customer,
                      "start_date": self.start_date,
                      "end_date": self.end_date}
        # if self.type == PromoType.BUY_ONE_GET_ONE:
        #     serialized["type"] = 0
        # if self.type == PromoType.PERCENT_DISCOUNT:
        #     serialized["type"] = 1
        # if self.type == PromoType.FREE_SHIPPING:
        #     serialized["type"] = 2
        # if self.type == PromoType.VIP:
        #     serialized["type"] = 3
        return serialized

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.type = getattr(PromoType, data["type"]) # create enum from string
            self.discount = data["discount"]
            self.customer = data["customer"]
            self.start_date = data["start_date"]
            self.end_date = data["end_date"]
            # if data["type"] == 0:
            #     self.type = PromoType.BUY_ONE_GET_ONE
            # if data["type"] == 1:
            #     self.type = PromoType.PERCENT_DISCOUNT
            # if data["type"] == 2:
            #     self.type = PromoType.FREE_SHIPPING
            # if data["type"] == 3:
            #     self.type = PromoType.VIP
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Promotion by its ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
