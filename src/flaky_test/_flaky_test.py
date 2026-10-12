import sys

if __name__ == "__main__" and not __package__:
    from pathlib import Path

    # Resolve package-relative imports when this file is run directly.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "flaky_test"

from ._permutations import Permutations
from ._test_result import TestResult


class FlakyTest:
    """
    Main class to drive flaky test confidence measurements.

    Examples:
        >>> test_result = TestResult(test_results="00010101010110")
        >>> FlakyTest().evaluate(test_results=[demo_test_result])
     """

    MIN_TEST_COUNT = 10
    """
    The minimum window size to allow for flaky test measurements. Values below this do not generate statistically 
    relevant values.
    """

    _pass_pct_lower = 0.10
    _pass_pct_upper = 0.85
    _deviation_bound = 4.0
    _test_count = 14

    _permutation_engine: Permutations

    def __init__(self, lower_bound=.10,
                 upper_bound=.85,
                 deviation_bound=4.0,
                 test_count=14):
        """
        Base initializer for the Flaky Test measurements.

        :param lower_bound: The lower fail percentage to bound measurements to. Test results that have a lower
         fail percentage will not be measured. These tests are considered 'passing' even if there are a small
         amount of failures recorded.
        :type lower_bound: float
        :param upper_bound: The upper fail percentage to bound measurements to. Test results that have a higher
         fail percentage will not be measured. These tests are considered 'broken' even if there are a small
         amount of passes recorded.
        :type upper_bound: float
        :param deviation_bound: This is the statistical Beta value used in a simple radial basis profile calculation.
          If the σ value is too small, no confidence will be returned. If too high, confidence level will be too low to
          be useful. A value around 4.0 is appropriate.
        :type deviation_bound: float
        :param test_count: The size of the test result window to work with. If tests results are longer than this
         window, they are head truncated before measurements. If too small, no measurement is made.
        :type test_count: int

        :raises AssertionError: if the test_count value is < MIN_TEST_COUNT
        """
        self._pass_pct_lower = lower_bound
        self._pass_pct_upper = upper_bound
        self._deviation_bound = deviation_bound
        assert test_count > FlakyTest.MIN_TEST_COUNT, f"Test count not long enough. Must be at least {FlakyTest.MIN_TEST_COUNT}"
        self._test_count = test_count
        self._permutation_engine = Permutations(window=self._test_count)

    def evaluate(self, test_results: list[TestResult]):
        """
        Initiate an evaluation of a set of test results.

         Initial gate checking is done to ensure the test result is of the right length and within the pass fail percentage
         window.

        :param test_results: A list of test results objects. Each test result therein is a sequence of pass-fail results
         whose length is equal to the initial `test_count` value.
        :type test_results: TestResult
        :return: A collection of test results and their calculated flaky test confidence level.
        :rtype: A list of tuples of type (TestResult, float)
        """
        calculated_confidences: list[tuple[TestResult, float]] = []

        for test_result in test_results:
            if len(test_result) > self._test_count:
                test_result.truncate_to_length(self._test_count)
            elif len(test_result) < self._test_count:
                print(f"Insufficient data to run test. Adjust 'test_count' to match the length: {len(test_result)}",
                      file=sys.stderr)
                calculated_confidences.append((test_result, 0))

            fail_pct = test_result.fail_pct()
            if self._pass_pct_lower <= fail_pct <= self._pass_pct_upper:
                self._permutation_engine.generate_all()
                calculated_confidence = self._permutation_engine.find_confidence(test_result, beta=self._deviation_bound)
                calculated_confidences.append((test_result, calculated_confidence))
            else:
                print("Test result outside of statistical bounds.", file=sys.stderr)
                calculated_confidences.append((test_result, 0))
        return calculated_confidences


def main():
    """Run the standalone flaky test demonstration."""
    demo_test_result = [TestResult(test_results="00010101010110")]
    confidences = FlakyTest().evaluate(test_results=demo_test_result)
    for confidence in confidences:
        print(f"Flaky Test confidence '{confidence[0]}': {confidence[1]:.2f}%")


if __name__ == '__main__':
    main()
