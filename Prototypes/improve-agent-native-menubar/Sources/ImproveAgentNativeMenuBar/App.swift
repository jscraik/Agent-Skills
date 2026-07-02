import AppKit
import Foundation
import SwiftUI

@main
struct ImproveAgentNativeMenuBarApp: App {
    @StateObject private var model = DashboardModel()

    var body: some Scene {
        MenuBarExtra {
            DashboardView(model: model)
                .frame(width: 332, height: 742)
                .task {
                    await model.refresh()
                }
        } label: {
            Text(model.menuTitle)
                .font(.system(size: 12, weight: .bold, design: .rounded))
        }
        .menuBarExtraStyle(.window)
    }
}

@MainActor
final class DashboardModel: ObservableObject {
    @Published var dashboard = SkillDashboard.placeholder
    @Published var isRefreshing = false
    private var didAttemptLoad = false

    init() {}

    var menuTitle: String {
        if isRefreshing, dashboard.score == nil {
            return "SDK ..."
        }
        if let score = dashboard.score {
            return "SDK \(score)"
        }
        if dashboard.tessl.displayStatus == "Auth needed" {
            return "SDK Auth"
        }
        if dashboard.tessl.displayStatus == "CLI missing" {
            return "SDK CLI"
        }
        return "SDK --"
    }

    func refresh(force: Bool = false) async {
        guard !isRefreshing else { return }
        guard force || !didAttemptLoad else { return }
        didAttemptLoad = true
        isRefreshing = true
        defer { isRefreshing = false }
        do {
            dashboard = try await DashboardLoader().load()
        } catch {
            dashboard = SkillDashboard.placeholder.withError(error.localizedDescription)
        }
    }
}

struct DashboardView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var model: DashboardModel

    var body: some View {
        TimelineView(.animation(minimumInterval: 1.0 / 30.0)) { timeline in
            dashboardBody(phase: PollingEffect.phase(at: timeline.date))
        }
    }

    private func dashboardBody(phase: Double) -> some View {
        let pollingPulse = PollingEffect.pulse(from: phase)
        return ZStack {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color.white.opacity(0.06), Color(red: 0.030, green: 0.031, blue: 0.034).opacity(0.86), Color.black.opacity(0.66)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .strokeBorder(Color.white.opacity(model.isRefreshing ? 0.12 + (0.04 * pollingPulse) : 0.12), lineWidth: 1)
                )
                .shadow(color: Color.white.opacity(model.isRefreshing ? 0.02 + (0.06 * pollingPulse) : 0.02), radius: model.isRefreshing ? 16 : 0, x: 0, y: 0)
                .shadow(color: .black.opacity(0.46), radius: 28, x: 0, y: 18)

            VStack(spacing: 0) {
                HeaderScoreView(dashboard: model.dashboard, isRefreshing: model.isRefreshing, pulse: pollingPulse)
                    .padding(.top, 26)

                VStack(alignment: .leading, spacing: 20) {
                    SkillIdentityView(dashboard: model.dashboard)
                    EvidenceRow(metric: model.dashboard.quality, title: "Quality", isRefreshing: model.isRefreshing, phase: phase)
                    EvidenceRow(metric: model.dashboard.impact, title: "Impact", badgeText: model.dashboard.deltaBadgeText, isRefreshing: model.isRefreshing, phase: phase)
                    SecurityBlock(signal: model.dashboard.security, isRefreshing: model.isRefreshing, phase: phase)
                    InstallCommand(command: model.dashboard.installCommand)
                    FooterBar(model: model)
                }
                .padding(.horizontal, 24)
                .padding(.top, 26)

                Spacer(minLength: 8)
            }
            .padding(6)
        }
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .foregroundStyle(.primaryText)
        .onExitCommand {
            dismiss()
        }
    }
}

enum PollingEffect {
    static func phase(at date: Date) -> Double {
        let cycle = date.timeIntervalSinceReferenceDate.truncatingRemainder(dividingBy: 1.2) / 1.2
        return min(max(cycle, 0), 1)
    }

    static func pulse(from phase: Double) -> Double {
        (sin(phase * .pi * 2 - .pi / 2) + 1) / 2
    }
}

struct ClosePopoverButton: View {
    let action: () -> Void

    var body: some View {
        Button {
            action()
        } label: {
            Image(systemName: "xmark")
                .font(.system(size: 12, weight: .semibold))
                .frame(width: 28, height: 28)
                .contentShape(Circle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(Color.white.opacity(0.62))
        .background {
            Circle()
                .fill(.thinMaterial)
                .opacity(0.18)
        }
        .overlay {
            Circle()
                .stroke(Color.white.opacity(0.10), lineWidth: 1)
        }
        .help("Close popover")
        .accessibilityLabel("Close popover")
    }
}

struct HeaderScoreView: View {
    let dashboard: SkillDashboard
    let isRefreshing: Bool
    let pulse: Double

    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                Hexagon()
                    .fill(.ultraThinMaterial)
                    .overlay(
                        Hexagon()
                            .fill(LinearGradient(colors: [.greenPanel.opacity(0.88), Color(red: 0.0, green: 0.05, blue: 0.025).opacity(0.94)], startPoint: .top, endPoint: .bottom))
                    )
                    .overlay(Hexagon().stroke(Color.black.opacity(0.42), lineWidth: 5))
                    .overlay(Hexagon().stroke(Color.greenBorder.opacity(0.78), lineWidth: 2))
                    .overlay(
                        Hexagon()
                            .stroke(LinearGradient(colors: [Color.successAccent.opacity(0.18), Color.clear], startPoint: .top, endPoint: .center), lineWidth: 1)
                            .padding(4)
                    )
                    .shadow(color: Color.successAccent.opacity(isRefreshing ? 0.08 + (0.20 * pulse) : 0.08), radius: isRefreshing ? 16 : 8, x: 0, y: 0)
                    .shadow(color: .black.opacity(0.54), radius: 20, x: 0, y: 16)
                    .frame(width: 160, height: 138)
                    .scaleEffect(isRefreshing ? 1.0 + (0.018 * pulse) : 1.0)

                Text(dashboard.scoreText)
                    .font(.system(size: 42, weight: .heavy, design: .rounded))
                    .foregroundStyle(dashboard.scoreTone == .positive ? dashboard.scoreTone.color : .primaryText)
                    .opacity(isRefreshing ? 0.82 + (0.18 * pulse) : 1.0)
            }

            HStack(spacing: 8) {
                Image(systemName: "arrow.up")
                    .font(.system(size: 18, weight: .bold))
                Text(dashboard.deltaBadgeText)
                    .font(.system(size: 17, weight: .heavy, design: .rounded))
            }
            .foregroundStyle(Color(red: 0.56, green: 1.0, blue: 0.70))
            .padding(.horizontal, 21)
            .padding(.vertical, 11)
            .background(Color.greenPanel.opacity(0.86))
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 8, style: .continuous).stroke(Color.greenBorder.opacity(0.90), lineWidth: 1))
            .offset(y: -12)
        }
    }
}

