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

"""Unit tests with simple mocked values for review and refinement."""

import pytest

from flaky_test import _test_result as module
from flaky_test._test_result import TestResult as ResultHistory


@pytest.mark.parametrize("history", ["", "01", "0011"])
def test_init(history):
    result = ResultHistory(history)

    assert result.test_results == list(history)
    assert result.entropy == -1


def test_init_keeps_histories_independent():
    first = ResultHistory("0")
    second = ResultHistory("0")
    first.test_results.append("1")

    assert second.test_results == ["0"]


@pytest.mark.parametrize("value,expected", [(0, "0"), (1, "1"), ("0", "0"), ("1", "1")])
def test_add_test_result(value, expected):
    result = ResultHistory("01")
    result.entropy = 0.0

    assert result.add_test_result(value) is None

    assert result.test_results == ["0", "1", expected]
    assert result.entropy == -1


@pytest.mark.parametrize("value", [module._Result.PASS, module._Result.FAIL])
def test_add_test_result_enum(mocker, value):
    as_str = mocker.patch.object(module._Result, "as_str", return_value="0")
    result = ResultHistory("")

    result.add_test_result(value)

    assert result.test_results == ["0"]
    as_str.assert_called_once_with()


@pytest.mark.parametrize("value", [2, -1, "invalid", "", None])
def test_add_test_result_rejects_invalid_values(value):
    result = ResultHistory("01")
    result.entropy = 0.0

    with pytest.raises(ValueError, match="Test results must be 0 .* or 1"):
        result.add_test_result(value)

    assert result.test_results == ["0", "1"]
    assert result.entropy == 0.0


def test_fail_pct(mocker):
    result = ResultHistory("01")
    count = mocker.patch.object(result, "fail_count", return_value=0)

    assert result.fail_pct() == 0.0

    count.assert_called_once_with()


def test_fail_pct_empty_history(mocker):
    result = ResultHistory("")
    mocker.patch.object(result, "fail_count", return_value=0)

    with pytest.raises(ZeroDivisionError):
        result.fail_pct()


@pytest.mark.parametrize("history,expected", [("", 0), ("000", 0), ("101", 2), ("111", 3)])
def test_fail_count(history, expected):
    assert ResultHistory(history).fail_count() == expected


@pytest.mark.parametrize("length,expected", [(2, ["1", "1"]), (4, ["0", "0", "1", "1"]), (5, ["0", "0", "1", "1"])])
def test_truncate_to_length(length, expected):
    result = ResultHistory("0011")

    assert result.truncate_to_length(length) is None

    assert result.test_results == expected


def test_bigram_entropy_calculates_and_caches(mocker):
    entropy = mocker.patch.object(module, "test_result_entropy", return_value=0.0)
    result = ResultHistory("01")

    assert result.bigram_entropy() == 0.0
    assert result.entropy == 0.0
    assert result.bigram_entropy() == 0.0

    entropy.assert_called_once_with("01")


def test_bigram_entropy_uses_existing_cache(mocker):
    entropy = mocker.patch.object(module, "test_result_entropy", return_value=0.0)
    result = ResultHistory("01")
    result.entropy = 1.0

    assert result.bigram_entropy() == 1.0

    entropy.assert_not_called()


@pytest.mark.parametrize("history,expected", [("", 0), ("01", 2)])
def test_len(history, expected):
    assert len(ResultHistory(history)) == expected


@pytest.mark.parametrize("history", ["", "01", "0011"])
def test_str(history):
    assert str(ResultHistory(history)) == history


def test_repr(mocker):
    as_str = mocker.patch.object(ResultHistory, "__str__", return_value="01")

    assert repr(ResultHistory("")) == "01"

    as_str.assert_called_once_with()
