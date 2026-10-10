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
    """
    Base Data Model class used to associate the Test Result with the logic required to derive its confidence value.
    """
    _window = 0
    _all_permutations = []

    TRANS_TABLE = str.maketrans({"1": "0", "0": "1"})
    """
    Helper translation utility to allow a given test result sequence to be inverted. This is useful when
    doing initial formulary calculations as inverted patterns have the same occurrence count.
    """

    def __init__(self, window = 14):
        """
        Initialize the permutation engine with initial space
        :param window:
        :type window:
        """
        self._window = window
        self._all_permutations = [0] * (window+1)

    def generate_all(self):
        """
        Generate all formulary table entries given the provided `window` size.

        Only 1/2 of the table is generated. All the mirror entries in tables have the same count and just have their
        pass/fail pattern inverted. Write out the table once generated in memory.

        :return: Nothing is returned
        :rtype: None
        """
        for passing in range(0, ceil((self._window+1) / 2.0)):
            failing = self._window - passing
            permutations = self._generate_pass_fail_permutations(passing, failing)
            self._update_formularies(passing, permutations)
            self._update_formularies(self._window - passing,
                                     list(map(lambda x: x.translate(Permutations.TRANS_TABLE), permutations)))
        self.write()

    def find_confidence(self, test_result: TestResult, deviation_bound: float):
        """
        Perform the statistical analysis of a given test result and the sigma deviation value to bound against.
        :param test_result:
        :type test_result:
        :param deviation_bound:
        :type deviation_bound:
        :return: The final confidence value or '0' if the test result value fell outside the deviation bounding.
        :rtype: float
        """
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
        """
        Recursively generate all the possible pass/fail patterns of a given window size.

         This is a depth-first approach that completely builds up each combination in one depth-pass.

        :param r: The `pass` count. Initial invocation provides the right value.
        :type r: int
        :param b: The `fail` count. Initial invocation provides the right value. The sum of this and the `r` value must
         equal the window size.
        :type b: int
        :param current_sequence: The sequence of pass/fail permutations that is being built up before being stored
         in the all_sequences object.
        :type current_sequence: str
        :param all_sequences: The accumulating list of all sequences for a given `r` and `b` values.
        :type all_sequences: list[str]
        :return: A partial or complete list of all calculated sequences. This is ultimately the value we use for lookups.
        :rtype: list[str]
        """
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
        """
        A convenience method to abstract out the storage of a list of permutations in into the final list for reference.

        :param index: The index of the backing store array to update with. We assume that the array has already been
         initialized to the proper size and this slot exists with an "empty" value.
        :type index: int
        :param permutations: The calculated list of permutations to save.
        :type permutations: list[str]
        :return: Nothing is returned from this method.
        :rtype: None
        """
        self._all_permutations[index] = permutations

    def write(self):
        """
        Write out the generated formulary tables to a temp file. This is so future uses don't need to keep
        recalculating the same values again.

        Checks will need to be added to see if the prior written JSON is of the same size. If not, a new table
        will need to be generated and saved.
        :return: No value is returned from the write.
        :rtype: None
        """
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as tmp_file:
            print(f"Formularies file created at: {tmp_file.name}")
            json.dump(self._all_permutations, tmp_file)

if __name__ == '__main__':
    permutate = Permutations()
    permutate.generate_all()
