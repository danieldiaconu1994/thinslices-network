import unittest
import json
from app import app


class ThinsliceNetwork(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client

    def test_get_all_work_orders(self):
        response = self.client().get("/work_orders")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_work_order_by_id(self):
        response = self.client().post("/work_order/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), dict)

    def test_get_all_customers(self):
        response = self.client().get("/customers")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_customer_by_id(self):
        response = self.client().post("/customer/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), dict)

    def test_create_work_order(self):
        payload = {"work_order_type": "install",
                   "schedule": "10.02.2023",
                   "customer_id": "1"}
        response = self.client().post(
            "/add/work_order", data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), dict)

    def test_create_customer(self):
        payload = {
               "first_name": "Test",
               "last_name": "Testescu",
               "address": "str. Testelor, nr. 13, Mirau, Giurgiu, Romania",
               "email_address": "test@test.test",
               "phone_number": "0756742921",
         }
        response = self.client().post(
            "/add/customer", data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), dict)


if __name__ == '__main__':
    unittest.main()
