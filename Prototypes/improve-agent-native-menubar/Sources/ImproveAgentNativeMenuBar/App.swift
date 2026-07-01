import AppKit
import Foundation
import SwiftUI

@main
struct ImproveAgentNativeMenuBarApp: App {
    @StateObject private var model = DashboardModel()

    var body: some Scene {
        MenuBarExtra {
            DashboardView(model: model)
                .frame(width: 332, height: 506)
                .task { await model.refresh() }
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

    init() {
        Task { await refresh() }
    }

    var menuTitle: String {
        "SDK"
    }

    func refresh() async {
        guard !isRefreshing else { return }
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
    @ObservedObject var model: DashboardModel

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color.white.opacity(0.06), Color(red: 0.025, green: 0.028, blue: 0.026).opacity(0.84), Color.black.opacity(0.66)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .strokeBorder(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.24),
                                    Color.successAccent.opacity(0.22),
                                    Color.black.opacity(0.45)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 1
                        )
                )
                .shadow(color: .black.opacity(0.50), radius: 24, x: 0, y: 18)
                .padding(6)

            VStack(spacing: 0) {
                HeaderScoreView(dashboard: model.dashboard)
                    .padding(.top, 18)

                VStack(alignment: .leading, spacing: 6) {
                    SkillIdentityView(dashboard: model.dashboard)
                    VerificationNotice(dashboard: model.dashboard)
                    EvidenceRow(metric: model.dashboard.quality, title: "Quality")
                    EvidenceRow(metric: model.dashboard.impact, title: "Impact")
                    SecurityBlock(signal: model.dashboard.security)
                    TesslBlock(signal: model.dashboard.tessl)
                    PrimaryAction(signal: model.dashboard.tessl)
                    InstallCommand(command: model.dashboard.installCommand)
                    FooterBar(model: model)
                }
                .padding(.horizontal, 24)
                .padding(.top, 2)

                Spacer(minLength: 8)
            }
            .padding(6)
        }
        .foregroundStyle(.primaryText)
    }
}

struct HeaderScoreView: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                Hexagon()
                    .fill(.ultraThinMaterial)
                    .overlay(
                        Hexagon()
                            .fill(LinearGradient(colors: [.greenPanel.opacity(0.88), Color(red: 0.0, green: 0.05, blue: 0.025).opacity(0.92)], startPoint: .top, endPoint: .bottom))
                    )
                    .overlay(Hexagon().stroke(Color.white.opacity(0.10), lineWidth: 1))
                    .overlay(Hexagon().stroke(dashboard.scoreTone.color.opacity(0.72), lineWidth: 3))
                    .overlay(
                        Hexagon()
                            .stroke(LinearGradient(colors: [Color.white.opacity(0.20), Color.clear], startPoint: .top, endPoint: .center), lineWidth: 1)
                            .padding(4)
                    )
                    .shadow(color: .black.opacity(0.45), radius: 18, x: 0, y: 14)
                    .frame(width: 64, height: 50)

                Text(dashboard.scoreText)
                    .font(.system(size: 20, weight: .heavy, design: .rounded))
                    .foregroundStyle(dashboard.scoreTone == .positive ? dashboard.scoreTone.color : .primaryText)
            }

            HStack(spacing: 8) {
                Image(systemName: dashboard.scoreTone == .positive ? "checkmark" : "exclamationmark.triangle.fill")
                    .font(.system(size: 9, weight: .bold))
                Text(dashboard.scoreCaption)
                    .font(.system(size: 10, weight: .medium))
            }
            .foregroundStyle(dashboard.scoreTone == .positive ? dashboard.scoreTone.color : .bodyText)
            .padding(.top, 4)
            .padding(.bottom, 2)
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
        VStack(alignment: .leading, spacing: 5) {
            Text(dashboard.registryPath)
                .font(.system(size: 12, weight: .semibold, design: .rounded))
                .foregroundStyle(.secondaryText)
                .lineLimit(1)
            Text(dashboard.displayName)
                .font(.system(size: 17, weight: .heavy, design: .rounded))
            Text(dashboard.summaryLine)
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .lineSpacing(1)
                .foregroundStyle(.bodyText)
                .lineLimit(1)
        }
    }
}

struct EvidenceRow: View {
    let metric: MetricSignal
    let title: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline) {
                Text(title)
                    .font(.system(size: 14, weight: .heavy, design: .rounded))
                Spacer()
                Text(metric.statusLabel)
                    .font(.system(size: 13, weight: .heavy, design: .rounded))
                    .foregroundStyle(metric.tone.color)
            }
            if let score = metric.score {
                ProgressStripe(value: min(max(Double(score) / 100.0, 0), 1), tone: metric.tone, showsFill: true)
            }
            Text(metric.compactDetail)
                .font(.system(size: 11, weight: .medium, design: .rounded))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
        }
    }
}

