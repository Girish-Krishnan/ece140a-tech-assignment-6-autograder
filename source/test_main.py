import unittest
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.defaultTestLoader.discover(
        start_dir=".",  # Current directory
        pattern="test_*.py",  # Files starting with test_
    )
    with open("/autograder/results/results.json", "w") as f:
        JSONTestRunner(visibility="visible", stream=f).run(suite)
