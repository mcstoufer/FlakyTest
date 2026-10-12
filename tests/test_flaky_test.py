"""Unit tests with simple mocked values for review and refinement."""

import pytest

from flaky_test import _flaky_test as module
from flaky_test._flaky_test import FlakyTest


@pytest.fixture
def engine(mocker):
    constructor = mocker.patch.object(module, "Permutations")
    constructor.return_value.generate_all.return_value = None
    constructor.return_value.find_confidence.return_value = 0.0
    return constructor


@pytest.fixture
def test_result(mocker):
    result = mocker.MagicMock(spec=module.TestResult)
    result.__len__.return_value = 14
    result.fail_pct.return_value = 0.5
    result.truncate_to_length.return_value = None
    return result


def test_init_defaults(engine):
    evaluator = FlakyTest()

    assert evaluator._pass_pct_lower == 0.10
    assert evaluator._pass_pct_upper == 0.85
    assert evaluator._deviation_bound == 4.0
    assert evaluator._test_count == 14
    assert evaluator._permutation_engine is engine.return_value
    engine.assert_called_once_with(window=14)


def test_init_custom_values(engine):
    evaluator = FlakyTest(0.2, 0.8, 2.0, 11)

    assert evaluator._pass_pct_lower == 0.2
    assert evaluator._pass_pct_upper == 0.8
    assert evaluator._deviation_bound == 2.0
    assert evaluator._test_count == 11
    engine.assert_called_once_with(window=11)


@pytest.mark.parametrize("test_count", [0, 9, 10])
def test_init_rejects_insufficient_window(engine, test_count):
    with pytest.raises(AssertionError, match="Test count not long enough"):
        FlakyTest(test_count=test_count)

    engine.assert_not_called()


def test_evaluate_empty_input(engine):
    assert FlakyTest().evaluate([]) == []

    engine.return_value.generate_all.assert_not_called()
    engine.return_value.find_confidence.assert_not_called()


@pytest.mark.parametrize("fail_pct", [0.10, 0.5, 0.85])
def test_evaluate_within_bounds(engine, test_result, fail_pct):
    test_result.fail_pct.return_value = fail_pct

    assert FlakyTest().evaluate([test_result]) == [(test_result, 0.0)]

    test_result.fail_pct.assert_called_once_with()
    test_result.truncate_to_length.assert_not_called()
    engine.return_value.generate_all.assert_called_once_with()
    engine.return_value.find_confidence.assert_called_once_with(test_result, beta=4.0)


def test_evaluate_truncates_long_history(engine, test_result):
    test_result.__len__.return_value = 15

    assert FlakyTest().evaluate([test_result]) == [(test_result, 0.0)]

    test_result.truncate_to_length.assert_called_once_with(14)
    engine.return_value.find_confidence.assert_called_once_with(test_result, beta=4.0)


@pytest.mark.parametrize("fail_pct", [0.0, 1.0])
def test_evaluate_outside_bounds(engine, test_result, capsys, fail_pct):
    test_result.fail_pct.return_value = fail_pct

    assert FlakyTest().evaluate([test_result]) == [(test_result, 0)]

    engine.return_value.generate_all.assert_not_called()
    engine.return_value.find_confidence.assert_not_called()
    assert capsys.readouterr().err == "Test result outside of statistical bounds.\n"


@pytest.mark.xfail(
    strict=True,
    reason="Short histories currently continue evaluation and produce two entries",
)
def test_evaluate_short_history_returns_one_zero(engine, test_result, capsys):
    test_result.__len__.return_value = 13

    results = FlakyTest().evaluate([test_result])

    assert "Insufficient data to run test" in capsys.readouterr().err
    assert results == [(test_result, 0)]
    engine.return_value.generate_all.assert_not_called()
    engine.return_value.find_confidence.assert_not_called()


def test_evaluate_multiple_results(engine, mocker, test_result):
    second = mocker.MagicMock(spec=module.TestResult)
    second.__len__.return_value = 14
    second.fail_pct.return_value = 0.5

    assert FlakyTest(deviation_bound=2.0).evaluate([test_result, second]) == [
        (test_result, 0.0), (second, 0.0)
    ]

    assert engine.return_value.generate_all.call_count == 2
    assert engine.return_value.find_confidence.call_args_list == [
        mocker.call(test_result, beta=2.0), mocker.call(second, beta=2.0)
    ]