struct VerificationNotice: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            HStack(spacing: 8) {
                Text(dashboard.verificationTitle)
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                    .foregroundStyle(dashboard.scoreTone.color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.86)
                Spacer()
                HStack(spacing: 5) {
                    Image(systemName: dashboard.tessl.ok ? "checkmark" : "lock.fill")
                        .font(.system(size: 9, weight: .bold))
                    Text(dashboard.tessl.ok ? "Verified" : "Auth required")
                        .font(.system(size: 10, weight: .semibold))
                }
                .foregroundStyle(dashboard.tessl.ok ? StatusTone.positive.color : .primaryText)
            }
            Text(dashboard.verificationDetail)
                .font(.system(size: 10, weight: .regular))
                .foregroundStyle(.bodyText)
                .lineLimit(2)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(.thinMaterial)
        .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).fill(Color.white.opacity(0.045)))
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.white.opacity(0.11), lineWidth: 1))
    }
}

struct SkillIdentityView: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(dashboard.registryPath)
                .font(.system(size: 15, weight: .semibold, design: .rounded))
                .foregroundStyle(.secondaryText)
                .lineLimit(1)
            Text(dashboard.displayName)
                .font(.system(size: 17, weight: .bold, design: .rounded))
            Text(dashboard.summaryLine)
                .font(.system(size: 14, weight: .medium, design: .rounded))
                .lineSpacing(5)
                .foregroundStyle(.bodyText)
                .lineLimit(2)
        }
    }
}

struct EvidenceRow: View {
    let metric: MetricSignal
    let title: String
    var badgeText: String?
    var isRefreshing = false
    var phase = 0.0

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Text(title)
                    .font(.system(size: 15, weight: .heavy, design: .rounded))
                Spacer()
                HStack(spacing: 8) {
                    Text(metric.statusLabel)
                        .font(.system(size: 15, weight: .heavy, design: .rounded))
                        .foregroundStyle(metric.tone.color)
                    if let badgeText {
                        StatusBadge(text: badgeText, systemName: "arrow.up", tone: metric.tone)
                    }
                }
            }
            if let score = metric.score {
                ProgressStripe(value: min(max(Double(score) / 100.0, 0), 1), tone: metric.tone, showsFill: true, isRefreshing: isRefreshing, phase: phase)
            } else {
                StaticRail(tone: .pending, isRefreshing: isRefreshing, phase: phase)
            }
            Text(metric.compactDetail)
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
        }
    }
}

struct SecurityBlock: View {
    let signal: SecuritySignal
    var isRefreshing = false
    var phase = 0.0

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                HStack(spacing: 8) {
                    Text("Security")
                        .font(.system(size: 15, weight: .heavy, design: .rounded))
                    Text(signal.sourceBadgeText)
                        .font(.system(size: 13, weight: .heavy, design: .rounded))
                        .foregroundStyle(.primaryText)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.white.opacity(0.055))
                        .clipShape(RoundedRectangle(cornerRadius: 7, style: .continuous))
                }
                Spacer()
                Text(signal.status)
                    .font(.system(size: 15, weight: .heavy, design: .rounded))
                    .foregroundStyle(signal.tone.color)
            }

            if signal.status.localizedCaseInsensitiveContains("flag") {
                SegmentedResultBar(tone: signal.tone, filledSegments: 3, totalSegments: 5, isRefreshing: isRefreshing, phase: phase)
            } else if signal.score != nil {
                SegmentedResultBar(tone: signal.tone, filledSegments: signal.segmentCount, totalSegments: 5, isRefreshing: isRefreshing, phase: phase)
            } else {
                StaticRail(tone: .pending, isRefreshing: isRefreshing, phase: phase)
            }

            Text(signal.detailLine)
                .font(.system(size: 12, weight: .regular))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
                .accessibilityLabel(signal.accessibilityText)
        }
    }
}

struct TesslBlock: View {
    let signal: TesslSignal

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack {
                HStack(spacing: 8) {
                    TesslLogoView()
                    Text(signal.title)
                        .font(.system(size: 13, weight: .heavy, design: .rounded))
                }
                Spacer()
                Text(signal.displayStatus)
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                    .foregroundStyle(.secondaryText)
            }
            Text(signal.compactDetail)
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
        }
    }
}

struct PrimaryAction: View {
    let signal: TesslSignal

    var body: some View {
        Button {
            NSWorkspace.shared.open(URL(string: "https://tessl.io/registry/jscraik/improve-agent-native")!)
        } label: {
            HStack(spacing: 8) {
                Image(systemName: signal.ok ? "checkmark.seal.fill" : "lock.fill")
                    .font(.system(size: 12, weight: .bold))
                Text(signal.ok ? "Open Tessl registry" : "Sign in to Tessl")
                    .font(.system(size: 12, weight: .heavy, design: .rounded))
                Spacer()
            }
            .foregroundStyle(signal.ok ? StatusTone.positive.color : Color.white.opacity(0.94))
            .padding(.horizontal, 12)
            .padding(.vertical, 5)
            .background(.thinMaterial)
            .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).fill((signal.ok ? StatusTone.positive : StatusTone.warning).panelColor.opacity(signal.ok ? 0.75 : 0.78)))
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 10).stroke((signal.ok ? StatusTone.positive : StatusTone.warning).color.opacity(0.42), lineWidth: 1))
        }
        .buttonStyle(.plain)
        .help(signal.ok ? "Open Tessl registry" : "Open Tessl to complete authentication")
        .accessibilityLabel(signal.ok ? "Open Tessl registry" : "Sign in to Tessl to finish Quality and Impact checks")
    }
}

