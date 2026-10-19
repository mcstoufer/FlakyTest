# flaky-test

Evaluate flaky test histories using bigram entropy. Requires Python 3.10 or later.

Licensed under the [GNU General Public License v3.0 only](LICENSE)
(`SPDX-License-Identifier: GPL-3.0-only`).

## Installation

From a local checkout:

```sh
pip install .
```

From GitHub:

```sh
pip install "flaky-test @ git+https://github.com/mcstoufer/FlakyTest.git"
```

From a package index after publishing the distribution:

```sh
pip install --index-url https://packages.example.com/simple/ flaky-test
```

To build wheel and source distributions for upload to PyPI or a private index:

```sh
pip install build twine
python -m build
python -m twine upload --repository-url https://packages.example.com/ dist/*
```

## Usage

```python
from flaky_test import FlakyTest, TestResult

# '0' represents passing test, '1' for failure.
results = TestResult("00010101010110")

FlakyTest().evaluate([results])

# If you want to measure more than the default 14 past results, just pass in a new 'window'
# value. FYI, values less than 12 do not generate useful measurements.
FlakyTest(window=18).evaluate([results])

results.add_test_result(0)  # 0 = pass, 1 = failure
```

`FlakyTest` and `TestResult` are the supported public API. Modules beginning
with `_` are internal implementation details. Earlier top-level imports should
be replaced with `from flaky_test import FlakyTest, TestResult`.
