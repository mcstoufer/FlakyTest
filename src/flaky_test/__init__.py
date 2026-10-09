"""Public API for evaluating flaky test histories."""

from ._flaky_test import FlakyTest
from ._test_result import TestResult

__all__ = ["FlakyTest", "TestResult"]
