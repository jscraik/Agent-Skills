// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "ImproveAgentNativeMenuBar",
    platforms: [.macOS(.v14)],
    products: [
        .library(name: "ImproveAgentNativeMenuBarCore", targets: ["ImproveAgentNativeMenuBarCore"]),
        .executable(name: "ImproveAgentNativeMenuBar", targets: ["ImproveAgentNativeMenuBar"])
    ],
    targets: [
        .target(name: "ImproveAgentNativeMenuBarCore"),
        .executableTarget(
            name: "ImproveAgentNativeMenuBar",
            dependencies: ["ImproveAgentNativeMenuBarCore"],
            resources: [.process("Resources")]
        ),
        .testTarget(
            name: "ImproveAgentNativeMenuBarCoreTests",
            dependencies: ["ImproveAgentNativeMenuBarCore"]
        )
    ]
)
