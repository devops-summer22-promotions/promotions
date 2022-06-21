"""
Test cases for Promotion Model

"""
import os
import logging
import unittest
from datetime import date
from service import app
from service.models import Promotion, PromoType, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  <your resource name>   M O D E L   T E S T   C A S E S
######################################################################
class TestPromotionModel(unittest.TestCase):
    """ Test Cases for Promotion Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_promotion(self):
        """ It should create a new promotion of various types and assert that it exists """
        promo_1 = Promotion(name="Flash BOGO sale!", type=PromoType.BUY_ONE_GET_ONE, start_date=date.fromisoformat("01-01-2022"), end_date=date.fromisoformat("01-02-2022"))
        self.assertEqual(promo_1, "<Promotion Flash BOGO sale! id=[None]>")
        self.assertTrue(promo_1 is not None)
        self.assertEqual(promo_1.id, None)
        self.assertEqual(promo_1.name, "Flash BOGO sale!")
        self.assertEqual(promo_1.type, PromoType.BUY_ONE_GET_ONE)
        self.assertEqual(promo_1.start_date, date.fromisoformat("01-01-2022"))
        self.assertEqual(promo_1.end_date, date.fromisoformat("01-02-2022"))
        # etc.
