import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight
import json


class TestStockForm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Playwright and browser instance before all tests."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch(headless=True)
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Navigate to the stock page before each test."""
        self.page.goto("http://localhost:6543/stock")

    @weight(3)
    def test_01_form_structure(self):
        """Test if form has correct structure with required labels and inputs"""
        # Check for form existence
        form = self.page.locator("form")
        self.assertTrue(form.is_visible(), "Form should be visible on the page")

        # Check for exactly 3 labels
        labels = self.page.locator("label")
        self.assertEqual(labels.count(), 3, "Form should have exactly 3 labels")

        submit_input = self.page.locator("input[type='submit']")
        self.assertTrue(
            submit_input.is_visible(), "Submit button should be visible on the page"
        )

        # Check for exactly 3 inputs with correct name attributes
        for i in range(1, 4):
            input_name = f"symbol{i}"
            input_element = self.page.locator(f"input[name='{input_name}']")
            self.assertEqual(
                input_element.count(),
                1,
                f"Should have exactly one input with name '{input_name}'",
            )

    @weight(4)
    def test_02_empty_form_validation(self):
        """Test that empty form cannot be submitted"""
        # Try to submit empty form
        submit_input = self.page.locator("input[type='submit']")
        submit_input.click()

        # Check if we're still on the same page (form didn't submit)
        self.assertEqual(
            self.page.url,
            "http://localhost:6543/stock",
            "Empty form should not be submitted",
        )

    @weight(4)
    def test_03_initial_stock_endpoints(self):
        """Test that stock endpoints return empty JSON initially"""

        def check_endpoint(number):
            response = self.page.request.get(f"http://localhost:6543/stock/{number}")
            self.assertEqual(response.status, 200)
            data = response.json()
            self.assertEqual(
                data, {}, f"Stock endpoint {number} should return empty JSON initially"
            )

        for i in range(1, 4):
            check_endpoint(i)

    @weight(5)
    def test_04_form_submission_redirect(self):
        """Test form submission and redirect"""
        # Fill out the form with stock symbols
        test_symbols = {"symbol1": "AAPL", "symbol2": "GOOGL", "symbol3": "MSFT"}

        for name, symbol in test_symbols.items():
            self.page.locator(f"input[name='{name}']").fill(symbol)

        # Submit form
        submit_input = self.page.locator("input[type='submit']")
        submit_input.click()

        # Check redirect
        self.assertEqual(
            self.page.url,
            "http://localhost:6543/stock/page",
            "Should redirect to /stock/page after submission",
        )

    @weight(5)
    def test_05_populated_stock_endpoints(self):
        """Test that stock endpoints return correct data structure after form submission"""
        # First submit form with test symbols
        test_symbols = {"symbol1": "AAPL", "symbol2": "GOOGL", "symbol3": "MSFT"}

        # Fill and submit form
        for name, symbol in test_symbols.items():
            self.page.locator(f"input[name='{name}']").fill(symbol)

        submit_input = self.page.locator("input[type='submit']")
        submit_input.click()

        # Now check each endpoint for correct data structure
        def verify_endpoint(number):
            response = self.page.request.get(f"http://localhost:6543/stock/{number}")
            self.assertEqual(response.status, 200)
            data = response.json()

            # Verify the response has all required fields
            required_fields = ["company name", "industry", "sector", "stock price"]
            for field in required_fields:
                self.assertIn(field, data, f"Response should contain {field}")
                self.assertIsNotNone(data[field], f"{field} should not be null")

        for i in range(1, 4):
            verify_endpoint(i)
