# Swift Charts 3D

## Overview
Use this reference when building 3D data visualizations with Swift Charts and Chart3D.

## Basic Chart3D
```swift
import SwiftUI
import Charts

struct Basic3DChartView: View {
    var body: some View {
        Chart3D {
            SurfacePlot(
                x: "X Axis",
                y: "Y Axis",
                z: "Z Axis",
                function: { x, y in
                    sin(x) * cos(y)
                }
            )
        }
    }
}
```

## Pose and camera projection
```swift
@State private var chartPose: Chart3DPose = .default
@State private var cameraProjection: Chart3DCameraProjection = .perspective

Chart3D {
    SurfacePlot(x: "X", y: "Y", z: "Z", function: { x, y in sin(x) * cos(y) })
}
.chart3DPose(chartPose)
.chart3DCameraProjection(cameraProjection)
```

## Interactive pose binding
```swift
.chart3DPose($chartPose)
```

## Surface styling
```swift
SurfacePlot(x: "X", y: "Y", z: "Z", function: { x, y in sin(x) * cos(y) })
    .foregroundStyle(Chart3DSurfaceStyle.heightBased(yRange: -1.0...1.0))
    .roughness(0.2)
```

## References
- https://developer.apple.com/documentation/Charts/Chart3D
- https://developer.apple.com/documentation/Charts/SurfacePlot
- https://developer.apple.com/documentation/Charts/Chart3DPose
- https://developer.apple.com/documentation/Charts/Chart3DSurfaceStyle
- https://developer.apple.com/documentation/Charts/Creating-a-chart-using-Swift-Charts
