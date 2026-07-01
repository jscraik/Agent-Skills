// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "ImproveAgentNativeMenuBar",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "ImproveAgentNativeMenuBar", targets: ["ImproveAgentNativeMenuBar"])
    ],
    targets: [
        .executableTarget(
            name: "ImproveAgentNativeMenuBar",
            resources: [.process("Resources")]
        )
    ]
)
