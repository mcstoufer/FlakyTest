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

from collections import Counter
import math

def test_result_entropy(text: str, overlapping: bool = True) -> float:
    """Calculates the Shannon entropy of 2-character sequences (bigrams) in a string."""
    step = 1 if overlapping else 2
    pairs = [text[i:i + 2] for i in range(0, len(text) - 1, step) if len(text[i:i + 2]) == 2]
    if not pairs:
        return 0.0

    counts = Counter(pairs)
    total = len(pairs)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())