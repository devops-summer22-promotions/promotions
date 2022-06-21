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
        promo_1 = Promotion(name="Flash BOGO sale!", type=PromoType.BUY_ONE_GET_ONE, start_date=date.fromisoformat("2022-07-01"), end_date=date.fromisoformat("2022-07-02"))
        self.assertEqual(str(promo_1), "<Promotion 'Flash BOGO sale!' id=[None]>")
        self.assertTrue(promo_1 is not None)
        self.assertEqual(promo_1.id, None)
        self.assertEqual(promo_1.name, "Flash BOGO sale!")
        self.assertEqual(promo_1.type, PromoType.BUY_ONE_GET_ONE)
        self.assertEqual(promo_1.start_date, date.fromisoformat("2022-07-01"))
        self.assertEqual(promo_1.end_date, date.fromisoformat("2022-07-02"))
        # promo_1.create()
        # to test effects of creation, may need to test in routes instead ?
        promo_2 = Promotion(name="20 pct off coupon", type=PromoType.PERCENT_DISCOUNT, discount=20, start_date=date.fromisoformat("2022-07-01"), end_date=date.fromisoformat("2022-07-02"))
        self.assertEqual(str(promo_2), "<Promotion '20 pct off coupon' id=[None]>")
        self.assertTrue(promo_2 is not None)
        self.assertEqual(promo_2.id, None)
        self.assertEqual(promo_2.name, "20 pct off coupon")
        self.assertEqual(promo_2.type, PromoType.PERCENT_DISCOUNT)
        self.assertEqual(promo_2.discount, 20)
        self.assertEqual(promo_2.start_date, date.fromisoformat("2022-07-01"))
        self.assertEqual(promo_2.end_date, date.fromisoformat("2022-07-02"))
        promo_3 = Promotion(name="Free shipping July", type=PromoType.FREE_SHIPPING, start_date=date.fromisoformat("2022-07-01"), end_date=date.fromisoformat("2022-07-31"))
        self.assertEqual(str(promo_3), "<Promotion 'Free shipping July' id=[None]>")
        self.assertTrue(promo_3 is not None)
        self.assertEqual(promo_3.id, None)
        self.assertEqual(promo_3.name, "Free shipping July")
        self.assertEqual(promo_3.type, PromoType.FREE_SHIPPING)
        self.assertEqual(promo_3.start_date, date.fromisoformat("2022-07-01"))
        self.assertEqual(promo_3.end_date, date.fromisoformat("2022-07-31"))
        promo_4 = Promotion(name="VIP customer 123 half off", type=PromoType.VIP, discount=50, customer=123, start_date=date.fromisoformat("2022-07-01"), end_date=date.fromisoformat("2022-07-02"))
        self.assertEqual(str(promo_4), "<Promotion 'VIP customer 123 half off' id=[None]>")
        self.assertTrue(promo_4 is not None)
        self.assertEqual(promo_4.id, None)
        self.assertEqual(promo_4.name, "VIP customer 123 half off")
        self.assertEqual(promo_4.type, PromoType.VIP)
        self.assertEqual(promo_4.discount, 50)
        self.assertEqual(promo_4.customer, 123)
        self.assertEqual(promo_4.start_date, date.fromisoformat("2022-07-01"))
        self.assertEqual(promo_4.end_date, date.fromisoformat("2022-07-02"))


        # etc. -- create other promo types; add further tests for sad path, and so forth
