import sys
from ._permutations import Permutations
from ._test_result import TestResult

class FlakyTest:
    MIN_TEST_COUNT = 10

    pass_pct_lower = 0
    pass_pct_upper = 1.0
    deviation_bound = 1.0
    test_count = 14

    permutation_engine: Permutations

    def __init__(self, lower_bound = .10,
                 upper_bound = .85,
                 deviation_bound = 1.5,
                 test_count = 14):
        self.pass_pct_lower = lower_bound
        self.pass_pct_upper = upper_bound
        self.deviation_bound = deviation_bound
        assert test_count> FlakyTest.MIN_TEST_COUNT, f"Test count not long enough. Must be at least {FlakyTest.MIN_TEST_COUNT}"
        self.test_count = test_count
        self.permutation_engine = Permutations(window=self.test_count)

    def evaluate(self, test_results: list[TestResult]):
        for test_result in test_results:
            if len(test_result) > self.test_count:
                test_result.truncate_to_length(self.test_count)
            elif len(test_result) < self.test_count:
                print(f"Insufficient data to run test. Adjust 'test_count' to match the length: {len(test_result)}", file=sys.stderr)
                return

            fail_pct = test_result.fail_pct()
            confidence = 0
            if self.pass_pct_lower <= fail_pct <= self.pass_pct_upper:
                self.permutation_engine.generate_all()
                confidence = self.permutation_engine.find_confidence(test_result, self.deviation_bound)
            else:
                print("Test result outside of statistical bounds.", file=sys.stderr)
            print(f"Flaky Test confidence '{test_results}': {confidence:.2f}%")

if __name__ == '__main__':
    demo_test_result = TestResult(test_results="00010101010110")
    FlakyTest().evaluate(test_results=[demo_test_result])
