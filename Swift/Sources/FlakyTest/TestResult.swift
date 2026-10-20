//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  TestResult.swift
//  FlakyTest
//
//  Created by Martin Stoufer on 10/17/26.
//

public class TestResult {
    var testResults: [String]
    
    public convenience init(testResult: String) {
        self.init(testResults: testResult.map { String($0) })
    }
    
    public init(testResults: [String]) {
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
