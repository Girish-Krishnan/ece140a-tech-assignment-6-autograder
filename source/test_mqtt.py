import unittest
import requests
from datetime import datetime
import paho.mqtt.client as mqtt
from gradescope_utils.autograder_utils.decorators import weight, number
import os
import time
import random

BROKER = "broker.hivemq.com"
PORT = 1883

class TestMQTT(unittest.TestCase):
    def setUp(self):
        """Set up test case"""
        self.base_url = "http://localhost:6543"
        self.steps = []
        self.base_topic = os.getenv("BASE_TOPIC")
        self.topic = f"{self.base_topic}/readings"

    def tearDown(self):
        """Clean up after test"""
        self.steps = []


    @weight(50)
    @number("[TA6] - 1.1")
    def test_mqtt_to_webserver(self):
        """Can you receive messages from MQTT and send it to the webserver via POST request?"""
        try:
            # Send a message to the MQTT broker
            temperature = random.randint(10, 40)
            pressure = random.randint(900, 1100)
            message = "{\"temperature\": %d, \"pressure\": %d}" % (temperature, pressure)
            self.steps.append(f"Sending message to MQTT broker: {message}")
            client = mqtt.Client()
            client.connect(BROKER, PORT)
            # Publish for 6 seconds
            last_publish = datetime.now()
            while (datetime.now() - last_publish).seconds < 20:
                client.publish(self.topic, message)
                time.sleep(0.01)

            client.disconnect()

            # Check if the webserver received the message
            self.steps.append("Checking if the webserver received the message")

            # Make a get request to the webserver
            response = requests.get(
                f"{self.base_url}/api/temperature?order-by=timestamp"
            )
            self.assertEqual(
                response.status_code,
                200,
                msg="GET request with order-by timestamp should return 200 (success) status code. Does your Tech Assignment 5 code work correctly?",
            )

            data = response.json()
            timestamps = [record["timestamp"] for record in data]
            
            # Check if the most recent timestamp is in 2025, february
            self.steps.append("Checking if the most recent timestamp is in 2025, February. Your most recent timestamp is: " + timestamps[-1])
            self.assertTrue(
                timestamps[-1].startswith("2025-02"),
                msg="The most recent timestamp should be in 2025, February (the current month). Make sure the timestamp is formatted as 'YYYY-MM-DD HH:MM:SS'.",
            )

            # Check if the most recent temperature is the same as the one sent to the MQTT broker
            self.steps.append("Checking if the most recent temperature is the same as the one sent to the MQTT broker")
            self.assertEqual(
                data[-1]["value"],
                temperature,
                msg="The most recent temperature should be the same as the one sent to the MQTT broker. Make sure the temperature value is stored in the 'value' field.",
            )

        except Exception as e:
            raise Exception(
                f"Failed at steps: {' -> '.join(self.steps)}\nError: {str(e)}"
            ) from e

            