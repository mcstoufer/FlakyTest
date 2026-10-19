# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of flaky-test.
#
# flaky-test is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# flaky-test is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with flaky-test. If not, see <https://www.gnu.org/licenses/>.

import unittest

import flaky_test
from flaky_test import FlakyTest, TestResult


class PublicAPITest(unittest.TestCase):
    def test_exports(self):
        self.assertEqual(flaky_test.__all__, ["FlakyTest", "TestResult"])
        for name in ("Permutations", "Result", "test_result_entropy"):
            self.assertFalse(hasattr(flaky_test, name))
        self.assertEqual(FlakyTest(test_count=11)._test_count, 11)

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
