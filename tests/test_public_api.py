import unittest

import flaky_test
from flaky_test import FlakyTest, TestResult


class PublicAPITest(unittest.TestCase):
    def test_exports(self):
        self.assertEqual(flaky_test.__all__, ["FlakyTest", "TestResult"])
        for name in ("Permutations", "Result", "test_result_entropy"):
            self.assertFalse(hasattr(flaky_test, name))
        self.assertEqual(FlakyTest(test_count=11).test_count, 11)

    def test_result_without_internal_enum(self):
        result = TestResult("01")
        result.bigram_entropy()
        result.add_test_result(1)
        result.add_test_result("0")
        self.assertEqual(str(result), "0110")
        self.assertEqual(result.fail_pct(), 0.5)
        self.assertGreater(result.bigram_entropy(), 0)
        with self.assertRaises(ValueError):
            result.add_test_result(2)
