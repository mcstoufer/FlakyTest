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

"""Public API for evaluating flaky test histories."""

from ._flaky_test import FlakyTest
from ._test_result import TestResult

__all__ = ["FlakyTest", "TestResult"]
