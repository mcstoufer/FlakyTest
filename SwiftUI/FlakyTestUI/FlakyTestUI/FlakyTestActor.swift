//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  FlakyTestActor.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/20/26.
//
import FlakyTest
import Foundation

actor
FlakyTestActor {
    private let flakyTest: FlakyTest
    
    init(passPct: Float, failPct: Float, deviationBound: Float, testCount: Int) {
        self.flakyTest = FlakyTest(
            passPctUpper: failPct,
            passPctLower: passPct,
            deviationBound: deviationBound,
            testCount: testCount
        )
    }
    
    func findConfidence(testResult: TestResult) -> Float {
        let confidences = self.flakyTest.evaluate(testResults: [testResult])
        return confidences[0].confidence
    }
}