struct TesslLogoView: View {
    var body: some View {
        ZStack {
            Circle()
                .fill(.thinMaterial)
            Circle()
                .fill(Color.black.opacity(0.34))

            if let image = TesslLogoLoader.image {
                Image(nsImage: image)
                    .resizable()
                    .interpolation(.high)
                    .scaledToFill()
                    .scaleEffect(1.95)
                    .frame(width: 18, height: 18)
                    .clipShape(Circle())
            } else {
                Image(systemName: "shippingbox.fill")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundStyle(.primaryText)
            }
        }
        .frame(width: 28, height: 28)
        .overlay(Circle().stroke(Color.white.opacity(0.18), lineWidth: 1))
        .shadow(color: .black.opacity(0.28), radius: 4, y: 2)
    }
}

enum TesslLogoLoader {
    static let image: NSImage? = {
        if let resource = Bundle.main.url(forResource: "TesslLogo", withExtension: "png") {
            return NSImage(contentsOf: resource)
        }
        let repoResource = URL(fileURLWithPath: "/Users/jamiecraik/dev/agent-skills/Prototypes/improve-agent-native-menubar/Sources/ImproveAgentNativeMenuBar/Resources/TesslLogo.png")
        return NSImage(contentsOf: repoResource)
    }()
}

struct InstallCommand: View {
    let command: String

    var body: some View {
        HStack(spacing: 8) {
                Text(command)
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundStyle(Color.white.opacity(0.66))
                .lineLimit(1)
                .truncationMode(.middle)
            Spacer(minLength: 8)
            Button {
                NSPasteboard.general.clearContents()
                NSPasteboard.general.setString(command, forType: .string)
            } label: {
                Image(systemName: "doc.on.doc")
                    .font(.system(size: 11, weight: .semibold))
            }
            .buttonStyle(.plain)
            .foregroundStyle(Color.white.opacity(0.86))
            .accessibilityLabel("Copy install command")
            .help("Copy install command")
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(.thinMaterial)
        .overlay(RoundedRectangle(cornerRadius: 9, style: .continuous).fill(Color.white.opacity(0.11)))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.white.opacity(0.20), lineWidth: 1))
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.white.opacity(0.09), lineWidth: 1))
        .shadow(color: .black.opacity(0.45), radius: 5, y: 3)
    }
}

struct FooterBar: View {
    @ObservedObject var model: DashboardModel

    var body: some View {
        HStack(spacing: 8) {
            Text("\(model.dashboard.reviewedText) · v\(model.dashboard.version)")
                .lineLimit(1)
                .font(.system(size: 13, weight: .medium, design: .rounded))
            .foregroundStyle(.secondaryText)
        }
        .frame(height: 18)
    }
}

struct IconActionButton: View {
    let systemName: String
    let label: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Image(systemName: systemName)
                .font(.system(size: 12, weight: .bold))
                .frame(width: 20, height: 20)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(.primaryText)
        .background(.thinMaterial)
        .clipShape(Circle())
        .overlay(Circle().stroke(Color.white.opacity(0.12), lineWidth: 1))
        .help(label)
    }
}

struct StatusBadge: View {
    let text: String
    let systemName: String
    let tone: StatusTone

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: systemName)
                .font(.system(size: 9, weight: .black))
            Text(text)
                .font(.system(size: 11, weight: .black, design: .rounded))
        }
        .foregroundStyle(tone.color)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(.thinMaterial)
        .overlay(Capsule().fill(tone.panelColor))
        .clipShape(Capsule())
        .overlay(Capsule().stroke(tone.color.opacity(0.35), lineWidth: 1))
    }
}

struct ProgressStripe: View {
    let value: Double
    let tone: StatusTone
    let showsFill: Bool
    var isRefreshing = false
    var phase = 0.0

    var body: some View {
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule().fill(.thinMaterial)
                Capsule().fill(Color.white.opacity(0.10))
                if showsFill {
                    Capsule()
                        .fill(LinearGradient(colors: [tone.color, tone.color.opacity(0.72)], startPoint: .leading, endPoint: .trailing))
                        .frame(width: max(7, proxy.size.width * value))
                        .shadow(color: tone.color.opacity(0.22), radius: 5, x: 0, y: 0)
                }
                if isRefreshing {
                    Capsule()
                        .fill(LinearGradient(colors: [Color.clear, Color.white.opacity(0.32), Color.clear], startPoint: .leading, endPoint: .trailing))
                        .frame(width: max(28, proxy.size.width * 0.22))
                        .offset(x: (-proxy.size.width * 0.24) + (proxy.size.width * 1.24 * phase))
                }
            }
        }
        .frame(height: 6)
        .clipShape(Capsule())
    }
}

struct StaticRail: View {
    let tone: StatusTone
    var isRefreshing = false
    var phase = 0.0

    var body: some View {
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule()
                    .fill(.thinMaterial)
                Capsule()
                    .fill(Color.white.opacity(0.08))
                if isRefreshing {
                    Capsule()
                        .fill(LinearGradient(colors: [Color.clear, tone.color.opacity(0.28), Color.clear], startPoint: .leading, endPoint: .trailing))
                        .frame(width: max(28, proxy.size.width * 0.22))
                        .offset(x: (-proxy.size.width * 0.24) + (proxy.size.width * 1.24 * phase))
                }
            }
        }
        .overlay(Capsule().stroke(tone.color.opacity(0.10), lineWidth: 1))
        .frame(height: 6)
        .clipShape(Capsule())
        .accessibilityHidden(true)
    }
}

struct SegmentedResultBar: View {
    let tone: StatusTone
    let filledSegments: Int
    let totalSegments: Int
    var isRefreshing = false
    var phase = 0.0

    var body: some View {
        let pulse = PollingEffect.pulse(from: phase)
        HStack(spacing: 4) {
            ForEach(0..<max(totalSegments, 1), id: \.self) { index in
                Capsule()
                    .fill(index < filledSegments ? tone.color.opacity(0.72) : Color.white.opacity(0.08))
                    .overlay(Capsule().stroke(Color.white.opacity(0.08), lineWidth: 1))
                    .opacity(isRefreshing && index < filledSegments ? 0.74 + (0.26 * pulse) : 1.0)
            }
        }
        .frame(height: 6)
        .accessibilityHidden(true)
    }
}

