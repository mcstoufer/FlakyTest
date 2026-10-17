# This is a sample Python script.
import json
import sys

import numpy as np
import os
import tempfile
from math import ceil, floor

from ._test_result import TestResult

class Permutations:
    """
    Base Data Model class used to associate the Test Result with the logic required to derive its confidence value.
    """
    _window = 0
    _all_permutations: list[list[str] | None] = []

    DOTFILE_PATH = os.path.expanduser("~/.flaky_formulary.json")
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
        self.load(window)

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

    @staticmethod
    def calculate_weight(index: int, length: int, spread: float, beta=4.0):
        midpoint = (length - 1) / 2
        # Raising to beta instead of 2 widens the shoulders of the weights themselves
        exponent = np.power(np.abs(index - midpoint), beta) / spread
        weight = 100 * np.exp(-exponent)
        return weight

    @staticmethod
    def calculate_large_scale_confidence(all_weights, target_index):
        """
        Highly efficient confidence calculator for thousands of buckets.
        Simple radial basis profile.
        """
        return all_weights[target_index]

    def find_confidence(self, test_result: TestResult, beta=4.0):
        """
        Perform the statistical analysis of a given test result and the sigma deviation value to bound against.
        :param test_result:
        :type test_result:
        :param beta:
        :type beta: float
        :return: The final confidence value or '0' if the test result value fell outside the deviation bounding.
        :rtype: float
        """
        result_template: list[str] = self._all_permutations[test_result.fail_count()] # type: ignore
        length = len(result_template)
        spread = np.power((floor(length / 2) / 1.3), beta)

        result_index = result_template.index(str(test_result))
        all_weights = np.asarray([Permutations.calculate_weight(index, length, spread, beta) for index in range(length)])

        return Permutations.calculate_large_scale_confidence(all_weights, result_index)

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

    def load(self, window):
        try:
            with open(Permutations.DOTFILE_PATH, "r") as tmp_file:
                self._all_permutations = json.load(tmp_file)
                length = len(self._all_permutations)
                if length != window+1:
                    self._all_permutations = [None] * (window + 1)
                    print("Updating formulary file. This may take a few moments for large windows.", file=sys.stderr)
                    self.generate_all()
        except FileNotFoundError:
            self._all_permutations = [None] * (window + 1)
            print("Did not find formulary file. Will create now.", file=sys.stderr)
            self.generate_all()

    def write(self):
        """
        Write out the generated formulary tables to a temp file. This is so future uses don't need to keep
        recalculating the same values again.

        Checks will need to be added to see if the prior written JSON is of the same size. If not, a new table
        will need to be generated and saved.
        :return: No value is returned from the write.
        :rtype: None
        """
        with open(Permutations.DOTFILE_PATH, "w", encoding="utf-8") as tmp_file:
            print(f"Formularies file created at: {tmp_file.name}")
            json.dump(self._all_permutations, tmp_file)

if __name__ == '__main__':
    permutate = Permutations()
    permutate.generate_all()