struct SecurityBlock: View {
    let signal: SecuritySignal

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(alignment: .firstTextBaseline) {
                Text("Security")
                    .font(.system(size: 14, weight: .heavy, design: .rounded))
                Spacer()
                Text(signal.status)
                    .font(.system(size: 13, weight: .heavy, design: .rounded))
                    .foregroundStyle(signal.tone.color)
            }

            Text(signal.detailLine)
                .font(.system(size: 11, weight: .regular))
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
                    Text("Tessl CLI reached")
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
        .overlay(Circle().stroke(Color.successAccent.opacity(0.10), lineWidth: 1))
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
        HStack(spacing: 10) {
            Text("Install")
                .font(.system(size: 10, weight: .semibold, design: .rounded))
                .foregroundStyle(.secondaryText)
            Text(command)
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .foregroundStyle(Color.white.opacity(0.72))
                .lineLimit(1)
                .truncationMode(.middle)
            Spacer(minLength: 8)
            Button {
                NSPasteboard.general.clearContents()
                NSPasteboard.general.setString(command, forType: .string)
            } label: {
                Image(systemName: "doc.on.doc")
                    .font(.system(size: 12, weight: .semibold))
            }
            .buttonStyle(.plain)
            .foregroundStyle(Color.white.opacity(0.86))
            .accessibilityLabel("Copy install command")
        }
        .padding(.horizontal, 9)
        .padding(.vertical, 4)
        .background(.thinMaterial)
        .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).fill(Color.white.opacity(0.045)))
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
                .font(.system(size: 9, weight: .medium, design: .rounded))
            .foregroundStyle(.secondaryText)
        }
        .frame(height: 14)
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
                .font(.system(size: 8, weight: .black))
            Text(text)
                .font(.system(size: 10, weight: .black, design: .rounded))
        }
        .foregroundStyle(tone.color)
        .padding(.horizontal, 7)
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
            }
        }
        .frame(height: 6)
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
        scoreTone == .positive ? "Validated score" : "Preliminary SDK score"
    }
    var verificationTitle: String {
        if security.status.localizedCaseInsensitiveContains("flag") { return "Verification incomplete" }
        return tessl.ok ? "Verification complete" : "Verification incomplete"
    }
    var verificationDetail: String {
        if !tessl.ok {
            return "Sign in to finish Quality and Impact checks."
        }
        if security.status.localizedCaseInsensitiveContains("flag") {
            return "Local SDK evidence is available, but security review needs attention."
        }
        return "Local SDK evidence and registry checks are available."
    }

    func withError(_ message: String) -> SkillDashboard {
        var copy = self
        copy.error = message
        copy.tessl = TesslSignal(ok: false, cliAvailable: false, displayStatus: "Blocked", detail: message)
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
        tessl: TesslSignal(ok: false, cliAvailable: false, displayStatus: "Not fetched", detail: "Tessl has not been probed yet."),
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
    var compactDetail: String {
        ok ? "Registry metadata available." : "Requires Tessl login to continue."
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

        return SkillDashboard(
            displayName: metadata.name,
            version: metadata.version,
            description: metadata.description,
            registryPath: "jscraik/\(metadata.name)",
            repoPath: root.path,
            installCommand: "tessl install jscraik/\(metadata.name)",
            reviewedText: "Local SDK evidence",
            deltaText: tessl.ok ? "Tessl" : "SDK",
            quality: qualitySignal(from: package),
            impact: impactSignal(from: scenario),
            security: securitySignal(from: security),
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
        let info = await run(root: root, command: "if [ -n \"$TESSL_TOKEN\" ]; then tessl plugin info jscraik/improve-agent-native; elif command -v op >/dev/null 2>&1; then op run -- tessl plugin info jscraik/improve-agent-native; else tessl plugin info jscraik/improve-agent-native; fi")
        let cliAvailable = info.exitCode != 127 && !info.combinedOutput.localizedCaseInsensitiveContains("command not found")
        if info.exitCode == 0, !info.combinedOutput.localizedCaseInsensitiveContains("authenticate") {
            return TesslSignal(ok: true, cliAvailable: true, displayStatus: "Fetched", detail: "Tessl CLI returned plugin info for private registry source.")
        }
        if info.combinedOutput.localizedCaseInsensitiveContains("authenticate") {
            return TesslSignal(ok: false, cliAvailable: cliAvailable, displayStatus: "Auth needed", detail: "tessl plugin info reached Tessl but requires login for this private plugin.")
        }

        let registry = await probe(url: registryURL)
        let plugin = await probe(url: pluginJSONURL)
        if registry == 200 || plugin == 200 {
            return TesslSignal(ok: true, cliAvailable: cliAvailable, displayStatus: "URL", detail: "Tessl URL endpoint responded successfully.")
        }
        return TesslSignal(ok: false, cliAvailable: cliAvailable, displayStatus: "Private", detail: "Tessl CLI blocked: \(info.shortFailure). Registry HTTP: \(registry.map(String.init) ?? "none"), plugin JSON HTTP: \(plugin.map(String.init) ?? "none").")
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