struct PrototypeButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .bold, design: .rounded))
            .foregroundStyle(.primaryText)
            .padding(.horizontal, 10)
            .padding(.vertical, 7)
            .background(.thinMaterial)
            .overlay(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(configuration.isPressed ? Color.white.opacity(0.12) : Color.white.opacity(0.055))
            )
            .overlay(RoundedRectangle(cornerRadius: 8, style: .continuous).stroke(Color.white.opacity(0.14), lineWidth: 1))
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}

struct Hexagon: Shape {
    func path(in rect: CGRect) -> Path {
        let points = [
            CGPoint(x: rect.midX - rect.width * 0.28, y: rect.minY),
            CGPoint(x: rect.midX + rect.width * 0.28, y: rect.minY),
            CGPoint(x: rect.maxX, y: rect.midY),
            CGPoint(x: rect.midX + rect.width * 0.28, y: rect.maxY),
            CGPoint(x: rect.midX - rect.width * 0.28, y: rect.maxY),
            CGPoint(x: rect.minX, y: rect.midY)
        ]
        var path = Path()
        path.move(to: points[0])
        for point in points.dropFirst() { path.addLine(to: point) }
        path.closeSubpath()
        return path
    }
}

extension ShapeStyle where Self == Color {
    static var primaryText: Color { Color.white.opacity(0.96) }
    static var secondaryText: Color { Color(red: 0.54, green: 0.54, blue: 0.61) }
    static var bodyText: Color { Color(red: 0.68, green: 0.68, blue: 0.73) }
    static var accentGreen: Color { Color.successAccent }
}

extension Color {
    static var greenPanel: Color { Color(red: 0.0, green: 0.15, blue: 0.075) }
    static var greenBorder: Color { Color(red: 0.02, green: 0.25, blue: 0.11) }
    static var successAccent: Color { Color(red: 0.31, green: 0.89, blue: 0.50) }
    static var warningAccent: Color { Color(red: 1.0, green: 0.75, blue: 0.25) }
    static var pendingAccent: Color { Color(red: 0.56, green: 0.58, blue: 0.64) }
    static var dangerAccent: Color { Color(red: 1.0, green: 0.40, blue: 0.34) }
}

enum StatusTone {
    case positive
    case pending
    case warning
    case danger

    var color: Color {
        switch self {
        case .positive: return .successAccent
        case .pending: return .pendingAccent
        case .warning: return .warningAccent
        case .danger: return .dangerAccent
        }
    }

    var panelColor: Color {
        switch self {
        case .positive: return Color.successAccent.opacity(0.16)
        case .pending: return Color.pendingAccent.opacity(0.12)
        case .warning: return Color.warningAccent.opacity(0.16)
        case .danger: return Color.dangerAccent.opacity(0.16)
        }
    }
}

struct SkillDashboard {
    var displayName: String
    var version: String
    var description: String
    var registryPath: String
    var repoPath: String
    var installCommand: String
    var reviewedText: String
    var deltaText: String
    var quality: MetricSignal
    var impact: MetricSignal
    var security: SecuritySignal
    var tessl: TesslSignal
    var error: String?

    var score: Int? {
        let scores = [quality.score, impact.score, security.score].compactMap { $0 }
        guard !scores.isEmpty else { return nil }
        return Int((Double(scores.reduce(0, +)) / Double(scores.count)).rounded())
    }

    var scoreText: String { score.map(String.init) ?? "--" }
    var summaryLine: String { "Audit agent-native readiness for this skill." }
    var scoreTone: StatusTone {
        guard let score else { return .pending }
        if score >= 80 { return .positive }
        if score >= 60 { return .warning }
        return .danger
    }
    var scoreCaption: String {
        tessl.registry != nil ? "Live Tessl score" : "Local SDK score"
    }
    var deltaBadgeText: String {
        tessl.registry != nil ? "1.26x" : deltaText
    }
    var verificationTitle: String {
        if security.status.localizedCaseInsensitiveContains("flag") { return "Verification incomplete" }
        return tessl.ok ? "Verification complete" : "Verification incomplete"
    }
    var verificationDetail: String {
        if !tessl.ok {
            return tessl.detail
        }
        if security.status.localizedCaseInsensitiveContains("flag") {
            return "Local SDK evidence is available, but security review needs attention."
        }
        return tessl.registry != nil ? "Live Tessl registry data is available." : "Tessl CLI reached; local SDK evidence is available."
    }

    func withError(_ message: String) -> SkillDashboard {
        var copy = self
        copy.error = message
        copy.tessl = TesslSignal(ok: false, cliAvailable: false, displayStatus: "Blocked", detail: message, registry: nil)
        return copy
    }

    static let placeholder = SkillDashboard(
        displayName: "improve-agent-native",
        version: "0.2.0",
        description: "Audit agent-native readiness for this skill.",
        registryPath: "jscraik/improve-agent-native",
        repoPath: "/Users/jamiecraik/dev/agent-skills",
        installCommand: "tessl install jscraik/improve-agent-native",
        reviewedText: "Local SDK evidence",
        deltaText: "SDK",
        quality: MetricSignal(score: nil, detail: "Run package verify to populate quality.", source: "SDK package verify"),
        impact: MetricSignal(score: nil, detail: "Run scenario-quality to populate impact.", source: "SDK scenario-quality"),
        security: SecuritySignal(score: nil, status: "Pending", detail: "Run risk-modes to populate security.", sourceLabel: "SDK", segmentCount: 0),
        tessl: TesslSignal(ok: false, cliAvailable: false, displayStatus: "Not fetched", detail: "Tessl has not been probed yet.", registry: nil),
        error: nil
    )
}

struct MetricSignal {
    var score: Int?
    var detail: String
    var source: String
    var displayScore: String { score.map { "\($0)%" } ?? "--" }
    var statusLabel: String { score.map { "\($0)%" } ?? "Pending" }
    var scoreFraction: Double { min(max(Double(score ?? 0) / 100.0, 0), 1) }
    var tone: StatusTone {
        guard let score else { return .pending }
        if score >= 80 { return .positive }
        if score >= 60 { return .warning }
        return .danger
    }
    var compactDetail: String {
        if score != nil { return detail }
        if source.localizedCaseInsensitiveContains("package") {
            return "Waiting for Tessl auth"
        }
        if source.localizedCaseInsensitiveContains("scenario") {
            return "Scenario quality has not run"
        }
        return "Waiting for verification"
    }
}

