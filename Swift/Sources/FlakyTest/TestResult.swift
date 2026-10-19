//
//  TestResult.swift
//  FlakyTest
//
//  Created by Martin Stoufer on 10/17/26.
//

public class TestResult {
    var testResults: [String]
    
    init(testResults: [String]) {
        self.testResults = testResults
    }
    
    var length:Int {
        return testResults.count
    }
    
    var string: String {
        return testResults.joined()
    }
    
    var failCount: Int {
        return testResults.filter { $0 == "1" }.count

    }
    var failPct: Float {
        return Float(self.failCount) / Float(self.length)
    }
    
    func truncateToLength(size: Int) {
        testResults = Array(testResults.suffix(size))
    }
}
