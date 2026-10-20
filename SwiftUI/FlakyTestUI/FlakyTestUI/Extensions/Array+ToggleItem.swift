//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  Array+ToggleItem.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/19/26.
//

extension Array where Element==ToggleItem {
    func reduceToPattern() -> String {
        return self.map { testResult in
            testResult.pattern
        }.joined()
    }
}
