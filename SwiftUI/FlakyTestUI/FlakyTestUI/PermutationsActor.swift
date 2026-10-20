//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  PermutationsActor.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/20/26.
//
import FlakyTest
import Foundation

actor
FlakyTestActor {
    private let flakyTest: FlakyTest
    
    init(testCount: Int) {
        self.flakyTest = FlakyTest(testCount: testCount)
    }
    
    func findConfidence(testResult: TestResult) -> Float {
        let confidences = self.flakyTest.evaluate(testResults: [testResult])
        return confidences[0].confidence
    }
}
