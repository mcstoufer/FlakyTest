from enum import Enum
from ._utilities import test_result_entropy

class _Result(Enum):
    PASS = 0
    FAIL = 1

    def as_str(self):
        return "0" if self == _Result.PASS else "1"

class TestResult:
    test_results: list[str] = []
    entropy: float = -1

    def __init__(self, test_results: str):
        self.test_results = list(test_results)

    def add_test_result(self, result: str | int | _Result):
        """Append 0 for a pass or 1 for a failure."""
        value = result.as_str() if isinstance(result, _Result) else str(result)
        if value not in ("0", "1"):
            raise ValueError("Test results must be 0 (pass) or 1 (failure)")
        self.test_results.append(value)
        self.entropy = -1

    def fail_pct(self):
        return self.fail_count() / len(self.test_results)

    def fail_count(self):
        return len(list(filter(lambda x: x == "1", self.test_results)))

    def truncate_to_length(self, length: int):
        self.test_results = self.test_results[-length:]

    def bigram_entropy(self) -> float:
        if self.entropy < 0:
            self.entropy = test_result_entropy(str(self))
        return self.entropy

    def __len__(self):
        return len(self.test_results)

    def __str__(self):
        return "".join(self.test_results)

    def __repr__(self) -> str:
        return str(self)
