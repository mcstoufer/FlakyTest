# This is a sample Python script.
import itertools
import bisect
import json
import tempfile
from math import ceil, floor
import statistics

from ._test_result import TestResult
from ._utilities import test_result_entropy

class Permutations:
    _window = 0
    _all_permutations = []

    TRANS_TABLE = str.maketrans({"1": "0", "0": "1"})

    def __init__(self, window = 14):
        self._window = window
        self._all_permutations = [0] * (window+1)

    def generate_all(self):

        for passing in range(0, ceil((self._window+1) / 2.0)):
            failing = self._window - passing
            permutations = self._generate_pass_fail_permutations(passing, failing)
            self._update_formularies(passing, permutations)
            self._update_formularies(self._window - passing,
                                     list(map(lambda x: x.translate(Permutations.TRANS_TABLE), permutations)))
        self.write()

    def find_confidence(self, test_result: TestResult, deviation_bound: float):
        result_template = self._all_permutations[test_result.fail_count()]
        weights = list(map(lambda x: test_result_entropy(x), result_template))
        result_dict = dict(zip(result_template, weights))

        mu = statistics.fmean(weights)
        sigma = statistics.pstdev(weights)

        lower_bound = mu - (deviation_bound * sigma)
        upper_bound = mu + (deviation_bound * sigma)

        ordered_result_dict = dict()
        for key, value in result_dict.items():
            ordered_result_dict.setdefault(value, list()).append(key)

        indexes = list(filter(lambda x: lower_bound <= x <= upper_bound, ordered_result_dict.keys()))
        new_dict = { k: ordered_result_dict[k] for k in indexes if k in ordered_result_dict }

        if test_result.bigram_entropy() in new_dict:
            bucket_entropy = test_result.bigram_entropy()
            max_entropy = max(new_dict.keys())
            return bucket_entropy / max_entropy
        else:
            return 0.0

    def _generate_pass_fail_permutations(self, r, b, current_sequence="", all_sequences=None):
        if all_sequences is None:
            all_sequences = []

        # Base case: if no balls are left, a valid permutation is complete
        if r == 0 and b == 0:
            all_sequences.append(current_sequence)
            return all_sequences

        # Branch 1: Pick a Red ball if available
        if r > 0:
            self._generate_pass_fail_permutations(r - 1, b, current_sequence + "1", all_sequences)

        # Branch 2: Pick a Black ball if available
        if b > 0:
            self._generate_pass_fail_permutations(r, b - 1, current_sequence + "0", all_sequences)

        return all_sequences

    def _update_formularies(self, index, permutations):
        self._all_permutations[index] = permutations

    def write(self):
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as tmp_file:
            print(f"Formularies file created at: {tmp_file.name}")
            json.dump(self._all_permutations, tmp_file)

if __name__ == '__main__':
    permutate = Permutations()
    permutate.generate_all()
