# flaky-test

Evaluate flaky test histories using bigram entropy. Requires Python 3.10 or later.

## Installation

From a local checkout:

```sh
pip install .
```

From GitHub (replace OWNER and REPOSITORY with your repository):

```sh
pip install "flaky-test @ git+https://github.com/OWNER/REPOSITORY.git"
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

The URLs above are placeholders. This project has not been published.

## Usage

```python
from flaky_test import FlakyTest, TestResult

results = TestResult("00010101010110")
FlakyTest().evaluate([results])
results.add_test_result(0)  # 0 = pass, 1 = failure
```

`FlakyTest` and `TestResult` are the supported public API. Modules beginning
with `_` are internal implementation details. Earlier top-level imports should
be replaced with `from flaky_test import FlakyTest, TestResult`.