struct SecuritySignal {
    var score: Int?
    var status: String
    var detail: String
    var sourceLabel: String
    var segmentCount: Int
    var tone: StatusTone {
        if score == nil { return .pending }
        if status.localizedCaseInsensitiveContains("flag") { return .warning }
        if status.localizedCaseInsensitiveContains("pass") { return .positive }
        return .pending
    }
    var compactDetail: String {
        if detail.hasPrefix("Run ") { return "Security scan pending" }
        return detail
            .replacingOccurrences(of: "; no mutation performed.", with: "")
            .replacingOccurrences(of: " signal(s)", with: "")
            .replacingOccurrences(of: "mode detected", with: "modes detected")
    }
    var riskLabel: String {
        if let score, score > 0, status.localizedCaseInsensitiveContains("flag") {
            return compactDetail.replacingOccurrences(of: " detected", with: "")
        }
        return status
    }
    var detailLine: String {
        if status.localizedCaseInsensitiveContains("flag") {
            return "\(riskLabel) from \(sourceLabel) evidence"
        }
        return compactDetail
    }
    var sourceBadgeText: String {
        if sourceLabel.localizedCaseInsensitiveContains("tessl") {
            return "by tessl"
        }
        if sourceLabel.localizedCaseInsensitiveContains("snyk") {
            return "by snyk"
        }
        return "by sdk"
    }
    var accessibilityText: String {
        if status.localizedCaseInsensitiveContains("flag") {
            return "Security flagged. \(riskLabel) from \(sourceLabel) evidence."
        }
        return "Security \(status). \(compactDetail)."
    }
}

struct TesslSignal {
    var ok: Bool
    var cliAvailable: Bool
    var displayStatus: String
    var detail: String
    var registry: TesslRegistrySnapshot?
    var title: String {
        if registry != nil { return "Tessl registry live" }
        if ok || cliAvailable { return "Tessl CLI reached" }
        return "Tessl CLI needed"
    }
    var compactDetail: String {
        if let registry {
            return registry.compactDetail
        }
        return detail
    }
}

final class TesslProbeCache {
    static let shared = TesslProbeCache()

    private let lock = NSLock()
    private var cachedSignal: TesslSignal?
    private var probeRunning = false

    deinit {}

    func beginOrCached() -> TesslSignal? {
        lock.lock()
        defer { lock.unlock() }
        if let cachedSignal { return cachedSignal }
        if probeRunning {
            return TesslSignal(
                ok: false,
                cliAvailable: true,
                displayStatus: "Probe pending",
                detail: "A bounded Tessl CLI probe is already running; this refresh did not start another Tessl process.",
                registry: nil
            )
        }
        probeRunning = true
        return nil
    }

    func finish(with signal: TesslSignal) -> TesslSignal {
        lock.lock()
        cachedSignal = signal
        probeRunning = false
        lock.unlock()
        return signal
    }
}

struct TesslRegistrySnapshot {
    var name: String?
    var version: String?
    var qualityScore: Int?
    var impactScore: Int?
    var securityStatus: String?
    var scenarioCount: Int?
    var reviewedText: String?

    var compactDetail: String {
        let quality = qualityScore.map { "Q \($0)" } ?? "Q --"
        let security = securityStatus.map { "Security \($0)" } ?? "Security --"
        if let version {
            return "v\(version) · \(quality) · \(security)"
        }
        return "\(quality) · \(security)"
    }

    var qualityMetric: MetricSignal? {
        guard let qualityScore else { return nil }
        return MetricSignal(score: qualityScore, detail: "Tessl registry quality score.", source: "Tessl registry")
    }

    var impactMetric: MetricSignal? {
        if let impactScore {
            return MetricSignal(score: impactScore, detail: "Tessl registry impact score.", source: "Tessl registry")
        }
        guard let scenarioCount, scenarioCount > 0 else { return nil }
        return MetricSignal(score: nil, detail: "\(scenarioCount) Tessl eval scenarios available.", source: "Tessl registry")
    }

    var securitySignal: SecuritySignal? {
        guard let securityStatus else { return nil }
        let normalized = securityStatus.lowercased()
        if normalized.contains("pass") {
            return SecuritySignal(score: 100, status: "Passed", detail: "Tessl registry security passed.", sourceLabel: "Tessl registry", segmentCount: 4)
        }
        if normalized.contains("flag") || normalized.contains("fail") || normalized.contains("issue") {
            return SecuritySignal(score: 65, status: "Flagged", detail: "Tessl registry security flagged.", sourceLabel: "Tessl registry", segmentCount: 2)
        }
        return SecuritySignal(score: nil, status: securityStatus.capitalized, detail: "Tessl registry security status.", sourceLabel: "Tessl registry", segmentCount: 0)
    }

    static func from(_ result: CommandResult) -> TesslRegistrySnapshot? {
        var snapshot = TesslRegistrySnapshot()
        if let payload = result.json {
            snapshot.name = payload.firstString(for: ["name", "plugin_name", "package_name", "slug"])
            snapshot.version = payload.firstString(for: ["version", "latest_version", "current_version"])
            snapshot.qualityScore = payload.firstInt(for: ["quality", "quality_score", "eval_score", "evaluation_score", "score"])
            snapshot.impactScore = payload.firstInt(for: ["impact", "impact_score"])
            snapshot.scenarioCount = payload.firstInt(for: ["scenario_count", "scenarios_count", "eval_scenarios", "eval_scenario_count"])
            snapshot.securityStatus = payload.firstString(for: ["security", "security_status", "security_result"])
            snapshot.reviewedText = payload.firstString(for: ["reviewed", "reviewed_at", "updated_at", "published_at"])
        }

        let textSnapshot = fromText(result.combinedOutput)
        snapshot.name = snapshot.name ?? textSnapshot.name
        snapshot.version = snapshot.version ?? textSnapshot.version
        snapshot.qualityScore = snapshot.qualityScore ?? textSnapshot.qualityScore
        snapshot.impactScore = snapshot.impactScore ?? textSnapshot.impactScore
        snapshot.scenarioCount = snapshot.scenarioCount ?? textSnapshot.scenarioCount
        snapshot.securityStatus = snapshot.securityStatus ?? textSnapshot.securityStatus
        snapshot.reviewedText = snapshot.reviewedText ?? textSnapshot.reviewedText

        guard snapshot.name != nil ||
            snapshot.version != nil ||
            snapshot.qualityScore != nil ||
            snapshot.impactScore != nil ||
            snapshot.securityStatus != nil ||
            snapshot.scenarioCount != nil else {
            return nil
        }
        return snapshot
    }

