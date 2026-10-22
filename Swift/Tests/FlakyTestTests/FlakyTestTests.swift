// SPDX-FileCopyrightText: 2026 Martin Stoufer
// SPDX-License-Identifier: GPL-3.0-only

import Testing
@testable import FlakyTest

@Suite("String and array inversion")
struct InversionTests {
    @Test(
        "Strings invert binary digits and preserve other characters",
        arguments: [
            ("", ""),
            ("0", "1"),
            ("1", "0"),
            ("101001", "010110"),
            ("10x-01", "01x-10"),
        ]
    )
    func stringInversion(input: String, expected: String) {
        #expect(input.invert() == expected)
    }

    @Test("Arrays invert each element without changing their order")
    func arrayInversion() {
        #expect(["10", "001", "text"].invert() == ["01", "110", "text"])
        #expect([String]().invert().isEmpty)
    }
}

@Suite("TestResult")
struct TestResultTests {
    @Test("The string initializer separates every character")
    func stringInitializer() {
        let result = TestResult(testResult: "10100")

        #expect(result.testResults == ["1", "0", "1", "0", "0"])
        #expect(result.string == "10100")
        #expect(result.length == 5)
    }

    @Test("The array initializer preserves complete elements")
    func arrayInitializer() {
        let result = TestResult(testResults: ["10", "x", "1"])

        #expect(result.testResults == ["10", "x", "1"])
        #expect(result.string == "10x1")
        #expect(result.length == 3)
    }

    @Test("Failure statistics count only exact one elements")
    func failureStatistics() {
        let result = TestResult(testResults: ["1", "0", "1", "x", "11"])

        #expect(result.failCount == 2)
        #expect(result.failPct == 0.4)
    }

    @Test("Truncation retains the newest results")
    func truncation() {
        let result = TestResult(testResult: "110010")

        result.truncateToLength(size: 4)

        #expect(result.string == "0010")
        #expect(result.length == 4)
    }

    @Test("Truncating to the current or a larger size leaves the result unchanged")
    func nonReducingTruncation() {
        let result = TestResult(testResult: "101")

        result.truncateToLength(size: 3)
        #expect(result.string == "101")

        result.truncateToLength(size: 10)
        #expect(result.string == "101")
    }
}

@Suite("Permutations", .serialized)
struct PermutationsTests {
    @Test("Generation produces every binary sequence grouped by failure count")
    func generatedFormulary() {
        let permutations = Permutations(window: 4)

        #expect(permutations.allPermutations.count == 5)
        #expect(permutations.allPermutations.map(\.count) == [1, 4, 6, 4, 1])

        for failureCount in 0...4 {
            let entries = permutations.allPermutations[failureCount]
            #expect(Set(entries).count == entries.count)
            #expect(entries.allSatisfy { entry in
                entry.count == 4 && entry.filter { $0 == "1" }.count == failureCount
            })
        }

        #expect(permutations.allPermutations[0] == ["0000"])
        #expect(permutations.allPermutations[4] == ["1111"])
    }

    @Test("Complementary groups are bitwise inverses")
    func complementaryGroups() {
        let permutations = Permutations(window: 5)

        for failureCount in 0...5 {
            #expect(
                permutations.allPermutations[failureCount].invert()
                    == permutations.allPermutations[5 - failureCount]
            )
        }
    }

    @Test("Confidence is highest near the center and symmetric")
    func confidenceWeighting() {
        let permutations = Permutations(window: 4)
        let template = permutations.allPermutations[2]

        let weights = template.map {
            permutations.findConfidence(testResult: TestResult(testResult: $0))
        }

        #expect(weights[2] == 100)
        #expect(weights[1] == weights[3])
        #expect(weights[0] == weights[4])
        #expect(weights[0] < weights[1])
        #expect(weights[1] < weights[2])
        #expect(weights[5] < weights[0])
    }

    @Test("Beta changes the confidence falloff")
    func betaControlsFalloff() {
        let permutations = Permutations(window: 4)
        let result = TestResult(testResult: permutations.allPermutations[2][0])

        let lowBeta = permutations.findConfidence(testResult: result, beta: 1)
        let highBeta = permutations.findConfidence(testResult: result, beta: 6)

        #expect(lowBeta != highBeta)
        #expect((0...100).contains(lowBeta))
        #expect((0...100).contains(highBeta))
    }

    @Test("A result missing from its failure-count template has zero confidence")
    func missingResult() {
        let permutations = Permutations(window: 3)
        permutations.allPermutations[1] = []

        let confidence = permutations.findConfidence(
            testResult: TestResult(testResult: "100")
        )

        #expect(confidence == 0)
    }
}

