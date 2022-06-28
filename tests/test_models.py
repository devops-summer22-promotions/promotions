"""
Test cases for Promotion Model

"""
import os
import logging
import unittest
from datetime import date
from service import app
from service.models import Promotion, PromoType, DataValidationError, db
from tests.factories import PromoFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
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
        promo_1.create()
        # to test effects of creation, may need to test in routes instead ?
        # perhaps not -- was a different bug with the DB; should be able to test here as well
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

    def test_create_promo_bad_deserialize(self):
        """It should raise an exception when attempting to deserialize bad data"""
        data = "not a serialized dictionary"
        test_promo = Promotion()
        self.assertRaises(DataValidationError, test_promo.deserialize, data)
    
    def test_list_all_promotion(self):
        """It should list all promotions in the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        #Create 5 promotions
        for i in range(5):
            promo = PromoFactory()
            promo.create()
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 5)
        
    def test_update_a_promotion(self):
        """It should update a promotion"""
        promotion = PromoFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)
        # Change it an save it
        promotion.type = PromoType.BUY_ONE_GET_ONE
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.type, PromoType.BUY_ONE_GET_ONE)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, original_id)
        self.assertEqual(promotions[0].type, PromoType.BUY_ONE_GET_ONE)

    def test_update_no_id(self):
        """It should not update a promotion with no id"""
        promotion = PromoFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_a_promotion(self):
        """It should Delete a Promotion"""
        promotion = PromoFactory()
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_find_promotion_by_id(self):
        """It should find a promotion by id"""
        promo = PromoFactory()
        promo.create()
        db.session.refresh(promo) 
        id =  promo.id
        print(f"Created a promotion, id = {promo.id}")
        inserted_promo = Promotion.find(id)
        self.assertIsNotNone(inserted_promo)

    