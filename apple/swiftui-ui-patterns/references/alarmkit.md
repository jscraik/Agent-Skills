# Using AlarmKit in a SwiftUI App

## Overview
AlarmKit (iOS 18+) lets apps create custom alarms and timers with system UI, Live Activities, and authorization. Use this reference when building alarm/timer experiences.

## Authorization
```swift
// Info.plist: NSAlarmKitUsageDescription

func requestAlarmAuthorization() async -> Bool {
    do {
        let state = try await AlarmManager.shared.requestAuthorization()
        return state == .authorized
    } catch {
        return false
    }
}
```

Use `authorizationState` (not `authorizationStatus`).

## Scheduling an alarm (one-time)
```swift
func createOneTimeAlarm(hour: Int, minute: Int) async throws -> Alarm {
    let id = UUID()
    let time = Alarm.Schedule.Relative.Time(hour: hour, minute: minute)
    let schedule = Alarm.Schedule.relative(.init(time: time, repeats: .never))

    let alertContent = AlarmPresentation.Alert(
        title: "Wake Up",
        stopButton: .stopButton,
        secondaryButton: .openAppButton,
        secondaryButtonBehavior: .custom
    )

    let presentation = AlarmPresentation(alert: alertContent)
    struct EmptyMetadata: AlarmMetadata {}

    let attributes = AlarmAttributes(
        presentation: presentation,
        metadata: EmptyMetadata(),
        tintColor: .blue
    )

    let configuration = AlarmManager.AlarmConfiguration(
        countdownDuration: nil,
        schedule: schedule,
        attributes: attributes,
        sound: .default
    )

    return try await AlarmManager.shared.schedule(id: id, configuration: configuration)
}
```

## Repeating alarm
```swift
func createWeeklyAlarm(hour: Int, minute: Int, weekdays: Set<Locale.Weekday>) async throws -> Alarm {
    let id = UUID()
    let time = Alarm.Schedule.Relative.Time(hour: hour, minute: minute)
    let schedule = Alarm.Schedule.relative(.init(time: time, repeats: .weekly(Array(weekdays))))

    let alertContent = AlarmPresentation.Alert(
        title: "Weekly Reminder",
        stopButton: .stopButton,
        secondaryButton: .snoozeButton,
        secondaryButtonBehavior: .countdown
    )

    let countdownDuration = Alarm.CountdownDuration(preAlert: nil, postAlert: 9 * 60)
    let presentation = AlarmPresentation(alert: alertContent)

    struct EmptyMetadata: AlarmMetadata {}
    let attributes = AlarmAttributes(
        presentation: presentation,
        metadata: EmptyMetadata(),
        tintColor: .green
    )

    let configuration = AlarmManager.AlarmConfiguration(
        countdownDuration: countdownDuration,
        schedule: schedule,
        attributes: attributes,
        sound: .default
    )

    return try await AlarmManager.shared.schedule(id: id, configuration: configuration)
}
```

## Timer (countdown)
```swift
func createCountdownTimer(seconds: TimeInterval) async throws -> Alarm {
    let id = UUID()
    let countdownDuration = Alarm.CountdownDuration(preAlert: seconds, postAlert: 10)

    let alert = AlarmPresentation.Alert(
        title: "Timer Complete",
        stopButton: .stopButton,
        secondaryButton: .repeatButton,
        secondaryButtonBehavior: .countdown
    )

    let countdown = AlarmPresentation.Countdown(title: "Timer Running", pauseButton: .pauseButton)
    let paused = AlarmPresentation.Paused(title: "Timer Paused", resumeButton: .resumeButton)

    let presentation = AlarmPresentation(alert: alert, countdown: countdown, paused: paused)

    struct TimerMetadata: AlarmMetadata { let purpose: String }
    let attributes = AlarmAttributes(
        presentation: presentation,
        metadata: TimerMetadata(purpose: "Cooking Timer"),
        tintColor: .orange
    )

    let configuration = AlarmManager.AlarmConfiguration(
        countdownDuration: countdownDuration,
        schedule: nil,
        attributes: attributes,
        sound: .default
    )

    return try await AlarmManager.shared.schedule(id: id, configuration: configuration)
}
```

## Observing alarm changes
```swift
Task {
    for await alarms in AlarmManager.shared.alarmUpdates {
        // Update UI with alarms
    }
}
```

## Live Activities
Implement a widget extension for countdown presentations. Use `ActivityConfiguration` with `AlarmAttributes` and `AlarmState`.

## Best Practices
- Request authorization early and handle denial.
- Provide clear `NSAlarmKitUsageDescription`.
- Use Live Activities for countdown presentations.
- Observe `alarmUpdates` and `authorizationUpdates`.
- Test on physical devices.

## References
- https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit
- https://developer.apple.com/documentation/AlarmKit
- https://developer.apple.com/documentation/AlarmKit/AlarmManager
- https://developer.apple.com/documentation/AlarmKit/Alarm
- https://developer.apple.com/documentation/AlarmKit/AlarmPresentation
- https://developer.apple.com/documentation/AlarmKit/AlarmAttributes
- https://developer.apple.com/wwdc25/230
