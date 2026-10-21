// SPDX-FileCopyrightText: 2026 Martin Stoufer
// SPDX-License-Identifier: GPL-3.0-only

import OSLog

public typealias Confidence = (testResult: TestResult, confidence: Float)

public class FlakyTest {
    public static let MIN_TEST_COUNT: Int = 10
    public static let DEFAULT_FAIL_PCT:Float = 0.85
    public static let DEFAULT_PASS_PCT:Float = 0.10
    public static let DEFAULT_DEV_BOUND: Float = 4.0
    
    let deviationBound: Float
    let testCount: Int
    let permutationEngine: Permutations
    let passRange: ClosedRange<Float>
    
    public init(
        failPctUpper: Float = DEFAULT_FAIL_PCT,
        failPctLower: Float = DEFAULT_PASS_PCT,
        deviationBound: Float = DEFAULT_DEV_BOUND,
        testCount: Int = 14
    ) {
        assert(testCount > FlakyTest.MIN_TEST_COUNT, "Test count not long enough. Must be at least \(FlakyTest.MIN_TEST_COUNT)")
        self.deviationBound = deviationBound
        self.testCount = testCount
        self.permutationEngine = Permutations(window: self.testCount)
        self.passRange = failPctLower...failPctUpper
    }
    
    public func evaluate(testResults: [TestResult]) -> [Confidence] {
        var calculatedConfidences: [Confidence] = []
        
        testResults.forEach { testResult in
            if testResult.length > self.testCount {
                testResult.truncateToLength(size:self.testCount)
            } else if testResult.length < self.testCount {
                Logger.core.notice("Insufficient data to run test. Adjust 'test_count' to match the length: \(testResult.length)")
                calculatedConfidences.append((testResult, 0.0))
            }
            
            if self.passRange.contains(testResult.failPct) {
                let calculatedConfidence = self.permutationEngine.findConfidence(testResult: testResult, beta: self.deviationBound)
                calculatedConfidences.append((testResult, calculatedConfidence))
            } else {
                Logger.core.warning("Test result outside of statistical bounds.")
                calculatedConfidences.append((testResult, 0.0))
            }
        }
        return calculatedConfidences
    }
}