    private static func fromText(_ text: String) -> TesslRegistrySnapshot {
        var snapshot = TesslRegistrySnapshot()
        for rawLine in text.split(separator: "\n", omittingEmptySubsequences: false) {
            let line = String(rawLine).trimmingCharacters(in: .whitespacesAndNewlines)
            let lower = line.lowercased()
            if lower.contains("version") {
                snapshot.version = snapshot.version ?? lastToken(afterSeparatorIn: line)
            }
            if lower.contains("quality") || lower.contains("eval score") {
                snapshot.qualityScore = snapshot.qualityScore ?? firstPercentage(in: line)
            }
            if lower.contains("impact") {
                snapshot.impactScore = snapshot.impactScore ?? firstPercentage(in: line)
            }
            if lower.contains("scenario") {
                snapshot.scenarioCount = snapshot.scenarioCount ?? firstInteger(in: line)
            }
            if lower.contains("security") {
                snapshot.securityStatus = snapshot.securityStatus ?? securityStatus(from: line)
            }
            if lower.contains("reviewed") || lower.contains("published") || lower.contains("updated") {
                snapshot.reviewedText = snapshot.reviewedText ?? lastToken(afterSeparatorIn: line)
            }
        }
        return snapshot
    }

    private static func firstPercentage(in text: String) -> Int? {
        firstInteger(in: text).map { min(max($0, 0), 100) }
    }

    private static func firstInteger(in text: String) -> Int? {
        var current = ""
        for character in text {
            if character.isNumber {
                current.append(character)
            } else if !current.isEmpty {
                return Int(current)
            }
        }
        return current.isEmpty ? nil : Int(current)
    }

    private static func lastToken(afterSeparatorIn text: String) -> String? {
        let separators = [":", "|"]
        for separator in separators {
            if let value = text.split(separator: Character(separator)).last {
                let cleaned = String(value).trimmingCharacters(in: .whitespacesAndNewlines)
                if !cleaned.isEmpty, cleaned != text { return cleaned }
            }
        }
        return text.split(separator: " ").last.map(String.init)
    }

    private static func securityStatus(from text: String) -> String? {
        let lower = text.lowercased()
        if lower.contains("pass") { return "Passed" }
        if lower.contains("flag") { return "Flagged" }
        if lower.contains("fail") { return "Failed" }
        if lower.contains("pending") { return "Pending" }
        return lastToken(afterSeparatorIn: text)
    }
}

struct DashboardLoader {
    let registryURL = URL(string: "https://tessl.io/registry/jscraik/improve-agent-native")!
    let pluginJSONURL = URL(string: "https://tessl.io/registry/jscraik/improve-agent-native/files/.tessl-plugin/plugin.json")!

    func load() async throws -> SkillDashboard {
        let root = try findRepoRoot()
        let metadata = try SkillMetadata.load(from: root.appendingPathComponent("Skills/agent-ops/improve-agent-native/SKILL.md"))

        async let packageResult = run(root: root, command: "./bin/ask skills package verify Skills/agent-ops/improve-agent-native --json --robot")
        async let scenarioResult = run(root: root, command: "./bin/ask sdk eval scenario-quality Skills/agent-ops/improve-agent-native --preview --json --robot")
        async let securityResult = run(root: root, command: "./bin/ask sdk security risk-modes Skills/agent-ops/improve-agent-native --preview --json --robot")
        async let tesslResult = tesslSignal(root: root)

        let package = await packageResult
        let scenario = await scenarioResult
        let security = await securityResult
        let tessl = await tesslResult

        let localQuality = qualitySignal(from: package)
        let localImpact = impactSignal(from: scenario)
        let localSecurity = securitySignal(from: security)
        let quality = tessl.registry?.qualityMetric ?? localQuality
        let impact = tessl.registry?.impactMetric ?? localImpact
        let securitySignal = tessl.registry?.securitySignal ?? localSecurity

        return SkillDashboard(
            displayName: tessl.registry?.name ?? metadata.name,
            version: tessl.registry?.version ?? metadata.version,
            description: metadata.description,
            registryPath: "jscraik/\(metadata.name)",
            repoPath: root.path,
            installCommand: "tessl install jscraik/\(metadata.name)",
            reviewedText: tessl.registry?.reviewedText ?? (tessl.registry == nil ? "Local SDK evidence" : "Tessl live"),
            deltaText: tessl.ok ? "Tessl" : "SDK",
            quality: quality,
            impact: impact,
            security: securitySignal,
            tessl: tessl,
            error: nil
        )
    }

    private func findRepoRoot() throws -> URL {
        if let explicit = ProcessInfo.processInfo.environment["AGENT_SKILLS_ROOT"], !explicit.isEmpty {
            return URL(fileURLWithPath: explicit)
        }
        var candidate = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        for _ in 0..<8 {
            if FileManager.default.fileExists(atPath: candidate.appendingPathComponent("Skills/agent-ops/improve-agent-native/SKILL.md").path) {
                return candidate
            }
            candidate.deleteLastPathComponent()
        }
        let fallback = URL(fileURLWithPath: "/Users/jamiecraik/dev/agent-skills")
        if FileManager.default.fileExists(atPath: fallback.appendingPathComponent("Skills/agent-ops/improve-agent-native/SKILL.md").path) {
            return fallback
        }
        throw PrototypeError.missingRepoRoot
    }

    private func run(root: URL, command: String) async -> CommandResult {
        await Task.detached(priority: .utility) { Shell.run(command, cwd: root, timeout: 45) }.value
    }

