// swift-tools-version: 6.4
// SPDX-FileCopyrightText: 2026 Martin Stoufer
// SPDX-License-Identifier: GPL-3.0-only
//
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "FlakyTest",
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "FlakyTest",
            targets: ["FlakyTest"]
        ),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "FlakyTest",
            path: "Sources",
            swiftSettings: [
                .enableUpcomingFeature("ApproachableConcurrency"),
            ],
        ),
        .testTarget(
            name: "FlakyTestTests",
            dependencies: ["FlakyTest"],
            swiftSettings: [
                .enableUpcomingFeature("ApproachableConcurrency"),
            ],
        ),
    ]
)
