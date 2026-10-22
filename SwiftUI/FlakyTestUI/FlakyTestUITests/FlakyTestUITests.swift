//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//

import Testing
import FlakyTest
@testable import FlakyTestUI

@MainActor
struct FlakyTestUITests {
    @Test func `Toggle item reflects its state`() {
        let passingItem = ToggleItem(isOn: false)
        let failingItem = ToggleItem(isOn: true)

        #expect(passingItem.name == "pass")
        #expect(passingItem.pattern == "0")
        #expect(failingItem.name == "fail")
        #expect(failingItem.pattern == "1")
    }

    @Test func `Toggle items reduce to an ordered pattern`() {
        let items = [ToggleItem(isOn: false), ToggleItem(isOn: true),
                     ToggleItem(isOn: true), ToggleItem(isOn: false)]

        #expect(items.reduceToPattern() == "0110")
        #expect([ToggleItem]().reduceToPattern().isEmpty)
    }

    @Test func `View model starts with expected defaults`() {
        let viewModel = FlakyTestUIViewModel()

        #expect(viewModel.errorString.isEmpty)
        #expect(viewModel.confidence == 0)
        #expect(viewModel.passPct == 10)
        #expect(viewModel.failPct == 85)
        #expect(viewModel.deviation == 4)
        #expect(viewModel.items.count == 14)
        #expect(viewModel.items.allSatisfy { !$0.isOn })
    }

    @Test(arguments: [false, true])
    func `Adding a test appends the requested state`(isFailing: Bool) {
        let viewModel = FlakyTestUIViewModel()
        viewModel.errorString = "previous error"

        viewModel.addTest(pass: isFailing)

        #expect(viewModel.items.count == 15)
        #expect(viewModel.items.last?.isOn == isFailing)
        #expect(viewModel.errorString.isEmpty)
    }

    @Test func `Replacing items updates the backing collection`() {
        let viewModel = FlakyTestUIViewModel()
        let replacement = [ToggleItem(isOn: true)]

        viewModel.items = replacement

        #expect(viewModel.items == replacement)
        #expect(viewModel._items == replacement)
    }

    @Test func `Turning a test on clears stale output`() {
        let viewModel = FlakyTestUIViewModel()
        viewModel.errorString = "previous error"
        viewModel.confidence = 42

        viewModel.updateToggleState(at: 0, to: true)

        #expect(viewModel.items[0].isOn)
        #expect(viewModel.errorString.isEmpty)
        #expect(viewModel.confidence == 0)
    }

    @Test func `Turning a test off preserves existing output`() {
        let viewModel = FlakyTestUIViewModel()
        viewModel._items[0].isOn = true
        viewModel.errorString = "existing error"
        viewModel.confidence = 42

        viewModel.updateToggleState(at: 0, to: false)

        #expect(!viewModel.items[0].isOn)
        #expect(viewModel.errorString == "existing error")
        #expect(viewModel.confidence == 42)
    }

    @Test func `Deleting above minimum removes the final test`() {
        let viewModel = FlakyTestUIViewModel()
        viewModel.addTest(pass: true)
        let expectedLastItem = viewModel.items[13]

        viewModel.deleteLastTest()

        #expect(viewModel.items.count == 14)
        #expect(viewModel.items.last == expectedLastItem)
        #expect(viewModel.errorString.isEmpty)
    }

    @Test func `Deleting down to minimum reports the lower bound`() {
        let viewModel = FlakyTestUIViewModel()
        viewModel.items = Array(viewModel.items.prefix(11))

        viewModel.deleteLastTest()

        #expect(viewModel.items.count == 10)
        #expect(viewModel.errorString == "⚠️ Flaky Test list count cannot go below 10")
    }

    @Test func `Deleting at minimum keeps all tests and reports the lower bound`() {
        let viewModel = FlakyTestUIViewModel()
        viewModel.items = Array(viewModel.items.prefix(10))

        viewModel.deleteLastTest()

        #expect(viewModel.items.count == 10)
        #expect(viewModel.errorString == "⚠️ Flaky Test list count cannot go below 10")
    }

    @Test func `Confidence is zero when failures are outside configured bounds`() async {
        let viewModel = FlakyTestUIViewModel()

        await viewModel.findConfidence()

        #expect(viewModel.confidence == 0)
    }

    @Test func `Confidence is calculated for a result inside configured bounds`() async {
        let viewModel = FlakyTestUIViewModel()
        viewModel.updateToggleState(at: 0, to: true)
        viewModel.updateToggleState(at: 1, to: true)

        await viewModel.findConfidence()

        #expect(viewModel.confidence > 0)
        #expect(viewModel.confidence <= 100)
    }

    @Test func `Actor returns zero for a result outside configured bounds`() async {
        let actor = FlakyTestActor(passPct: 0.1, failPct: 0.85, deviationBound: 4, testCount: 14)

        let confidence = await actor.findConfidence(testResult: .init(testResult: "00000000000000"))

        #expect(confidence == 0)
    }
}