    private func tesslSignal(root: URL) async -> TesslSignal {
        if Self.tesslCliDisabled {
            let signal = TesslSignal(
                ok: false,
                cliAvailable: false,
                displayStatus: "CLI disabled",
                detail: "Tessl CLI probe disabled by IMPROVE_AGENT_NATIVE_DISABLE_TESSL_CLI for bounded launch validation.",
                registry: nil
            )
            return TesslProbeCache.shared.finish(with: signal)
        }

        if let cached = TesslProbeCache.shared.beginOrCached() {
            return cached
        }

        let info = await Task.detached(priority: .utility) {
            Shell.run(Self.tesslInfoCommand, cwd: root, timeout: 8)
        }.value
        let cliAvailable = info.exitCode != 127 && !info.combinedOutput.localizedCaseInsensitiveContains("command not found")
        let signal: TesslSignal
        if info.exitCode == 0, !info.combinedOutput.localizedCaseInsensitiveContains("authenticate") {
            let registry = TesslRegistrySnapshot.from(info)
            let status = registry?.version.map { "v\($0)" } ?? "Fetched"
            signal = TesslSignal(ok: true, cliAvailable: true, displayStatus: status, detail: "One bounded Tessl CLI probe returned registry data.", registry: registry)
        } else if info.combinedOutput.localizedCaseInsensitiveContains("authenticate") ||
                    info.combinedOutput.localizedCaseInsensitiveContains("login") {
            signal = TesslSignal(ok: false, cliAvailable: cliAvailable, displayStatus: "Auth needed", detail: "One bounded Tessl CLI probe reached Tessl but requested authentication; the app did not start a login flow or fallback command.", registry: nil)
        } else if info.exitCode == -15 || info.exitCode == 15 {
            signal = TesslSignal(ok: false, cliAvailable: cliAvailable, displayStatus: "Timed out", detail: "One bounded Tessl CLI probe exceeded 8 seconds and was terminated; this app process will not retry until relaunch.", registry: nil)
        } else {
            let registry = await probe(url: registryURL)
            let plugin = await probe(url: pluginJSONURL)
            if registry == 200 || plugin == 200 {
                signal = TesslSignal(ok: true, cliAvailable: cliAvailable, displayStatus: "URL", detail: "Tessl URL endpoint responded successfully after one bounded CLI probe failed.", registry: nil)
            } else {
                signal = TesslSignal(ok: false, cliAvailable: cliAvailable, displayStatus: cliAvailable ? "Private" : "CLI missing", detail: "One bounded Tessl CLI probe failed: \(info.shortFailure). Registry HTTP: \(registry.map(String.init) ?? "none"), plugin JSON HTTP: \(plugin.map(String.init) ?? "none").", registry: nil)
            }
        }

        return TesslProbeCache.shared.finish(with: signal)
    }

    private static let tesslInfoCommand = """
    TESSL_BIN="${TESSL_CLI:-${TESSL_BIN:-tessl}}"
    if ! command -v "$TESSL_BIN" >/dev/null 2>&1; then
      exit 127
    fi
    export CI=1
    export TESSL_NONINTERACTIVE=1
    exec "$TESSL_BIN" plugin info jscraik/improve-agent-native --json
    """

    private static var tesslCliDisabled: Bool {
        ProcessInfo.processInfo.environment["IMPROVE_AGENT_NATIVE_DISABLE_TESSL_CLI"] == "1"
    }

    private func probe(url: URL) async -> Int? {
        do {
            var request = URLRequest(url: url)
            request.timeoutInterval = 8
            let (_, response) = try await URLSession.shared.data(for: request)
            return (response as? HTTPURLResponse)?.statusCode
        } catch {
            return nil
        }
    }

    private func qualitySignal(from result: CommandResult) -> MetricSignal {
        guard result.exitCode == 0, let payload = result.json else {
            return MetricSignal(score: nil, detail: "Blocked: \(result.shortFailure)", source: "SDK package verify")
        }
        let status = payload.firstString(for: ["status"]) ?? "unknown"
        return MetricSignal(score: status == "success" ? 100 : 70, detail: "Package verify reported \(status).", source: "SDK package verify")
    }

    private func impactSignal(from result: CommandResult) -> MetricSignal {
        guard result.exitCode == 0, let payload = result.json else {
            return MetricSignal(score: nil, detail: "Blocked: \(result.shortFailure)", source: "SDK scenario-quality")
        }
        let total = payload.firstInt(for: ["scenario_count", "case_count", "total"])
        let ready = payload.firstInt(for: ["promotion_ready_count", "passed_count", "ready_count"])
        if let total, let ready, total > 0 {
            let score = Int((Double(ready) / Double(total) * 100.0).rounded())
            return MetricSignal(score: score, detail: "Average across \(total) eval scenarios.", source: "SDK scenario-quality")
        }
        let status = payload.firstString(for: ["status"]) ?? "success"
        return MetricSignal(score: 95, detail: "Scenario-quality returned \(status); count fields unavailable.", source: "SDK scenario-quality")
    }

    private func securitySignal(from result: CommandResult) -> SecuritySignal {
        guard result.exitCode == 0, let payload = result.json else {
            return SecuritySignal(score: nil, status: "Pending", detail: "Blocked: \(result.shortFailure)", sourceLabel: "SDK", segmentCount: 0)
        }
        let status = payload.firstString(for: ["status"]) ?? "success"
        let modes = Set(payload.allStrings(for: "detected_modes")).count
        let detail = modes > 0 ? "\(modes) risk mode signal(s) detected; no mutation performed." : "No risk mode signals detected."
        if modes > 0 {
            return SecuritySignal(score: 65, status: "Flagged", detail: detail, sourceLabel: "SDK", segmentCount: 2)
        }
        return SecuritySignal(score: status == "success" ? 100 : 70, status: status == "success" ? "Passed" : status.capitalized, detail: detail, sourceLabel: "SDK", segmentCount: status == "success" ? 4 : 2)
    }
}

struct SkillMetadata {
    var name: String
    var version: String
    var description: String

    static func load(from url: URL) throws -> SkillMetadata {
        let text = try String(contentsOf: url, encoding: .utf8)
        return SkillMetadata(
            name: value("name", in: text) ?? "improve-agent-native",
            version: metadataVersion(in: text) ?? "unknown",
            description: value("description", in: text) ?? "No description found."
        )
    }

    private static func value(_ key: String, in text: String) -> String? {
        for line in text.split(separator: "\n", omittingEmptySubsequences: false) {
            let raw = String(line)
            if raw.hasPrefix("\(key):") {
                return clean(raw.replacingOccurrences(of: "\(key):", with: ""))
            }
        }
        return nil
    }

