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
# helper functions for dealing with datetimes as created by Postgres
from service.utils.time_management import str_to_dt
from tests.factories import PromoFactory
import datetime


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
        self.client = app.test_client()
        # some sort of naming expectation conflict in provided code; use both for now
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        pass

    def _create_promotion(self, count):
        """Factory method to create pets in bulk"""
        promo = []
        for _ in range(count):
            test_promotion = PromoFactory()
            response = self.client.post(
                BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test pet"
            )
            new_promo = response.get_json()
            test_promotion.id = new_promo["id"]
            promo.append(test_promotion)
        return promo

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # TODO: check additional information here after we decide what we want the index route to return
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Promotions REST API Service") #, etc.
        self.assertIn(b"Promotions REST API Service", resp.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

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
        response = self.client.post(
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
        self.assertEqual(
            str_to_dt(new_promo["start_date"]), test_promo.start_date)
        self.assertEqual(str_to_dt(new_promo["end_date"]), test_promo.end_date)

    def test_create_promo_customer_id_empty_string(self):
        """It should create a Promotion with customer id set to empty string"""
        test_promo = PromoFactory()
        test_promo.customer = ""
        logging.debug(test_promo)
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        test_promotion = self._create_promotion(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_promo_no_data(self):
        """It should not create a Promotion with missing data"""
        response = self.client.post(
            BASE_URL,
            json={},
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promo_bad_available(self):
        """It should not create a Promotion with bad available data"""
        test_promo = PromoFactory()
        logging.debug(test_promo)
        # change some data to a bad type:
        test_promo.type = 2
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promo_bad_method(self):
        """It should not create a Promotion via a GET request"""
        test_promo = PromoFactory()
        logging.debug(test_promo)
        # attempt promo creation via HTTP GET:
        response = self.client.get(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )

    def test_create_promo_bad_duplicate(self):
        """It should not create a duplicate Promotion"""
        test_promo = PromoFactory()
        test_promo.name = "foo"
        response_1 = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        response_2 = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response_2.status_code, status.HTTP_409_CONFLICT)

    def test_create_promo_customer_not_integer(self):
        """It should not a Promotion with non-integer customer id"""
        test_promo = PromoFactory()
        test_promo.customer = "x"
        logging.debug(test_promo)
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_content_type(self):
        """It should correctly detect a bad content type"""
        non_json = "text/html"
        test_promo = PromoFactory()
        logging.debug(test_promo)
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=non_json
        )
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_find_promo_by_id(self):
        """It should create a Promotion and find it by ID"""
        test_promo = PromoFactory()
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_promo = response.get_json()
        id = new_promo["id"]

        response = self.client.get(
            BASE_URL + '/' + str(id),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promo_1 = response.get_json()
        self.assertEqual(new_promo_1["id"], id)

    def test_find_promo_by_id_not_found(self):
        """It should not find a Promotion that does not exist"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])

        response = self.client.get(
            BASE_URL + '/' + '1',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_find_promo_by_id_post(self):
        """It should not find a Promotion via an HTTP POST method"""
        response = self.client.post(
            BASE_URL + '/' + '1',
        )
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_find_promo_by_id_not_a_number(self):
        """It should not find a Promotion with a non-numeric ID"""
        response = self.client.get(
            BASE_URL + '/' + 'a',
        )
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_find_promo_by_id_out_of_range(self):
        """It should not find a Promotion with an ID number out of range"""
        response = self.client.get(
            BASE_URL + '/' + '2147483648',
        )
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        
    def test_update_promotion(self):
        """It should update an existing Promotion"""
        # create a promotion to update
        test_promo = PromoFactory()
        response = self.client.post(BASE_URL, json=test_promo.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promo = response.get_json()
        id = new_promo["id"]
        logging.debug(new_promo)
        new_promo["name"] = "GOOD"
        response = self.client.put(BASE_URL + '/' + str(id), json=new_promo)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promo = response.get_json()
        self.assertEqual(updated_promo["name"], "GOOD")
        
    def test_update_promotion_not_exists(self):
        """It should not update a Promotion that does not exist"""
        # create a promotion to update
        test_promo = PromoFactory()
        response = self.client.post(BASE_URL, json=test_promo.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promo = response.get_json()
        id = new_promo["id"] + 1
        logging.debug(new_promo)
        new_promo["name"] = "GOOD"
        response = self.client.put(BASE_URL + '/' + str(id), json=new_promo)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_promotion(self):
        """It should early cancel a Promotion that exists by setting end_date equal to start_date"""
        # create a Promotion to cancel
        test_promo = PromoFactory()
        response_1 = self.client.post(BASE_URL, json=test_promo.serialize())
        new_promo = response_1.get_json()
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        # cancel the Promotion that was just created
        promo_id = new_promo["id"]
        response_2 = self.client.put(BASE_URL + '/' + str(promo_id) + "/cancel")
        updated_promo = response_2.get_json()
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_promo["start_date"], updated_promo["end_date"])

    def test_cancel_promotion_not_exists(self):
        """It should not early cancel a Promotion that does not exist"""
        # create a Promotion to generate the highest current ID
        test_promo = PromoFactory()
        response_1 = self.client.post(BASE_URL, json=test_promo.serialize())
        new_promo = response_1.get_json()
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        bad_id = new_promo["id"] + 1
        response_2 = self.client.put(BASE_URL + '/' + str(bad_id) + "/cancel")
        self.assertEqual(response_2.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_promotion(self):
        """ It should fetch a promotion by query conditions """
        test_promo = PromoFactory()
        test_promo.name = "foo"
        test_promo.type = PromoType.PERCENT_DISCOUNT
        test_promo.discount = 30
        test_promo.customer = 123
        test_promo.start_date = datetime.date(2022, 7, 19)
        test_promo.end_date = datetime.date(2022, 7, 20)

        logging.debug("Test Promotion: %s", test_promo.serialize())
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(BASE_URL, query_string={
            "name":"f",
            "type":"PERCENT_DISCOUNT",
            "discount":"30",
            "customer":"123",
            "start_date":"2022-07-19",
            "end_date":"2022-07-20",
        })

        response = self.client.get(BASE_URL)
        self.assertEqual(len(response.get_json()), 1)

        response = self.client.get(BASE_URL, query_string={
            "name":"b",
        })
        self.assertEqual(len(response.get_json()), 0)

        response = self.client.get(BASE_URL, query_string={
            "type":"X",
        })
        self.assertEqual(len(response.get_json()), 0)

        response = self.client.get(BASE_URL, query_string={
            "discount":"1",
        })
        self.assertEqual(len(response.get_json()), 0)

        response = self.client.get(BASE_URL, query_string={
            "customer":"20",
        })
        self.assertEqual(len(response.get_json()), 0)

        response = self.client.get(BASE_URL, query_string={
            "start_date":"2022-07-01",
        })
        self.assertEqual(len(response.get_json()), 0)

        response = self.client.get(BASE_URL, query_string={
            "end_date":"2022-07-01",
        })
        self.assertEqual(len(response.get_json()), 0)

    def test_query_promotion_unsupported_condition(self):
        """ It should not fetch a promotion by unsupported query conditions"""
        test_promo = PromoFactory()
        logging.debug("Test Promotion: %s", test_promo.serialize())
        response = self.client.post(
            BASE_URL,
            json=test_promo.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(BASE_URL, query_string={
            "unsupported_key":"123"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  