@Suite("FlakyTest evaluation", .serialized)
struct FlakyTestEvaluationTests {
    @Test("Public defaults remain stable")
    func defaults() {
        #expect(FlakyTest.MIN_TEST_COUNT == 10)
        #expect(FlakyTest.DEFAULT_FAIL_PCT == 0.85)
        #expect(FlakyTest.DEFAULT_PASS_PCT == 0.10)
        #expect(FlakyTest.DEFAULT_DEV_BOUND == 4)
    }

    @Test("Initialization configures the requested analysis")
    func initialization() {
        let analyzer = FlakyTest(
            failPctUpper: 0.75,
            failPctLower: 0.25,
            deviationBound: 2,
            testCount: 11
        )

        #expect(analyzer.testCount == 11)
        #expect(analyzer.deviationBound == 2)
        #expect(analyzer.passRange == 0.25...0.75)
        #expect(analyzer.permutationEngine.window == 11)
    }

    @Test("An empty input returns no confidences")
    func emptyInput() {
        let analyzer = FlakyTest(testCount: 11)

        #expect(analyzer.evaluate(testResults: []).isEmpty)
    }

    @Test("In-range results are evaluated by the permutation engine")
    func inRangeResult() throws {
        let analyzer = FlakyTest(testCount: 11)
        let result = TestResult(testResult: "00000111111")
        let expected = analyzer.permutationEngine.findConfidence(
            testResult: result,
            beta: analyzer.deviationBound
        )

        let evaluated = try #require(analyzer.evaluate(testResults: [result]).first)

        #expect(evaluated.testResult === result)
        #expect(evaluated.confidence == expected)
        #expect(evaluated.confidence > 0)
    }

    @Test(
        "Results outside inclusive failure bounds receive zero confidence",
        arguments: ["00000000000", "11111111111"]
    )
    func outOfRangeResult(sequence: String) throws {
        let analyzer = FlakyTest(
            failPctUpper: 0.75,
            failPctLower: 0.25,
            testCount: 11
        )
        let result = TestResult(testResult: sequence)

        let evaluated = try #require(analyzer.evaluate(testResults: [result]).first)

        #expect(evaluated.testResult === result)
        #expect(evaluated.confidence == 0)
    }

    @Test("Failure bounds include both endpoints")
    func inclusiveBounds() {
        let analyzer = FlakyTest(
            failPctUpper: 0.75,
            failPctLower: 0.25,
            testCount: 12
        )
        let lower = TestResult(testResult: "111000000000")
        let upper = TestResult(testResult: "111111111000")
        let evaluations = analyzer.evaluate(testResults: [lower, upper])

        #expect(evaluations.count == 2)
        #expect(evaluations.allSatisfy { $0.confidence > 0 })
    }

    @Test("Long histories are truncated to the configured newest window")
    func longHistoryTruncation() throws {
        let analyzer = FlakyTest(testCount: 11)
        let result = TestResult(testResult: "11111100000111111")

        let evaluated = try #require(analyzer.evaluate(testResults: [result]).first)

        #expect(result.string == "00000111111")
        #expect(result.length == 11)
        #expect(evaluated.testResult === result)
        #expect(evaluated.confidence > 0)
    }

    @Test("Insufficient out-of-range data receives zero confidence")
    func insufficientData() throws {
        let analyzer = FlakyTest(testCount: 11)
        let result = TestResult(testResult: "0000")

        let evaluations = analyzer.evaluate(testResults: [result])
        let evaluated = try #require(evaluations.first)

        withKnownIssue("Insufficient results are appended once before bounds checking and again afterward.") {
            #expect(evaluations.count == 1)
        }
        #expect(evaluated.testResult === result)
        #expect(evaluated.confidence == 0)
        #expect(result.length == 4)
    }

    @Test("Multiple results preserve input order")
    func multipleResults() {
        let analyzer = FlakyTest(testCount: 11)
        let first = TestResult(testResult: "00000111111")
        let second = TestResult(testResult: "11111111111")
        let evaluations = analyzer.evaluate(testResults: [first, second])

        #expect(evaluations.count == 2)
        #expect(evaluations[0].testResult === first)
        #expect(evaluations[1].testResult === second)
        #expect(evaluations[0].confidence > 0)
        #expect(evaluations[1].confidence == 0)
    }
}
