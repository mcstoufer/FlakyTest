//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  FlakyTestUIViewModel.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/19/26.
//

import Foundation
import FlakyTest

// Model structure representing each individual toggle unit
struct ToggleItem: Identifiable, Hashable {
    let id: UUID = UUID()
    var name: String {
        return isOn ? "fail" : "pass"
    }
    var isOn: Bool
    
    var pattern: String {
        return isOn ? "1" : "0"
    }
}

@Observable
@MainActor
class FlakyTestUIViewModel {
    
    var errorString: String = ""
    var confidence: Float = 0.0
    var passPct: Int = Int(FlakyTest.DEFAULT_PASS_PCT * 100)
    var failPct: Int = Int(FlakyTest.DEFAULT_FAIL_PCT * 100)
    var deviation: Float = FlakyTest.DEFAULT_DEV_BOUND
    
    // Backing array holding the source of truth for the states
    var _items: [ToggleItem] = Array(repeating: ToggleItem(isOn: false), count: 14)
    
    var items: [ToggleItem] {
        get { _items }
        set { _items = newValue}
    }
    
    func updateToggleState(at index: Int, to  newValue: Bool) {
        _items[index].isOn = newValue
        
        if newValue {
            errorString = ""
            confidence = 0.0
        }
    }
    
    func addTest(pass: Bool = false) {
        errorString = ""
        items.append(ToggleItem(isOn: pass))
    }
    
    func deleteLastTest() {
        if items.count > FlakyTest.MIN_TEST_COUNT {
            items.removeLast()
            errorString = ""
        }
        if items.count == FlakyTest.MIN_TEST_COUNT {
            errorString = "⚠️ Flaky Test list count cannot go below \(FlakyTest.MIN_TEST_COUNT)"
        }
    }
    
    func findConfidence() async {
        let engine = FlakyTestActor(
            passPct: Float(passPct) / 100.0,
            failPct: Float(failPct) / 100.0,
            deviationBound: deviation,
            testCount: items.count
        )
        let result = await engine.findConfidence(testResult: TestResult(testResult: items.reduceToPattern()))
        confidence = result
    }
}