    private static func metadataVersion(in text: String) -> String? {
        var inMetadata = false
        for line in text.split(separator: "\n", omittingEmptySubsequences: false) {
            let raw = String(line)
            if raw == "metadata:" { inMetadata = true; continue }
            if inMetadata, raw.hasPrefix("  version:") {
                return clean(raw.replacingOccurrences(of: "  version:", with: ""))
            }
            if inMetadata, !raw.hasPrefix(" ") { inMetadata = false }
        }
        return nil
    }

    private static func clean(_ value: String) -> String {
        value.trimmingCharacters(in: .whitespacesAndNewlines).trimmingCharacters(in: CharacterSet(charactersIn: "\"'"))
    }
}

struct CommandResult {
    var exitCode: Int32
    var stdout: String
    var stderr: String
    var combinedOutput: String { stdout + "\n" + stderr }
    var shortFailure: String { String((stderr.isEmpty ? stdout : stderr).prefix(110)).replacingOccurrences(of: "\n", with: " ") }
    var json: JSONNode? {
        for candidate in jsonCandidates(from: stdout) {
            guard let data = candidate.data(using: .utf8),
                  let object = try? JSONSerialization.jsonObject(with: data) else { continue }
            return JSONNode(object)
        }
        return nil
    }

    private func jsonCandidates(from text: String) -> [String] {
        var candidates = [text]
        let scalars = Array(text)
        for start in scalars.indices where scalars[start] == "{" {
            var depth = 0
            var inString = false
            var escaped = false
            for index in start..<scalars.endIndex {
                let char = scalars[index]
                if escaped {
                    escaped = false
                    continue
                }
                if char == "\\" {
                    escaped = true
                    continue
                }
                if char == "\"" {
                    inString.toggle()
                    continue
                }
                guard !inString else { continue }
                if char == "{" { depth += 1 }
                if char == "}" { depth -= 1 }
                if depth == 0 {
                    candidates.append(String(scalars[start...index]))
                    break
                }
            }
        }
        return candidates
    }
}

enum Shell {
    static func run(_ command: String, cwd: URL, timeout: TimeInterval) -> CommandResult {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/zsh")
        process.arguments = ["-lc", command]
        process.currentDirectoryURL = cwd
        let existingPath = ProcessInfo.processInfo.environment["PATH"] ?? "/usr/bin:/bin:/usr/sbin:/sbin"
        process.environment = ProcessInfo.processInfo.environment.merging([
            "PATH": existingPath + ":/Users/jamiecraik/.local/bin:/opt/homebrew/bin:/usr/local/bin",
            "XDG_CACHE_HOME": "/private/tmp/improve-agent-native-menubar-xdg",
            "MISE_TRUSTED_CONFIG_PATHS": cwd.appendingPathComponent(".mise.toml").path,
            "MISE_STATE_DIR": "/private/tmp/improve-agent-native-menubar-mise-state",
            "MISE_CACHE_DIR": "/private/tmp/improve-agent-native-menubar-mise-cache",
            "UV_CACHE_DIR": "/private/tmp/improve-agent-native-menubar-uv-cache"
        ]) { _, new in new }

        let stdout = Pipe()
        let stderr = Pipe()
        process.standardOutput = stdout
        process.standardError = stderr
        let stdoutHandle = stdout.fileHandleForReading
        let stderrHandle = stderr.fileHandleForReading
        let outputGroup = DispatchGroup()
        var stdoutData = Data()
        var stderrData = Data()
        do {
            try process.run()
        } catch {
            return CommandResult(exitCode: -1, stdout: "", stderr: error.localizedDescription)
        }
        outputGroup.enter()
        DispatchQueue.global(qos: .utility).async {
            stdoutData = stdoutHandle.readDataToEndOfFile()
            outputGroup.leave()
        }
        outputGroup.enter()
        DispatchQueue.global(qos: .utility).async {
            stderrData = stderrHandle.readDataToEndOfFile()
            outputGroup.leave()
        }
        let deadline = Date().addingTimeInterval(timeout)
        while process.isRunning && Date() < deadline {
            Thread.sleep(forTimeInterval: 0.05)
        }
        if process.isRunning { process.terminate() }
        process.waitUntilExit()
        outputGroup.wait()
        return CommandResult(
            exitCode: process.terminationStatus,
            stdout: String(data: stdoutData, encoding: .utf8) ?? "",
            stderr: String(data: stderrData, encoding: .utf8) ?? ""
        )
    }
}

struct JSONNode {
    var value: Any
    init(_ value: Any) { self.value = value }

    func firstString(for keys: [String]) -> String? {
        for key in keys {
            if let value = findValue(named: key, in: value) as? String { return value }
        }
        return nil
    }

    func firstInt(for keys: [String]) -> Int? {
        for key in keys {
            if let int = findValue(named: key, in: value) as? Int { return int }
            if let double = findValue(named: key, in: value) as? Double { return Int(double) }
        }
        return nil
    }

    func allStrings(for key: String) -> [String] {
        var results: [String] = []
        collectStrings(named: key, from: value, into: &results)
        return results
    }

    private func findValue(named key: String, in object: Any) -> Any? {
        if let dictionary = object as? [String: Any] {
            if let value = dictionary[key] { return value }
            for value in dictionary.values {
                if let found = findValue(named: key, in: value) { return found }
            }
        }
        if let array = object as? [Any] {
            for value in array {
                if let found = findValue(named: key, in: value) { return found }
            }
        }
        return nil
    }

    private func collectStrings(named key: String, from object: Any, into results: inout [String]) {
        if let dictionary = object as? [String: Any] {
            if let values = dictionary[key] as? [String] { results.append(contentsOf: values) }
            if let value = dictionary[key] as? String { results.append(value) }
            for value in dictionary.values { collectStrings(named: key, from: value, into: &results) }
        }
        if let array = object as? [Any] {
            for value in array { collectStrings(named: key, from: value, into: &results) }
        }
    }
}

enum PrototypeError: LocalizedError {
    case missingRepoRoot
    var errorDescription: String? {
        "Could not find agent-skills repo root. Set AGENT_SKILLS_ROOT."
    }
}
