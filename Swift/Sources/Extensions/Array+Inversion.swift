//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  Array+Inversion.swift
//  FlakyTest
//
//  Created by Martin Stoufer on 10/17/26.
//

extension Array where Element==String {
    func invert() -> [String] {
        return self.map { $0.invert() }
    }
}

extension String {
    static let TRANS_TABLE: [Character: Character] = ["1": "0", "0": "1"]

    func invert() -> String {
        return String(self.map { String.TRANS_TABLE[$0] ?? $0 })
    }
}
