//
//  Logger+Extensions.swift
//  FlakyTest
//
//  Created by Martin Stoufer on 10/17/26.
//
import Foundation
import OSLog

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.mcstoufer.flaky_test"
    
    static let core = Logger(subsystem: subsystem, category: "Core")
    
    static let engine = Logger(subsystem: subsystem, category: "Engine")
}
