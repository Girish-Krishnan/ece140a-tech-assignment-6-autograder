import unittest
import requests
from datetime import datetime
from gradescope_utils.autograder_utils.decorators import weight, number


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up test case"""
        self.base_url = "http://localhost:6543"
        self.steps = []

    def tearDown(self):
        """Clean up after test"""
        self.steps = []

    @weight(0)
    @number("[TA5] - 1.1")
    def test_01_sensor_counts(self):
        """Test getting counts for all sensor types"""
        try:
            self.steps.append("Checking temperature sensor count")
            response = requests.get(f"{self.base_url}/api/temperature/count")
            self.assertEqual(
                response.status_code,
                200,
                msg="Temperature endpoint should return 200 status code",
            )
            self.assertEqual(
                response.json(), 2016, msg="Temperature count should be 2016"
            )

            self.steps.append("Checking humidity sensor count")
            response = requests.get(f"{self.base_url}/api/humidity/count")
            self.assertEqual(
                response.status_code,
                200,
                msg="Humidity endpoint should return 200 status code",
            )
            self.assertEqual(response.json(), 2016, msg="Humidity count should be 2016")

            self.steps.append("Checking light sensor count")
            response = requests.get(f"{self.base_url}/api/light/count")
            self.assertEqual(
                response.status_code,
                200,
                msg="Light endpoint should return 200 status code",
            )
            self.assertEqual(response.json(), 2016, msg="Light count should be 2016")
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.2")
    def test_02_invalid_sensor_type(self):
        """Test invalid sensor type returns 404"""
        try:
            self.steps.append("Checking invalid sensor type")
            response = requests.get(f"{self.base_url}/api/ERROR_TYPE/count")
            self.assertEqual(
                response.status_code,
                404,
                msg="Invalid sensor type should return 404 status code",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.3")
    def test_03_post_and_get(self):
        """Test posting new data and retrieving it"""
        try:
            self.steps.append("Posting new temperature data")
            data = {"value": 25.5, "unit": "C", "timestamp": "2024-02-04 12:00:00"}
            response = requests.post(f"{self.base_url}/api/temperature", json=data)
            self.assertEqual(
                response.status_code,
                200,
                msg="POST request should return 200 status code",
            )
            new_id = response.json()["id"]

            self.steps.append("Getting posted temperature data")
            response = requests.get(f"{self.base_url}/api/temperature/{new_id}")
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request should return 200 status code",
            )
            self.assertEqual(
                response.json()["value"],
                25.5,
                msg="Retrieved value should match posted value",
            )
            self.assertEqual(
                response.json()["unit"],
                "C",
                msg="Retrieved unit should match posted unit",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.4")
    def test_04_post_put_get(self):
        """Test posting, updating, and retrieving data"""
        try:
            self.steps.append("Posting initial temperature data")
            data = {"value": 25.5, "unit": "C", "timestamp": "2024-02-04 12:00:00"}
            response = requests.post(f"{self.base_url}/api/temperature", json=data)
            new_id = response.json()["id"]

            self.steps.append("Updating posted temperature data")
            update_data = {"value": 26.5, "unit": "F"}
            response = requests.put(
                f"{self.base_url}/api/temperature/{new_id}", json=update_data
            )
            self.assertEqual(
                response.status_code,
                200,
                msg="PUT request should return 200 status code",
            )

            self.steps.append("Getting updated temperature data")
            response = requests.get(f"{self.base_url}/api/temperature/{new_id}")
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request should return 200 status code",
            )
            self.assertEqual(
                response.json()["value"],
                26.5,
                msg="Retrieved value should match updated value",
            )
            self.assertEqual(
                response.json()["unit"],
                "F",
                msg="Retrieved unit should match updated unit",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.5")
    def test_05_post_get_delete_get(self):
        """Test posting without timestamp, getting, deleting, and getting again"""
        try:
            self.steps.append("Posting temperature data without timestamp")
            data = {"value": 25.5, "unit": "C"}
            response = requests.post(f"{self.base_url}/api/temperature", json=data)
            new_id = response.json()["id"]

            self.steps.append(
                "Getting posted temperature data to check default timestamp"
            )
            response = requests.get(f"{self.base_url}/api/temperature/{new_id}")
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request should return 200 status code",
            )
            self.assertIsNotNone(
                response.json()["timestamp"], msg="Default timestamp should be set"
            )

            self.steps.append("Deleting temperature data")
            response = requests.delete(f"{self.base_url}/api/temperature/{new_id}")
            self.assertEqual(
                response.status_code,
                200,
                msg="DELETE request should return 200 status code",
            )

            self.steps.append("Getting deleted temperature data")
            response = requests.get(f"{self.base_url}/api/temperature/{new_id}")
            self.assertEqual(
                response.status_code,
                404,
                msg="GET request for deleted data should return 404",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.6")
    def test_06_order_by_value(self):
        """Test ordering by value"""
        try:
            self.steps.append("Getting temperature data ordered by value")
            response = requests.get(f"{self.base_url}/api/temperature?order-by=value")
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request with order-by should return 200 status code",
            )
            data = response.json()

            self.steps.append("Verifying data is ordered by value")
            values = [record["value"] for record in data]
            self.assertEqual(
                values,
                sorted(values),
                msg="Data should be sorted by value in ascending order",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.7")
    def test_07_order_by_timestamp(self):
        """Test ordering by timestamp"""
        try:
            self.steps.append("Getting temperature data ordered by timestamp")
            response = requests.get(
                f"{self.base_url}/api/temperature?order-by=timestamp"
            )
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request with order-by timestamp should return 200 status code",
            )
            data = response.json()

            self.steps.append("Verifying data is ordered by timestamp")
            timestamps = [record["timestamp"] for record in data]
            self.assertEqual(
                timestamps,
                sorted(timestamps),
                msg="Data should be sorted by timestamp in ascending order",
            )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

    @weight(0)
    @number("[TA5] - 1.8")
    def test_08_date_range(self):
        """Test date range filtering"""
        try:
            self.steps.append("Getting temperature data within date range")
            response = requests.get(
                f"{self.base_url}/api/temperature?"
                "start-date=2024-01-01 00:00:00&"
                "end-date=2024-01-01 00:40:00"
            )
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request with date range should return 200 status code",
            )
            data = response.json()

            self.steps.append("Verifying number of records in date range")
            self.assertEqual(
                len(data),
                9,
                msg="Should return exactly 9 records within the specified date range\nstart-date=2024-01-01 00:00:00&\nend-date=2024-01-01 00:40:00",
            )

            self.steps.append("Verifying all records are within date range")
            start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime("2024-01-01 00:40:00", "%Y-%m-%d %H:%M:%S")

            for record in data:
                record_date = datetime.strptime(
                    record["timestamp"], "%Y-%m-%d %H:%M:%S"
                )
                self.assertTrue(
                    start_date <= record_date <= end_date,
                    msg=f"Record timestamp {record_date} should be within range",
                )
        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e
