"""Unit tests with simple mocked values for review and refinement."""

import pytest

from flaky_test import _permutations as module
from flaky_test._permutations import Permutations


@pytest.mark.parametrize("window", [0, 2, 14])
def test_init(window):
    permutations = Permutations(window=window)

    assert permutations._window == window
    assert permutations._all_permutations == [None] * (window + 1)


def test_init_default_window():
    permutations = Permutations()

    assert permutations._window == 14
    assert permutations._all_permutations == [None] * 15


@pytest.mark.parametrize("window", [2, 3])
def test_generate_all(mocker, window):
    permutations = Permutations(window=window)
    generate = mocker.patch.object(
        permutations, "_generate_pass_fail_permutations", return_value=["01"]
    )
    update = mocker.patch.object(permutations, "_update_formularies", return_value=None)
    write = mocker.patch.object(permutations, "write", return_value=None)

    assert permutations.generate_all() is None

    generate.assert_has_calls([mocker.call(0, window), mocker.call(1, window - 1)])
    assert generate.call_count == 2
    assert update.call_args_list == [
        mocker.call(0, ["01"]),
        mocker.call(window, ["10"]),
        mocker.call(1, ["01"]),
        mocker.call(window - 1, ["10"]),
    ]
    write.assert_called_once_with()


@pytest.mark.parametrize("beta", [None, 2.0])
def test_calculate_weight(mocker, beta):
    absolute = mocker.patch.object(module.np, "abs", return_value=1.0)
    power = mocker.patch.object(module.np, "power", return_value=1.0)
    exponential = mocker.patch.object(module.np, "exp", return_value=1.0)
    kwargs = {} if beta is None else {"beta": beta}

    assert Permutations.calculate_weight(0, 3, 2.0, **kwargs) == 100.0

    absolute.assert_called_once_with(-1.0)
    power.assert_called_once_with(1.0, 4.0 if beta is None else beta)
    exponential.assert_called_once_with(-0.5)


def test_calculate_large_scale_confidence(mocker):
    weights = mocker.MagicMock()
    weights.__getitem__.return_value = 0.0

    assert Permutations.calculate_large_scale_confidence(weights, 1) == 0.0

    weights.__getitem__.assert_called_once_with(1)


@pytest.mark.parametrize("beta", [None, 2.0])
def test_find_confidence(mocker, beta):
    permutations = Permutations(window=2)
    permutations._all_permutations[1] = ["10", "01"]
    test_result = mocker.MagicMock(spec=module.TestResult)
    test_result.fail_count.return_value = 1
    test_result.__str__.return_value = "01"
    power = mocker.patch.object(module.np, "power", return_value=1.0)
    weight = mocker.patch.object(Permutations, "calculate_weight", return_value=0.0)
    asarray = mocker.patch.object(module.np, "asarray", return_value=[0.0, 0.0])
    confidence = mocker.patch.object(
        Permutations, "calculate_large_scale_confidence", return_value=0.0
    )
    kwargs = {} if beta is None else {"beta": beta}
    expected_beta = 4.0 if beta is None else beta

    assert permutations.find_confidence(test_result, **kwargs) == 0.0

    test_result.fail_count.assert_called_once_with()
    power.assert_called_once_with(1 / 1.3, expected_beta)
    assert weight.call_args_list == [
        mocker.call(0, 2, 1.0, expected_beta),
        mocker.call(1, 2, 1.0, expected_beta),
    ]
    asarray.assert_called_once_with([0.0, 0.0])
    confidence.assert_called_once_with([0.0, 0.0], 1)


def test_generate_pass_fail_permutations_base_case():
    permutations = Permutations(window=0)

    assert permutations._generate_pass_fail_permutations(0, 0) == [""]


def test_generate_pass_fail_permutations_existing_accumulator():
    permutations = Permutations(window=2)
    sequences = ["10"]

    result = permutations._generate_pass_fail_permutations(0, 0, "01", sequences)

    assert result is sequences
    assert sequences == ["10", "01"]


@pytest.mark.parametrize(
    "passing,failing,expected_branches",
    [
        (1, 0, [(0, 0, "1")]),
        (0, 1, [(0, 0, "0")]),
        (1, 1, [(0, 1, "1"), (1, 0, "0")]),
    ],
)
def test_generate_pass_fail_permutations_recursive_calls(
    mocker, passing, failing, expected_branches
):
    permutations = Permutations(window=passing + failing)
    # Keep the actual method under test; replace only its recursive calls.
    generate = permutations._generate_pass_fail_permutations
    recurse = mocker.patch.object(
        permutations, "_generate_pass_fail_permutations", return_value=[]
    )
    sequences = []

    assert generate(passing, failing, all_sequences=sequences) is sequences

    assert recurse.call_args_list == [
        mocker.call(r, b, sequence, sequences)
        for r, b, sequence in expected_branches
    ]


def test_update_formularies():
    permutations = Permutations(window=2)
    sequences = ["01"]

    assert permutations._update_formularies(1, sequences) is None

    assert permutations._all_permutations == [None, ["01"], None]
    assert permutations._all_permutations[1] is sequences


def test_write(mocker, capsys):
    permutations = Permutations(window=2)
    temporary_file = mocker.MagicMock()
    temporary_file.name = "placeholder.json"
    context = mocker.MagicMock()
    context.__enter__.return_value = temporary_file
    create_file = mocker.patch.object(
        module.tempfile, "NamedTemporaryFile", return_value=context
    )
    dump = mocker.patch.object(module.json, "dump", return_value=None)

    assert permutations.write() is None

    create_file.assert_called_once_with(
        mode="w+", suffix=".json", delete=False, encoding="utf-8"
    )
    dump.assert_called_once_with(permutations._all_permutations, temporary_file)
    context.__exit__.assert_called_once_with(None, None, None)
    assert capsys.readouterr().out == "Formularies file created at: placeholder.json\n"
