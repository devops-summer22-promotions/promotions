"""
Models for Promotion

All of the models are stored in this module
"""
import logging
from datetime import date
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


VALID_TYPES = ["BUY_ONE_GET_ONE", "PERCENT_DISCOUNT", "FREE_SHIPPING", "VIP"]

class PromoType(Enum):
    """Enumeration of valid Promotion types"""

    BUY_ONE_GET_ONE = 0
    PERCENT_DISCOUNT = 1
    FREE_SHIPPING = 2
    VIP = 3  # can potentially interact w/ customer ID from customers team
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
    type = db.Column(db.Enum(PromoType), nullable=False,
                     server_default=(PromoType.UNKNOWN.name))
    # could be a float, or just assume "whole point" percentage discounts as here (and convert later when necessary); null for non-PERCENT_DISCOUNT promos
    discount = db.Column(db.Integer, nullable=True, default=None)
    # e.g. for a VIP promotion / promos only applicable to a specific customer -- null by default
    customer = db.Column(db.Integer, nullable=True, default=None)
    # date that promotion becomes effective
    start_date = db.Column(db.Date(), nullable=False)
    # date after which promotion is no longer effective
    end_date = db.Column(db.Date(), nullable=False)

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
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        try:
            serialized = {"id": self.id,
                          "name": self.name,
                          "type": self.type.name,
                          "discount": self.discount,
                          "customer": self.customer,
                          "start_date": self.start_date.isoformat(),
                          "end_date": self.end_date.isoformat()}
        except:
            logger.warn("Unable to serialize Promotion data")
            serialized = {}

        return serialized

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            # create enum from string

            if (data["type"] in VALID_TYPES):
                self.type = getattr(PromoType, data["type"])
            else:
                raise TypeError
            self.discount = data["discount"]
            self.customer = data["customer"]
            self.start_date = date.fromisoformat(data["start_date"])
            self.end_date = date.fromisoformat(data["end_date"])
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
    def find_by_name(cls, name: str) -> list:
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name.contains(name))
    
    @classmethod
    def find_by_type(cls, type: str) -> list:
        """Returns all of the Promotions in a type

        :param type: the type of the Promotions you want to match
        :type of type: str

        :return: a collection of Promotions in that type
        :rtype: list

        """
        logger.info("Processing type query for %s ...", type)
        return cls.query.filter(cls.type == type)


    @classmethod
    def find_by_discount(cls, discount) -> list:
        """Returns all of the Promotions with same discount rate

        :param discount: the discount rate of the Promotions you want to match
        :type of discount: integer

        :return: a collection of Promotions with same discount rate
        :rtype: list

        """
        logger.info("Processing discount query for %s ...", discount)
        return cls.query.filter(cls.discount == discount)


    @classmethod
    def find_by_customer(cls, customer) -> list:
        """Returns all of the Promotions under same customer ID

        :param customer: the customer ID of the Promotions you want to match
        :type of customer: integer

        :return: a collection of Promotions under same customer ID
        :rtype: list

        """
        logger.info("Processing customer ID query for %s ...", customer)
        return cls.query.filter(cls.customer == customer)


    @classmethod
    def find_by_start_date(cls, start_date) -> list:
        """Returns all of the Promotions under same start_date

        :param type: the start_date of the Promotions you want to match
        :type of start_date: Date()

        :return: a collection of Promotions under same start_date
        :rtype: list

        """
        logger.info("Processing start_date query for %s ...", start_date)
        return cls.query.filter(cls.start_date == start_date)
        

    @classmethod
    def find_by_end_date(cls, end_date) -> list:
        """Returns all of the Promotions under same end_date

        :param type: the end_date of the Promotions you want to match
        :type of end_date: Date()

        :return: a collection of Promotions under same end_date
        :rtype: list

        """
        logger.info("Processing end_date query for %s ...", end_date)
        return cls.query.filter(cls.end_date == end_date)

