"""
TestPromotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import PromoType, db, Promotion
from service.utils import status  # HTTP Status Codes
from service.utils.time_management import str_to_dt # helper functions for dealing with datetimes as created by Postgres
from tests.factories import PromoFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        self.client = self.app # some sort of naming expectation conflict in provided code; use both for now
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        pass

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # TODO: check additional information here after we decide what we want the index route to return
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Promotions REST API Service") #, etc.

    def test_create_promotion(self):
        """ It should create various kinds of promotions """
        test_promo = PromoFactory()
        test_promo.name = "foo"
        if test_promo.type == PromoType.PERCENT_DISCOUNT:
            test_promo.discount = 30
        if test_promo.type == PromoType.VIP:
            test_promo.discount = 55
            test_promo.customer = 123
        logging.debug("Test Promotion: %s", test_promo.serialize())
        response = self.app.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promo = response.get_json()
        self.assertEqual(new_promo["name"], test_promo.name)
        self.assertEqual(new_promo["type"], test_promo.type.name)
        if new_promo["type"] in [PromoType.PERCENT_DISCOUNT.name, PromoType.VIP.name]:
            self.assertEqual(new_promo["discount"], test_promo.discount)
        if new_promo["type"] == PromoType.VIP.name:
            self.assertEqual(new_promo["customer"], test_promo.customer)
        self.assertEqual(str_to_dt(new_promo["start_date"]), test_promo.start_date)
        self.assertEqual(str_to_dt(new_promo["end_date"]), test_promo.end_date)

        # Check that the location header was correct
        # TODO: figure out proper location URL construction technique -- not sure we can use "url_for()" (?)
        # response = self.client.get(location, content_type=CONTENT_TYPE_JSON)
        # logging.debug("Got location: %s", location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_promo = response.get_json()
        # self.assertEqual(new_promo["name"], test_promo.name)
        # self.assertEqual(new_promo["type"], test_promo.type.name)
        # if new_promo.type in [PromoType.PERCENT_DISCOUNT, PromoType.VIP]:
        #     self.assertEqual(new_promo["discount"], test_promo.discount)
        # if new_promo.type == PromoType.VIP:
        #     self.assertEqual(new_promo["customer"], test_promo.customer)
        # self.assertEqual(new_promo["start_date"], test_promo.start_date)
        # self.assertEqual(new_promo["end_date"], test_promo.end_date)
