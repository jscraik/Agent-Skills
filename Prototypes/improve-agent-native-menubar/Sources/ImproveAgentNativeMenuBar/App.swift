import AppKit
import Foundation
import SwiftUI

enum MenuBarTemplateMetrics {
    static let width: CGFloat = 356
    static let height: CGFloat = 560
}

@main
struct ImproveAgentNativeMenuBarApp: App {
    @StateObject private var model = DashboardModel()

    init() {
        if let outputPath = SnapshotRequest.outputPath {
            SnapshotRenderer.render(to: URL(fileURLWithPath: outputPath))
            Foundation.exit(0)
        }
    }

    var body: some Scene {
        MenuBarExtra {
            DashboardView(model: model)
                .frame(width: MenuBarTemplateMetrics.width, height: MenuBarTemplateMetrics.height)
                .task { await model.refresh() }
        } label: {
            SkillsMenuBarIconView()
                .accessibilityLabel(model.menuTitle)
        }
        .menuBarExtraStyle(.window)
    }
}

struct SkillsMenuBarIconView: View {
    var body: some View {
        Group {
            if let image = SkillsSDKIconLoader.menuBarImage {
                Image(nsImage: image)
                    .resizable()
                    .interpolation(.high)
                    .scaledToFit()
            } else {
                Image(systemName: "doc.text.magnifyingglass")
                    .resizable()
                    .scaledToFit()
                    .foregroundStyle(.primary)
            }
        }
        .frame(width: 23, height: 23)
        .frame(width: 23, height: 23, alignment: .center)
        .contentShape(Rectangle())
    }
}

@MainActor
final class DashboardModel: ObservableObject {
    @Published var dashboard = SkillDashboard.placeholder
    @Published var isRefreshing = false
    private let refreshIntervalNanoseconds: UInt64 = 5 * 60 * 1_000_000_000
    private var refreshLoopTask: Task<Void, Never>?

    init(dashboard: SkillDashboard = .placeholder, autorefresh: Bool = true) {
        self.dashboard = dashboard
        if autorefresh {
            Task { await refresh() }
            startRefreshLoop()
        }
    }

    deinit {
        refreshLoopTask?.cancel()
    }

    var menuTitle: String {
        return "Skills SDK"
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

    private func startRefreshLoop() {
        refreshLoopTask?.cancel()
        refreshLoopTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: self?.refreshIntervalNanoseconds ?? 300_000_000_000)
                guard !Task.isCancelled else { return }
                await self?.refresh()
            }
        }
    }
}

@MainActor
final class CopyFeedbackModel: ObservableObject {
    static let shared = CopyFeedbackModel()
    @Published var copiedCommand: String?

    func copy(_ command: String) {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(command, forType: .string)
        copiedCommand = command
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { [weak self] in
            guard self?.copiedCommand == command else { return }
            self?.copiedCommand = nil
        }
    }
}

enum SnapshotRequest {
    static var outputPath: String? {
        let args = CommandLine.arguments
        guard let index = args.firstIndex(of: "--snapshot"), args.indices.contains(index + 1) else {
            return nil
        }
        return args[index + 1]
    }
}

enum SnapshotRenderer {
    @MainActor
    static func render(to outputURL: URL) {
        do {
            let dashboard = try DashboardLoader().loadSync()
            let model = DashboardModel(dashboard: dashboard, autorefresh: false)
            let view = DashboardView(model: model)
                .frame(width: MenuBarTemplateMetrics.width, height: MenuBarTemplateMetrics.height)
                .background(Color.black)
            let renderer = ImageRenderer(content: view)
            renderer.scale = 2
            guard let image = renderer.cgImage else {
                throw SnapshotError.bitmapUnavailable
            }
            let bitmap = NSBitmapImageRep(cgImage: image)
            guard let data = bitmap.representation(using: .png, properties: [:]) else {
                throw SnapshotError.pngUnavailable
            }
            try data.write(to: outputURL)
            print("Wrote snapshot \(outputURL.path)")
        } catch {
            fputs("Snapshot failed: \(error.localizedDescription)\n", stderr)
            Foundation.exit(1)
        }
    }
}

enum SnapshotError: LocalizedError {
    case bitmapUnavailable
    case pngUnavailable

    var errorDescription: String? {
        switch self {
        case .bitmapUnavailable: return "Could not allocate snapshot bitmap."
        case .pngUnavailable: return "Could not encode snapshot PNG."
        }
    }
}

struct DashboardView: View {
    @ObservedObject var model: DashboardModel

    var body: some View {
        ZStack {
            PopoverInteriorBackdrop()

            VStack(spacing: 0) {
                HeaderScoreView(dashboard: model.dashboard)
                    .padding(.top, 18)

                VStack(alignment: .leading, spacing: 7) {
                    SkillIdentityView(dashboard: model.dashboard)
                    ProofLaneComparisonView(dashboard: model.dashboard)
                    FleetSummaryView(fleet: model.dashboard.fleet)
                    LocalChecksPanel(dashboard: model.dashboard)
                    SecurityBlock(signal: model.dashboard.security)
                    SectionLabel("Action")
                    CommandDock(dashboard: model.dashboard)
                }
                .padding(.horizontal, 14)
                .padding(.top, 3)
                Spacer(minLength: 0)
            }
            .padding(.horizontal, 6)
            .padding(.vertical, 5)
        }
        .background(Color.clear)
        .foregroundStyle(.primaryText)
    }
}

struct PopoverInteriorBackdrop: View {
    var body: some View {
        Rectangle()
            .fill(
                LinearGradient(
                    colors: [
                        Color.black.opacity(0.56),
                        Color.black.opacity(0.48),
                        Color.black.opacity(0.62)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
            )
            .overlay(
                Rectangle()
                    .fill(Color.white.opacity(0.014))
                    .blendMode(.plusLighter)
            )
    }
}

struct HeaderScoreView: View {
    let dashboard: SkillDashboard

    var body: some View {
        HStack(alignment: .center, spacing: 16) {
            ScoreEmblemView(dashboard: dashboard)

            VStack(alignment: .leading, spacing: 4) {
                HStack(alignment: .center, spacing: 8) {
                    Text(dashboard.verdictTitle)
                        .font(.system(size: 16, weight: .heavy, design: .rounded))
                        .foregroundStyle(.primaryText)
                        .lineLimit(1)
                        .minimumScaleFactor(0.82)
                }

                Text(dashboard.verdictDetail)
                    .font(.system(size: 10, weight: .semibold, design: .rounded))
                    .foregroundStyle(.bodyText)
                    .lineLimit(1)
                    .truncationMode(.tail)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.horizontal, 18)
        .padding(.bottom, 10)
    }
}

struct ScoreEmblemView: View {
    let dashboard: SkillDashboard
    private var ringColor: Color {
        if dashboard.score == nil {
            return dashboard.emblemBadgeTone.color.opacity(0.42)
        }
        return dashboard.scoreTone.color.opacity(0.64)
    }
    private var scoreTextColor: Color {
        if dashboard.score == nil {
            return Color.white.opacity(0.86)
        }
        return dashboard.scoreTone == .positive ? dashboard.scoreTone.color : .primaryText
    }

    var body: some View {
        ZStack(alignment: .top) {
            ZStack {
                Hexagon()
                    .fill(
                        LinearGradient(
                            colors: [
                                .greenPanel.opacity(0.92),
                                Color(red: 0.0, green: 0.045, blue: 0.025).opacity(0.96)
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .overlay(
                        Hexagon()
                            .fill(
                                RadialGradient(
                                    colors: [
                                        ringColor.opacity(0.24),
                                        Color.clear
                                    ],
                                    center: .top,
                                    startRadius: 0,
                                    endRadius: 58
                                )
                            )
                            .blendMode(.plusLighter)
                    )
                    .overlay(
                        Hexagon()
                            .stroke(Color.white.opacity(0.11), lineWidth: 1)
                            .padding(4)
                    )
                    .overlay(Hexagon().stroke(ringColor, lineWidth: 2))
                    .shadow(color: ringColor.opacity(0.18), radius: 8, x: 0, y: 0)
                    .shadow(color: .black.opacity(0.42), radius: 14, x: 0, y: 9)
                    .frame(width: 76, height: 62)

                Text(dashboard.scoreText)
                    .font(.system(size: 22, weight: .heavy, design: .rounded))
                    .foregroundStyle(scoreTextColor)
            }
            .zIndex(0)

            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(Color.black.opacity(0.76))
                .frame(width: 104, height: 36)
                .shadow(color: .black.opacity(0.44), radius: 9, y: -1)
                .offset(y: 38)
                .zIndex(1)

            HStack(spacing: 6) {
                Image(systemName: dashboard.emblemBadgeSystemName)
                    .font(.system(size: 12, weight: .heavy))
                Text(dashboard.emblemBadgeLabel)
                    .font(.system(size: 13, weight: .heavy, design: .rounded))
                    .lineLimit(1)
                    .minimumScaleFactor(0.78)
            }
            .foregroundStyle(dashboard.emblemBadgeTone.color)
            .frame(width: 104, height: 36)
            .background(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(dashboard.emblemBadgeTone.panelColor.opacity(0.98))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .stroke(LinearGradient(colors: [dashboard.emblemBadgeTone.color.opacity(0.46), dashboard.emblemBadgeTone.color.opacity(0.22)], startPoint: .top, endPoint: .bottom), lineWidth: 1)
            )
            .shadow(color: dashboard.emblemBadgeTone.color.opacity(0.18), radius: 8, y: 1)
            .shadow(color: .black.opacity(0.40), radius: 8, y: 5)
            .offset(y: 38)
            .zIndex(2)
        }
        .frame(width: 104, height: 84, alignment: .top)
        .accessibilityLabel("Local score \(dashboard.scoreText), local status \(dashboard.emblemBadgeLabel).")
    }
}

struct ProofLaneComparisonView: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(spacing: 6) {
            HStack(spacing: 8) {
                Text("Source")
                    .frame(width: 102, alignment: .leading)
                Text("Score")
                    .frame(maxWidth: .infinity, alignment: .center)
                Text("Impact")
                    .frame(maxWidth: .infinity, alignment: .center)
                Text("Security")
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }
            .font(.system(size: 8, weight: .heavy, design: .rounded))
            .foregroundStyle(.secondaryText)
            .tracking(0.45)
            .textCase(.uppercase)
            .padding(.horizontal, 10)

            ComparisonMetricRow(
                icon: .skills,
                title: "Skills SDK",
                subtitle: "Local",
                score: dashboard.scoreText,
                scoreTone: dashboard.scoreTone,
                impact: dashboard.localImpactDisplay,
                impactTone: dashboard.impact.tone,
                security: dashboard.security.statusDisplay,
                securityTone: dashboard.security.tone
            )
            ComparisonMetricRow(
                icon: .tessl,
                title: "Tessl",
                subtitle: "Registry",
                score: dashboard.tessl.registryResultLabel,
                scoreTone: dashboard.tessl.ok ? dashboard.tessl.registryScoreTone : dashboard.tessl.tone,
                impact: dashboard.tessl.registryImpactDisplay,
                impactTone: dashboard.tessl.registryImpactTone,
                security: dashboard.tessl.registrySecurityDisplay,
                securityTone: dashboard.tessl.registrySecurityTone
            )
        }
        .padding(.vertical, 4)
        .accessibilityLabel("Proof lanes. Skills SDK local score \(dashboard.scoreText). Tessl registry score \(dashboard.tessl.registryResultLabel).")
    }
}

struct ComparisonMetricRow: View {
    let icon: ProofLaneCard.IconKind
    let title: String
    let subtitle: String
    let score: String
    let scoreTone: StatusTone
    let impact: String
    let impactTone: StatusTone
    let security: String
    let securityTone: StatusTone

    var body: some View {
        HStack(spacing: 8) {
            HStack(spacing: 8) {
                ProofLaneIcon(kind: icon)
                VStack(alignment: .leading, spacing: 1) {
                    Text(title)
                        .font(.system(size: 11, weight: .heavy, design: .rounded))
                        .foregroundStyle(.primaryText)
                        .lineLimit(1)
                    Text(subtitle.uppercased())
                        .font(.system(size: 7, weight: .heavy, design: .rounded))
                        .foregroundStyle(.secondaryText)
                        .tracking(0.45)
                        .lineLimit(1)
                }
            }
            .frame(width: 102, alignment: .leading)

            MiniValueBadge(text: score, tone: scoreTone, style: .hex)
                .frame(maxWidth: .infinity)
            MiniValueBadge(text: impact, tone: impactTone, style: .pill)
                .frame(maxWidth: .infinity)
            MiniValueBadge(text: security, tone: securityTone, style: .pill)
                .frame(maxWidth: .infinity, alignment: .trailing)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 7)
        .background(
            RoundedRectangle(cornerRadius: 11, style: .continuous)
                .fill(Color.white.opacity(icon == .skills ? 0.050 : 0.030))
        )
        .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous).stroke(Color.white.opacity(0.070), lineWidth: 1))
    }
}

struct MiniValueBadge: View {
    enum Style {
        case hex
        case pill
    }

    let text: String
    let tone: StatusTone
    let style: Style

    var body: some View {
        switch style {
        case .hex:
            ZStack {
                Hexagon()
                    .fill(tone.panelColor.opacity(0.38))
                Hexagon()
                    .stroke(tone.color.opacity(0.72), lineWidth: 0.9)
                Text(displayText)
                    .font(.system(size: 11, weight: .heavy, design: .rounded))
                    .foregroundStyle(tone.color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.78)
            }
            .frame(width: 36, height: 30)
        case .pill:
            Text(displayText)
                .font(.system(size: displayText.count > 8 ? 8 : 10, weight: .heavy, design: .rounded))
                .foregroundStyle(tone.color)
                .lineLimit(1)
                .minimumScaleFactor(0.70)
                .frame(width: 68, height: 20)
                .background(Capsule().fill(tone.panelColor.opacity(0.70)))
                .overlay(Capsule().stroke(tone.color.opacity(0.34), lineWidth: 1))
        }
    }

    private var displayText: String {
        text == "--" ? "--" : text
    }
}

struct ProofLaneCard: View {
    enum IconKind {
        case skills
        case tessl
    }

    let icon: IconKind
    let title: String
    let status: String
    let value: String
    let detail: String
    let tone: StatusTone
    private var displayValue: String {
        value == "--" ? "--" : value
    }
    private var displayTone: Color {
        value == "--" ? Color.secondaryText : tone.color
    }
    private var valueFont: Font {
        value == "--"
            ? .system(size: 10, weight: .heavy, design: .rounded)
            : .system(size: 18, weight: .heavy, design: .rounded)
    }

    var body: some View {
        HStack(spacing: 10) {
            ProofLaneIcon(kind: icon)

            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(title)
                        .font(.system(size: 12, weight: .bold, design: .rounded))
                        .foregroundStyle(.primaryText)
                        .lineLimit(1)
                        .minimumScaleFactor(0.82)
                    Text(status.uppercased())
                        .font(.system(size: 7, weight: .heavy, design: .rounded))
                        .foregroundStyle(.secondaryText)
                        .tracking(0.45)
                        .lineLimit(1)
                }
                Text(detail)
                    .font(.system(size: 9, weight: .semibold, design: .rounded))
                    .foregroundStyle(.bodyText)
                    .lineLimit(1)
                    .truncationMode(.tail)
            }

            Spacer(minLength: 6)

            Text(displayValue)
                .font(valueFont)
                .foregroundStyle(displayTone)
                .lineLimit(1)
                .minimumScaleFactor(0.80)
                .frame(width: 56, alignment: .trailing)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 9)
        .padding(.vertical, 6)
        .overlay(
            Rectangle()
                .fill(Color.white.opacity(icon == .skills ? 0.070 : 0.035))
                .frame(height: 1)
                .padding(.leading, 34),
            alignment: .bottom
        )
    }
}

struct ProofLaneIcon: View {
    let kind: ProofLaneCard.IconKind

    var body: some View {
        Group {
            switch kind {
            case .skills:
                SkillsSDKLogoView(size: 27)
            case .tessl:
                TesslLogoView(size: 27)
            }
        }
        .opacity(0.94)
    }
}

struct FleetSummaryView: View {
    let fleet: FleetSignal

    var body: some View {
        HStack(spacing: 7) {
            Image(systemName: "square.stack.3d.up.fill")
                .font(.system(size: 10, weight: .bold))
                .foregroundStyle(fleet.tone.color)
            Text(fleet.compactLine)
                .font(.system(size: 10, weight: .semibold, design: .rounded))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
                .truncationMode(.tail)
            Spacer(minLength: 4)
            CopyIconButton(
                command: fleet.inventoryCommand,
                idleSystemName: "list.bullet.clipboard",
                copiedSystemName: "checkmark",
                help: "Copy all-skills inventory command"
            )
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 5)
        .background(
            RoundedRectangle(cornerRadius: 9, style: .continuous)
                .fill(Color.white.opacity(0.035))
        )
        .overlay(RoundedRectangle(cornerRadius: 9, style: .continuous).stroke(Color.white.opacity(0.06), lineWidth: 1))
        .accessibilityLabel("Local fleet inventory. \(fleet.title). \(fleet.detail).")
    }
}

struct LocalChecksPanel: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .top, spacing: 8) {
                MetricBarColumn(
                    title: "Quality",
                    value: dashboard.quality.statusLabel,
                    detail: dashboard.quality.compactDetail,
                    progress: dashboard.quality.scoreFraction,
                    tone: dashboard.quality.tone,
                    showsFill: dashboard.quality.score != nil
                )
                MetricBarColumn(
                    title: "Impact",
                    value: dashboard.impact.statusLabel,
                    detail: dashboard.impact.shortDetail,
                    progress: dashboard.impact.scoreFraction,
                    tone: dashboard.impact.tone,
                    showsFill: dashboard.impact.score != nil
                )
                MetricBarColumn(
                    title: "Security",
                    value: dashboard.security.statusDisplay,
                    detail: dashboard.security.severityLine,
                    progress: min(max(Double(dashboard.security.score ?? 0) / 100.0, 0), 1),
                    tone: dashboard.security.tone,
                    showsFill: dashboard.security.score != nil
                )
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 11, style: .continuous)
                .fill(Color.white.opacity(0.045))
        )
        .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous).stroke(Color.white.opacity(0.085), lineWidth: 1))
        .accessibilityLabel("Local checks. Quality \(dashboard.quality.statusLabel). Impact \(dashboard.impact.statusLabel). Security \(dashboard.security.statusDisplay).")
    }
}

struct MetricBarColumn: View {
    let title: String
    let value: String
    let detail: String
    let progress: Double
    let tone: StatusTone
    let showsFill: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text(title)
                    .font(.system(size: 10, weight: .heavy, design: .rounded))
                    .foregroundStyle(.primaryText)
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)
                Spacer(minLength: 2)
                Text(displayValue)
                    .font(.system(size: displayValue.count > 7 ? 8 : 10, weight: .heavy, design: .rounded))
                    .foregroundStyle(tone.color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.66)
            }
            ProgressStripe(value: progress, tone: tone, showsFill: showsFill)
                .frame(height: 5)
            Text(detail)
                .font(.system(size: 8, weight: .medium, design: .rounded))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
                .truncationMode(.tail)
        }
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .accessibilityLabel("\(title). \(value). \(detail).")
    }

    private var displayValue: String {
        value == "--" ? "Pending" : value
    }
}

struct SectionLabel: View {
    let text: String

    init(_ text: String) {
        self.text = text
    }

    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 8, weight: .bold, design: .rounded))
            .foregroundStyle(.secondaryText)
            .tracking(0.7)
            .padding(.top, 5)
    }
}

struct SkillIdentityView: View {
    let dashboard: SkillDashboard

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(spacing: 6) {
                Text(dashboard.registryPath)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(.secondaryText)
                    .lineLimit(1)
                    .truncationMode(.middle)
                Spacer(minLength: 4)
                CopyIconButton(
                    command: dashboard.selectedSkillInspectCommand,
                    idleSystemName: "doc.text.magnifyingglass",
                    copiedSystemName: "checkmark",
                    help: "Copy selected SKILL.md inspect command"
                )
            }
            Text(dashboard.displayName)
                .font(.system(size: 18, weight: .heavy, design: .rounded))
                .lineLimit(1)
                .minimumScaleFactor(0.86)
            Text(dashboard.summaryLine)
                .font(.system(size: 11, weight: .medium, design: .rounded))
                .lineSpacing(1)
                .foregroundStyle(.bodyText)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

struct EvidenceRow: View {
    let metric: MetricSignal
    let title: String

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(title)
                .font(.system(size: 13, weight: .bold, design: .rounded))
                .frame(width: 58, alignment: .leading)
            Text(metric.statusLabel)
                .font(.system(size: 12, weight: .bold, design: .rounded))
                .foregroundStyle(metric.tone.color)
                .lineLimit(1)
                .minimumScaleFactor(0.72)
                .frame(width: 62, alignment: .trailing)
            Text(metric.compactDetail)
                .font(.system(size: 10, weight: .medium, design: .rounded))
                .foregroundStyle(.bodyText)
                .lineLimit(1)
                .truncationMode(.tail)
            Spacer(minLength: 4)
            CopyIconButton(
                command: metric.command,
                idleSystemName: "terminal",
                copiedSystemName: "checkmark",
                help: "Copy \(metric.sourceShort) command"
            )
            if metric.tone != .positive, let score = metric.score {
                ProgressStripe(value: min(max(Double(score) / 100.0, 0), 1), tone: metric.tone, showsFill: true)
                    .frame(width: 42)
            }
        }
        .accessibilityLabel("\(title). \(metric.statusLabel). \(metric.compactDetail).")
    }
}

struct SecurityBlock: View {
    let signal: SecuritySignal

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(alignment: .firstTextBaseline) {
                HStack(spacing: 6) {
                    Image(systemName: signal.tone == .warning ? "exclamationmark.shield.fill" : "checkmark.shield.fill")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(signal.tone.color)
                    Text("Security")
                        .font(.system(size: 15, weight: .heavy, design: .rounded))
                }
                Spacer()
                HStack(spacing: 6) {
                    Text(signal.statusDisplay)
                        .font(.system(size: 14, weight: .heavy, design: .rounded))
                        .lineLimit(1)
                        .minimumScaleFactor(0.78)
                }
                .foregroundStyle(signal.tone.color)
            }

            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text(signal.severityLine)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(signal.tone.color)
                    .lineLimit(1)
                Spacer(minLength: 0)
                if signal.status.localizedCaseInsensitiveContains("flag") {
                    Text(signal.penaltyLine)
                        .font(.system(size: 10, weight: .heavy, design: .rounded))
                        .foregroundStyle(signal.tone.color)
                }
            }
            .accessibilityLabel(signal.accessibilityText)
        }
        .padding(.horizontal, signal.status.localizedCaseInsensitiveContains("flag") ? 10 : 0)
        .padding(.vertical, signal.status.localizedCaseInsensitiveContains("flag") ? 8 : 0)
        .background(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(signal.status.localizedCaseInsensitiveContains("flag") ? signal.tone.panelColor.opacity(0.46) : Color.clear)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(signal.status.localizedCaseInsensitiveContains("flag") ? signal.tone.color.opacity(0.22) : Color.clear, lineWidth: 1)
        )
    }
}

struct TesslBlock: View {
    let dashboard: SkillDashboard
    private var signal: TesslSignal { dashboard.tessl }
    private var localSecurityFlagged: Bool { dashboard.security.status.localizedCaseInsensitiveContains("flag") }
    private var title: String {
        signal.ok ? "Tessl score" : "Tessl registry"
    }
    private var detail: String {
        signal.ok ? signal.registryComparisonDetail(localScore: dashboard.score) : signal.compactDetail
    }
    private var trailingLabel: String {
        signal.ok ? "Registry" : signal.registryStatusLabel
    }
    private var trailingValue: String {
        signal.ok ? signal.registryResultLabel : "--"
    }

    var body: some View {
        HStack(spacing: 10) {
            TesslLogoView(size: 24)
            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .lineLimit(1)
                Text(detail)
                    .font(.system(size: 10, weight: .medium, design: .rounded))
                    .foregroundStyle(.bodyText)
                    .lineLimit(1)
                    .truncationMode(.tail)
            }
            Spacer(minLength: 6)
            VStack(alignment: .trailing, spacing: 1) {
                Text(trailingLabel)
                    .font(.system(size: 8, weight: .heavy, design: .rounded))
                    .foregroundStyle(.secondaryText)
                    .textCase(.uppercase)
                    .lineLimit(1)
                Text(trailingValue)
                    .font(.system(size: 17, weight: .heavy, design: .rounded))
                    .foregroundStyle(signal.registryStatusTone.color)
                    .lineLimit(1)
            }
            CopyIconButton(
                command: dashboard.registrySearchCommand,
                idleSystemName: "terminal",
                copiedSystemName: "checkmark",
                help: "Copy Tessl registry search"
            )
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 7)
        .background(
            RoundedRectangle(cornerRadius: 11, style: .continuous)
                .fill(Color.white.opacity(localSecurityFlagged ? 0.020 : 0.030))
        )
        .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous).stroke(Color.white.opacity(localSecurityFlagged ? 0.045 : 0.065), lineWidth: 1))
    }
}

struct CommandDock: View {
    let dashboard: SkillDashboard
    @ObservedObject private var feedback = CopyFeedbackModel.shared
    private var signal: TesslSignal { dashboard.tessl }
    private var securityFlagged: Bool { dashboard.security.status.localizedCaseInsensitiveContains("flag") }
    private var actionCommand: String {
        securityFlagged ? dashboard.security.inspectCommand : signal.recoveryCommand
    }
    private var copied: Bool { feedback.copiedCommand == actionCommand }
    private var actionTone: StatusTone {
        if copied { return .positive }
        if securityFlagged { return dashboard.security.tone }
        return signal.tone
    }
    private var actionIcon: String {
        if copied { return "checkmark" }
        if securityFlagged { return "terminal.fill" }
        return signal.ok ? "arrow.up.right.square" : "terminal.fill"
    }
    private var actionTitle: String {
        if copied { return securityFlagged ? "Copied security check" : signal.copiedActionTitle }
        if securityFlagged { return "Copy security check" }
        return signal.actionTitle
    }
    private var actionHelp: String {
        if securityFlagged { return "Copy local SDK security check" }
        return signal.actionHelp
    }
    private var secondaryCommand: String {
        signal.ok ? dashboard.selectedSkillInspectCommand : signal.recoveryCommand
    }
    private var secondaryLabel: String {
        signal.ok ? "Inspect" : "Next"
    }

    var body: some View {
        VStack(spacing: 0) {
            Button {
                if securityFlagged {
                    feedback.copy(dashboard.security.inspectCommand)
                } else if signal.ok {
                    if let url = dashboard.registryURL {
                        NSWorkspace.shared.open(url)
                    }
                } else if signal.cliAvailable {
                    LoginLauncher.open(command: signal.recoveryCommand)
                } else {
                    feedback.copy(signal.recoveryCommand)
                }
            } label: {
                HStack(spacing: 8) {
                    Image(systemName: actionIcon)
                        .font(.system(size: 11, weight: .bold))
                    Text(actionTitle)
                        .font(.system(size: 12, weight: .heavy, design: .rounded))
                        .lineLimit(1)
                    Spacer()
                }
                .foregroundStyle(actionTone.color)
                .padding(.horizontal, 12)
                .padding(.vertical, 7)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(actionTone.panelColor.opacity(securityFlagged ? 0.42 : 0.34))
            }
            .buttonStyle(.plain)
            .help(actionHelp)

            Rectangle()
                .fill(Color.white.opacity(0.050))
                .frame(height: 1)

            HStack(spacing: 10) {
                Text(secondaryLabel)
                    .font(.system(size: 9, weight: .semibold, design: .rounded))
                    .foregroundStyle(.secondaryText)
                Text(secondaryCommand)
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundStyle(Color.white.opacity(0.70))
                    .lineLimit(1)
                    .truncationMode(.middle)
                Spacer(minLength: 8)
                CopyIconButton(
                    command: secondaryCommand,
                    idleSystemName: signal.ok ? "doc.text.magnifyingglass" : "terminal",
                    copiedSystemName: "checkmark",
                    help: signal.ok ? "Copy selected local skill inspect command" : "Copy next Tessl command"
                )
            }
            .padding(.horizontal, 9)
            .padding(.vertical, 5)
        }
        .background(
            RoundedRectangle(cornerRadius: 11, style: .continuous)
                .fill(Color.black.opacity(0.30))
        )
        .clipShape(RoundedRectangle(cornerRadius: 11, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous).stroke(actionTone.color.opacity(securityFlagged ? 0.22 : 0.14), lineWidth: 1))
        .accessibilityLabel("Action. \(actionTitle). Secondary command \(secondaryCommand).")
    }
}

struct PrimaryAction: View {
    let dashboard: SkillDashboard
    @ObservedObject private var feedback = CopyFeedbackModel.shared
    private var signal: TesslSignal { dashboard.tessl }
    private var securityFlagged: Bool { dashboard.security.status.localizedCaseInsensitiveContains("flag") }
    private var actionCommand: String {
        securityFlagged ? dashboard.security.inspectCommand : signal.recoveryCommand
    }
    private var copied: Bool { feedback.copiedCommand == actionCommand }
    private var actionTone: StatusTone {
        if copied { return .positive }
        if securityFlagged { return dashboard.security.tone }
        return signal.tone
    }
    private var actionIcon: String {
        if copied { return "checkmark" }
        if securityFlagged { return "terminal.fill" }
        return signal.ok ? "arrow.up.right.square" : "terminal.fill"
    }
    private var actionTitle: String {
        if copied { return securityFlagged ? "Copied security check" : signal.copiedActionTitle }
        if securityFlagged { return "Copy security check" }
        return signal.actionTitle
    }
    private var actionHelp: String {
        if securityFlagged { return "Copy local SDK security check" }
        return signal.actionHelp
    }

    var body: some View {
        Button {
            if securityFlagged {
                feedback.copy(dashboard.security.inspectCommand)
            } else if signal.ok {
                if let url = dashboard.registryURL {
                    NSWorkspace.shared.open(url)
                }
            } else if signal.cliAvailable {
                LoginLauncher.open(command: signal.recoveryCommand)
            } else {
                feedback.copy(signal.recoveryCommand)
            }
        } label: {
            HStack(spacing: 8) {
                Image(systemName: actionIcon)
                    .font(.system(size: 12, weight: .bold))
                Text(actionTitle)
                    .font(.system(size: 12, weight: .heavy, design: .rounded))
                Spacer()
            }
            .foregroundStyle(actionTone.color)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(securityFlagged ? actionTone.panelColor.opacity(0.80) : signal.ok ? StatusTone.positive.panelColor.opacity(0.80) : Color.black.opacity(0.26))
            )
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 10).stroke(actionTone.color.opacity(0.42), lineWidth: 1))
        }
        .buttonStyle(.plain)
        .help(actionHelp)
    }
}

struct TesslLogoView: View {
    var size: CGFloat = 28
    private var imageSize: CGFloat { max(16, size * 0.66) }

    var body: some View {
        ZStack {
            Circle()
                .fill(.thinMaterial)
            Circle()
                .fill(Color.white.opacity(0.08))
            Circle()
                .fill(Color.black.opacity(0.24))

            if let image = TesslLogoLoader.image {
                Image(nsImage: image)
                    .resizable()
                    .interpolation(.high)
                    .scaledToFill()
                    .scaleEffect(1.84)
                    .frame(width: imageSize, height: imageSize)
                    .clipShape(Circle())
            } else {
                Image(systemName: "shippingbox.fill")
                    .font(.system(size: max(11, size * 0.5), weight: .bold))
                    .foregroundStyle(.primaryText)
            }
        }
        .frame(width: size, height: size)
        .overlay(Circle().stroke(Color.white.opacity(0.18), lineWidth: 1))
        .overlay(Circle().stroke(Color.successAccent.opacity(0.10), lineWidth: 1))
        .shadow(color: .black.opacity(0.28), radius: 4, y: 2)
    }
}

struct SkillsSDKLogoView: View {
    var size: CGFloat = 28
    private var glyphSize: CGFloat { max(12, size * 0.50) }
    private var dotSize: CGFloat { max(5, size * 0.20) }

    var body: some View {
        ZStack {
            Circle()
                .fill(.thinMaterial)
            Circle()
                .fill(Color.white.opacity(0.08))
            Circle()
                .fill(Color.black.opacity(0.24))

            Image(systemName: "doc.text.fill")
                .font(.system(size: glyphSize, weight: .semibold))
                .foregroundStyle(Color.white.opacity(0.88))
                .offset(x: -1, y: -0.5)

            Circle()
                .fill(Color(red: 0.55, green: 0.66, blue: 0.56))
                .frame(width: dotSize, height: dotSize)
                .overlay(Circle().stroke(Color.black.opacity(0.42), lineWidth: 0.8))
                .offset(x: size * 0.24, y: size * 0.24)
        }
        .frame(width: size, height: size)
        .overlay(Circle().stroke(Color.white.opacity(0.18), lineWidth: 1))
        .overlay(Circle().stroke(Color.successAccent.opacity(0.10), lineWidth: 1))
        .shadow(color: .black.opacity(0.28), radius: 4, y: 2)
    }
}

enum LoginLauncher {
    @MainActor
    static func open(command: String) {
        let script = """
        tell application "Terminal"
            activate
            do script "(escapedAppleScript(command))"
        end tell
        """
        var error: NSDictionary?
        if let appleScript = NSAppleScript(source: script), appleScript.executeAndReturnError(&error).stringValue != nil || error == nil {
            return
        }
        CopyFeedbackModel.shared.copy(command)
    }

    private static func escapedAppleScript(_ value: String) -> String {
        value
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
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

enum SkillsSDKIconLoader {
    static let image: NSImage? = {
        if let resource = Bundle.main.url(forResource: "SkillsSDKIcon", withExtension: "png") {
            let image = NSImage(contentsOf: resource)
            image?.isTemplate = false
            return image
        }
        let repoResource = URL(fileURLWithPath: "/Users/jamiecraik/dev/agent-skills/Prototypes/improve-agent-native-menubar/Sources/ImproveAgentNativeMenuBar/Resources/SkillsSDKIcon.png")
        let image = NSImage(contentsOf: repoResource)
        image?.isTemplate = false
        return image
    }()

    static let menuBarImage: NSImage? = {
        guard let image else { return nil }
        let targetSize = NSSize(width: 23, height: 23)
        let resized = NSImage(size: targetSize)
        resized.lockFocus()
        NSGraphicsContext.current?.imageInterpolation = .high
        image.draw(in: NSRect(origin: .zero, size: targetSize), from: .zero, operation: .sourceOver, fraction: 1)
        image.draw(in: NSRect(origin: .zero, size: targetSize), from: .zero, operation: .plusLighter, fraction: 0.18)
        resized.unlockFocus()
        resized.isTemplate = false
        return resized
    }()
}

struct InstallCommand: View {
    let command: String
    let signal: TesslSignal
    private var displayedCommand: String {
        signal.ok ? command : signal.recoveryCommand
    }

    var body: some View {
        HStack(spacing: 10) {
            Text(signal.installLabel)
                .font(.system(size: 9, weight: .semibold, design: .rounded))
                .foregroundStyle(.secondaryText)
            Text(displayedCommand)
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .foregroundStyle(Color.white.opacity(0.78))
                .lineLimit(1)
                .truncationMode(.middle)
            Spacer(minLength: 8)
            CopyIconButton(
                command: displayedCommand,
                idleSystemName: signal.ok ? "doc.on.doc" : "terminal",
                copiedSystemName: "checkmark",
                help: signal.ok ? "Copy install command" : "Copy next Tessl command"
            )
        }
        .padding(.horizontal, 9)
        .padding(.vertical, 4)
        .background(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(Color.black.opacity(signal.ok ? 0.30 : 0.36))
        )
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.white.opacity(0.16), lineWidth: 1))
    }
}

struct SourcePill: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.system(size: 7, weight: .bold, design: .rounded))
            .foregroundStyle(Color.pendingAccent.opacity(0.68))
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(Color.black.opacity(0.16))
            )
            .clipShape(Capsule())
            .overlay(Capsule().stroke(Color.pendingAccent.opacity(0.16), lineWidth: 1))
    }
}

struct CopyIconButton: View {
    let command: String
    let idleSystemName: String
    let copiedSystemName: String
    let help: String
    @ObservedObject private var feedback = CopyFeedbackModel.shared
    private var copied: Bool { feedback.copiedCommand == command }

    var body: some View {
        Button {
            feedback.copy(command)
        } label: {
            Image(systemName: copied ? copiedSystemName : idleSystemName)
                .font(.system(size: 9, weight: .bold))
                .frame(width: 19, height: 19)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(copied ? StatusTone.positive.color : .secondaryText)
        .background(Color.white.opacity(copied ? 0.045 : 0.018))
        .clipShape(RoundedRectangle(cornerRadius: 5, style: .continuous))
        .help(help)
        .accessibilityLabel(help)
    }
}

struct FooterBar: View {
    @ObservedObject var model: DashboardModel

    var body: some View {
        HStack(spacing: 8) {
            Spacer(minLength: 0)
            CopyIconButton(
                command: model.dashboard.localEvidenceCommand,
                idleSystemName: "doc.on.clipboard",
                copiedSystemName: "checkmark",
                help: "Copy all local SDK checks"
            )
            Button {
                Task { await model.refresh() }
            } label: {
                Image(systemName: model.isRefreshing ? "arrow.triangle.2.circlepath" : "arrow.clockwise")
                    .font(.system(size: 9, weight: .bold))
                    .frame(width: 18, height: 18)
                    .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .foregroundStyle(model.isRefreshing ? StatusTone.warning.color : .secondaryText)
            .help("Refresh local and Tessl evidence")
        }
        .frame(height: 18)
        .padding(.bottom, 2)
    }
}

struct ProgressStripe: View {
    let value: Double
    let tone: StatusTone
    let showsFill: Bool

    var body: some View {
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule().fill(Color.white.opacity(0.115))
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
    static var secondaryText: Color { Color(red: 0.57, green: 0.57, blue: 0.64) }
    static var bodyText: Color { Color(red: 0.71, green: 0.71, blue: 0.77) }
    static var accentGreen: Color { Color.successAccent }
}

extension Color {
    static var greenPanel: Color { Color(red: 0.0, green: 0.15, blue: 0.075) }
    static var greenBorder: Color { Color(red: 0.02, green: 0.25, blue: 0.11) }
    static var successAccent: Color { Color(red: 0.31, green: 0.89, blue: 0.50) }
    static var warningAccent: Color { Color(red: 1.0, green: 0.70, blue: 0.22) }
    static var advisoryAccent: Color { Color(red: 0.16, green: 0.84, blue: 0.94) }
    static var pendingAccent: Color { Color(red: 0.56, green: 0.58, blue: 0.64) }
    static var dangerAccent: Color { Color(red: 1.0, green: 0.40, blue: 0.34) }
}

enum StatusTone {
    case positive
    case advisory
    case pending
    case warning
    case danger

    var color: Color {
        switch self {
        case .positive: return .successAccent
        case .advisory: return .advisoryAccent
        case .pending: return .pendingAccent
        case .warning: return .warningAccent
        case .danger: return .dangerAccent
        }
    }

    var panelColor: Color {
        switch self {
        case .positive: return Color.successAccent.opacity(0.16)
        case .advisory: return Color.advisoryAccent.opacity(0.16)
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
    var localEvidenceCommand: String
    var reviewedText: String
    var deltaText: String
    var quality: MetricSignal
    var impact: MetricSignal
    var security: SecuritySignal
    var tessl: TesslSignal
    var fleet: FleetSignal
    var refreshedAt: Date
    var error: String?

    var score: Int? {
        guard let qualityScore = quality.score,
              let impactScore = impact.score,
              let securityScore = security.score else { return nil }
        return Int((Double(qualityScore + impactScore + securityScore) / 3.0).rounded())
    }

    var scoreText: String { score.map(String.init) ?? "--" }
    var summaryLine: String { description }
    var scoreTone: StatusTone {
        guard let score else { return .pending }
        if score >= 80 { return .positive }
        if score >= 60 { return .warning }
        return .danger
    }
    var scoreCaption: String {
        "Local"
    }
    var scoreSourceLine: String {
        score == nil ? "Q/I/S pending" : "Q\(quality.formulaValue) I\(impact.formulaValue) S\(security.formulaValue)"
    }
    var localImpactDisplay: String {
        impact.ratioLabel ?? (impact.score == nil ? "Not run" : impact.statusLabel)
    }
    var registryURL: URL? {
        let escaped = registryPath
            .split(separator: "/")
            .map { String($0).addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? String($0) }
            .joined(separator: "/")
        return URL(string: "https://tessl.io/registry/\(escaped)")
    }
    var registrySearchCommand: String {
        "tessl search --json --type skills \(registryPath)"
    }
    var selectedSkillInspectCommand: String {
        "cd \(globalShellQuoted(repoPath)) && sed -n '1,120p' \(globalShellQuoted(fleet.selectedSkillPath))"
    }
    var emblemBadgeLabel: String {
        if security.status.localizedCaseInsensitiveContains("flag") {
            return security.statusDisplay
        }
        if score == nil {
            return "Local pending"
        }
        return "Local score"
    }
    var emblemBadgeSystemName: String {
        if security.status.localizedCaseInsensitiveContains("flag") {
            return "exclamationmark.shield.fill"
        }
        if score == nil {
            return "clock"
        }
        return "checkmark.seal.fill"
    }
    var emblemBadgeTone: StatusTone {
        if security.status.localizedCaseInsensitiveContains("flag") {
            return security.tone
        }
        if score == nil {
            return .pending
        }
        return scoreTone
    }
    var verdictTitle: String {
        if security.status.localizedCaseInsensitiveContains("flag") { return "Needs review" }
        if score == nil { return "Local pending" }
        return "Skills SDK"
    }
    var verdictDetail: String {
        if security.status.localizedCaseInsensitiveContains("flag") && !tessl.ok {
            return "Security flagged · \(tessl.blockerSummary)"
        }
        if security.status.localizedCaseInsensitiveContains("flag") {
            return "\(security.statusDisplay) need inspection"
        }
        if !tessl.ok {
            return "Current improve-agent-native run · \(tessl.blockerSummary)"
        }
        return "Local SDK evidence and Tessl registry checks available"
    }
    var provenanceLine: String {
        let tesslState = tessl.ok ? "loaded" : tessl.compactBlockerSummary
        return "SDK \(compactScoreBreakdownLine) · \(tessl.compactVersionBadge) · 5m · \(tesslState)"
    }
    var scoreBreakdownLine: String {
        "Q \(quality.formulaValue) · I \(impact.formulaValue) · S \(security.formulaValue)"
    }
    var compactScoreBreakdownLine: String {
        "Q\(quality.formulaValue) I\(impact.formulaValue) S\(security.formulaValue)"
    }
    var localComparisonDetail: String {
        let impactValue = impact.score == nil ? "--" : impact.formulaValue
        return "Q\(quality.formulaValue) I\(impactValue) S\(security.formulaValue)"
    }
    var refreshedTimeText: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: refreshedAt)
    }

    func withError(_ message: String) -> SkillDashboard {
        var copy = self
        copy.error = message
        copy.tessl = TesslSignal(
            ok: false,
            cliAvailable: false,
            authenticated: false,
            displayStatus: "Blocked",
            detail: message,
            cliVersion: nil,
            registryScore: nil,
            registryVersion: nil,
            registryQualityScore: nil,
            registryImpactScore: nil,
            registrySecurityLabel: nil,
            registryEvalCount: nil,
            registryImprovementMultiplier: nil,
            recoveryCommand: "tessl doctor"
        )
        return copy
    }

    static let placeholder = SkillDashboard(
        displayName: "improve-agent-native",
        version: "0.2.0",
        description: "Audit agent-native readiness for this skill.",
        registryPath: "jscraik/improve-agent-native",
        repoPath: "/Users/jamiecraik/dev/agent-skills",
        installCommand: "tessl install jscraik/improve-agent-native",
        localEvidenceCommand: DashboardLoader.localEvidenceCommand(root: DashboardLoader.defaultRepoRoot),
        reviewedText: "Local SDK evidence",
        deltaText: "Local SDK",
        quality: MetricSignal(
            score: nil,
            detail: "Run package verify to populate quality.",
            source: "Local SDK package verify",
            command: DashboardLoader.copyCommand(root: DashboardLoader.defaultRepoRoot, command: DashboardLoader.packageCommand)
        ),
        impact: MetricSignal(
            score: nil,
            detail: "Run scenario-quality to populate impact.",
            source: "Local SDK scenario-quality",
            command: DashboardLoader.copyCommand(root: DashboardLoader.defaultRepoRoot, command: DashboardLoader.impactCommand)
        ),
        security: SecuritySignal(
            score: nil,
            status: "Pending",
            detail: "Run risk-modes to populate security.",
            sourceLabel: "Local SDK",
            segmentCount: 0,
            inspectCommand: DashboardLoader.copyCommand(root: DashboardLoader.defaultRepoRoot, command: DashboardLoader.securityCommand)
        ),
        tessl: TesslSignal(
            ok: false,
            cliAvailable: false,
            authenticated: false,
            displayStatus: "Not fetched",
            detail: "Tessl has not been probed yet.",
            cliVersion: nil,
            registryScore: nil,
            registryVersion: nil,
            registryQualityScore: nil,
            registryImpactScore: nil,
            registrySecurityLabel: nil,
            registryEvalCount: nil,
            registryImprovementMultiplier: nil,
            recoveryCommand: "tessl doctor"
        ),
        fleet: FleetSignal.placeholder,
        refreshedAt: Date(),
        error: nil
    )
}

private func globalShellQuoted(_ value: String) -> String {
    "'\(value.replacingOccurrences(of: "'", with: "'\\''"))'"
}

struct FleetSignal {
    var skillCount: Int
    var groupCount: Int
    var largestGroupName: String
    var largestGroupCount: Int
    var metadataCount: Int
    var referencesCount: Int
    var evalsCount: Int
    var selectedSkillPath: String
    var inventoryCommand: String

    static let placeholder = FleetSignal(
        skillCount: 0,
        groupCount: 0,
        largestGroupName: "unknown",
        largestGroupCount: 0,
        metadataCount: 0,
        referencesCount: 0,
        evalsCount: 0,
        selectedSkillPath: "Skills/agent-ops/improve-agent-native/SKILL.md",
        inventoryCommand: DashboardLoader.copyCommand(root: DashboardLoader.defaultRepoRoot, command: DashboardLoader.allSkillsInventoryCommand)
    )

    var title: String {
        skillCount > 0 ? "\(skillCount) local skills" : "Skill inventory pending"
    }

    var scanMode: String {
        "inventory"
    }

    var detail: String {
        guard skillCount > 0 else { return "Discovering Skills/**/SKILL.md before deeper checks." }
        return "\(groupCount) groups · meta \(coverage(metadataCount)) · refs \(coverage(referencesCount)) · evals \(coverage(evalsCount))"
    }
    var compactLine: String {
        guard skillCount > 0 else { return "Discovering local skills inventory" }
        return "\(skillCount) skills · \(groupCount) groups · \(largestGroupName) \(largestGroupCount)"
    }

    var tone: StatusTone {
        guard skillCount > 0 else { return .pending }
        if evalsCount < skillCount || referencesCount < skillCount || metadataCount < skillCount { return .warning }
        return .positive
    }

    private func coverage(_ count: Int) -> String {
        guard skillCount > 0 else { return "--" }
        return "\(count)/\(skillCount)"
    }
}

struct MetricSignal {
    var score: Int?
    var detail: String
    var source: String
    var command: String
    var statusOverride: String? = nil
    var displayScore: String { score.map { "\($0)%" } ?? "--" }
    var statusLabel: String { statusOverride ?? score.map { "\($0)%" } ?? "Pending" }
    var formulaValue: String { score.map { "\($0)" } ?? "--" }
    var sourceShort: String {
        if source.localizedCaseInsensitiveContains("package") { return "package verify" }
        if source.localizedCaseInsensitiveContains("scenario") { return "scenario-quality" }
        return source
    }
    var scoreFraction: Double { min(max(Double(score ?? 0) / 100.0, 0), 1) }
    var ratioLabel: String? {
        guard let first = detail.split(separator: " ").first.map(String.init),
              first.contains("/") else { return nil }
        return first
    }
    var tone: StatusTone {
        guard let score else { return .pending }
        if score >= 80 { return .positive }
        if score >= 60 { return .warning }
        return .danger
    }
    var compactDetail: String {
        if score != nil {
            if source.localizedCaseInsensitiveContains("package") {
                return "Package verified"
            }
            if source.localizedCaseInsensitiveContains("scenario") {
                return detail
                    .replacingOccurrences(of: " eval scenarios available.", with: " scenarios")
                    .replacingOccurrences(of: "Average across ", with: "")
            }
            return detail
        }
        if source.localizedCaseInsensitiveContains("package") {
            return "No package score yet"
        }
        if source.localizedCaseInsensitiveContains("scenario") {
            return "Scenario check not run"
        }
        return "Waiting for verification"
    }
    var shortDetail: String {
        compactDetail
            .replacingOccurrences(of: " scenarios", with: " scen.")
            .replacingOccurrences(of: "Package verified", with: "package")
            .replacingOccurrences(of: "Scenario check not run", with: "not run")
            .replacingOccurrences(of: "No package score yet", with: "no score")
    }
}

struct SecuritySignal {
    var score: Int?
    var status: String
    var detail: String
    var sourceLabel: String
    var segmentCount: Int
    var inspectCommand: String
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
    var statusDisplay: String {
        if status.localizedCaseInsensitiveContains("flag") {
            if let count = Int(riskLabel.prefix { $0.isNumber }) {
                return "\(count) risks"
            }
            return riskLabel.replacingOccurrences(of: " risk modes", with: " risks")
        }
        return status
    }
    var detailLine: String {
        if status.localizedCaseInsensitiveContains("flag") {
            return "\(riskLabel) from \(sourceLabel) evidence"
        }
        return compactDetail
    }
    var formulaValue: String { score.map { "\($0)" } ?? "--" }
    var scoreMathLine: String {
        guard let score else { return "pending" }
        return "100 - \(max(0, 100 - score)) = \(score)"
    }
    var penaltyLine: String {
        guard let score else { return "pending" }
        let penalty = max(0, 100 - score)
        return penalty > 0 ? "-\(penalty)" : "no penalty"
    }
    var severityLine: String {
        if status.localizedCaseInsensitiveContains("flag") {
            let withoutModes = riskLabel
                .replacingOccurrences(of: " risk modes", with: "")
                .replacingOccurrences(of: ".", with: "")
            if let colonIndex = withoutModes.firstIndex(of: ":") {
                return String(withoutModes[withoutModes.index(after: colonIndex)...]).trimmingCharacters(in: .whitespaces)
            }
            return withoutModes
        }
        return compactDetail
    }
    var sourceBadge: String {
        status.localizedCaseInsensitiveContains("flag") ? "from \(sourceLabel) receipt" : sourceLabel
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
    var authenticated: Bool
    var displayStatus: String
    var detail: String
    var cliVersion: String?
    var registryScore: Int?
    var registryVersion: String?
    var registryQualityScore: Int?
    var registryImpactScore: Int?
    var registrySecurityLabel: String?
    var registryEvalCount: Int?
    var registryImprovementMultiplier: Double?
    var recoveryCommand: String
    var compactDetail: String {
        if ok, let registryVersion { return "Registry metadata v\(registryVersion); local evidence remains separate." }
        if ok { return "Registry metadata connected; local evidence remains separate." }
        if !cliAvailable { return "Tessl CLI is not available on PATH." }
        if !authenticated { return "\(cliVersionLabel) · login unlocks registry search." }
        return detail
    }
    var registryDetailLine: String {
        if ok {
            var parts: [String] = []
            if let registryVersion { parts.append("v\(registryVersion)") }
            if let registryScore { parts.append("score \(registryScore)") }
            parts.append("separate proof")
            return parts.joined(separator: " · ")
        }
        return compactDetail
    }
    var cliVersionLabel: String {
        cliVersion.map { "tessl \($0)" } ?? "tessl CLI detected"
    }
    var versionBadge: String {
        cliVersion.map { "tessl \($0)" } ?? (cliAvailable ? "tessl CLI" : "no tessl")
    }
    var compactVersionBadge: String {
        cliVersion.map { "tessl \($0)" } ?? (cliAvailable ? "tessl" : "no tessl")
    }
    var tone: StatusTone {
        if ok { return .positive }
        if cliAvailable { return .warning }
        return .pending
    }
    var registryStatusLabel: String {
        if ok, registryScore != nil { return "Loaded" }
        return displayStatus
    }
    var registryStatusTone: StatusTone {
        if ok { return .pending }
        return tone
    }
    var actionTitle: String {
        if ok { return "Open Tessl registry" }
        if cliAvailable { return "Log in to Tessl" }
        return "Copy install help"
    }
    var copiedActionTitle: String {
        if ok { return "Open Tessl registry" }
        return "Copied \(recoveryCommand)"
    }
    var actionHelp: String {
        if ok { return "Open Tessl registry" }
        if cliAvailable { return "Open Terminal and run \(recoveryCommand)" }
        return "Copy \(recoveryCommand) to the clipboard"
    }
    var installLabel: String {
        ok ? "Install" : "Login"
    }
    var blockerSummary: String {
        if ok { return "registry ok" }
        if !cliAvailable { return "CLI missing" }
        if !authenticated { return "auth expired" }
        return displayStatus.lowercased()
    }
    var compactBlockerSummary: String {
        if ok { return "registry ok" }
        if !cliAvailable { return "no CLI" }
        if !authenticated { return "auth exp" }
        return displayStatus.lowercased()
    }
    var nextStepSentence: String {
        if ok { return "Registry metadata is available." }
        return "Run \(recoveryCommand); local Q/I/S stays current."
    }
    var registryResultLabel: String {
        if let registryScore { return "\(registryScore)" }
        if ok { return "Registry OK" }
        if !cliAvailable { return "No CLI" }
        if !authenticated { return "Locked" }
        return "Blocked"
    }
    var registryScoreTone: StatusTone {
        guard let registryScore else { return ok ? .pending : tone }
        if registryScore >= 80 { return .positive }
        if registryScore >= 60 { return .warning }
        return .danger
    }
    var registryImpactDisplay: String {
        if let registryImprovementMultiplier {
            return "\(String(format: "%.2f", registryImprovementMultiplier))x"
        }
        if let registryImpactScore {
            return "\(registryImpactScore)%"
        }
        return "--"
    }
    var registryImpactTone: StatusTone {
        if let registryImprovementMultiplier {
            return registryImprovementMultiplier >= 1 ? .positive : .danger
        }
        guard let registryImpactScore else { return .pending }
        if registryImpactScore >= 80 { return .positive }
        if registryImpactScore >= 60 { return .warning }
        return .danger
    }
    var registrySecurityDisplay: String {
        guard ok else { return displayStatus }
        guard let registrySecurityLabel else { return "Loaded" }
        if registrySecurityLabel.localizedCaseInsensitiveContains("pass") {
            return "Passed"
        }
        if registrySecurityLabel.localizedCaseInsensitiveContains("low") {
            return "Passed"
        }
        return registrySecurityLabel.capitalized
    }
    var registrySecurityTone: StatusTone {
        guard ok else { return tone }
        guard let registrySecurityLabel else { return .pending }
        if registrySecurityLabel.localizedCaseInsensitiveContains("pass") { return .positive }
        if registrySecurityLabel.localizedCaseInsensitiveContains("low") { return .positive }
        if registrySecurityLabel.localizedCaseInsensitiveContains("advisory") { return .advisory }
        return .danger
    }
    func driftLabel(localScore: Int?) -> String {
        guard let localScore else { return "--" }
        if let registryScore {
            let delta = registryScore - localScore
            if delta > 0 { return "+\(delta)" }
            return "\(delta)"
        }
        if ok { return "No score" }
        return "--"
    }
    func registryRelationLabel(localScore: Int?) -> String {
        guard localScore != nil else { return "local score pending" }
        guard let localScore, let registryScore else { return "No registry score" }
        let delta = registryScore - localScore
        if delta == 0 { return "Matches local" }
        if delta > 0 { return "\(delta) above local" }
        return "\(abs(delta)) below local"
    }
    func registryComparisonDetail(localScore: Int?) -> String {
        if ok, let breakdown = registryBreakdownLine {
            if localScore == nil {
                return breakdown
            }
            return "\(breakdown) · \(registryRelationLabel(localScore: localScore))"
        }
        if ok {
            return "Registry metadata · \(registryRelationLabel(localScore: localScore))"
        }
        return nextStepSentence
    }
    func headerBadgeLabel(localScore: Int?) -> String? {
        guard ok, let registryScore else { return nil }
        return "Tessl \(registryScore) \(driftLabel(localScore: localScore))"
    }
    func headerBadgeTone(localScore: Int?) -> StatusTone {
        guard ok else { return .pending }
        guard let localScore, let registryScore else { return .positive }
        if registryScore < localScore { return .warning }
        return .positive
    }
    var registryBreakdownLine: String? {
        guard ok else { return nil }
        var parts: [String] = []
        if let registryQualityScore { parts.append("Q\(registryQualityScore)") }
        if let registryImpactScore { parts.append("I\(registryImpactScore)") }
        if let registrySecurityLabel { parts.append("S:\(registrySecurityLabel.uppercased())") }
        if let registryEvalCount { parts.append("E\(registryEvalCount)") }
        if let registryImprovementMultiplier {
            parts.append("x\(String(format: "%.2f", registryImprovementMultiplier))")
        }
        return parts.isEmpty ? nil : parts.joined(separator: " ")
    }
}

struct DashboardLoader {
    static let defaultRepoRoot = URL(fileURLWithPath: "/Users/jamiecraik/dev/agent-skills")
    static let defaultSkillPath = "Skills/agent-ops/improve-agent-native/SKILL.md"
    static let packageCommand = "./bin/ask skills package verify Skills/agent-ops/improve-agent-native --json --robot"
    static let impactCommand = "./bin/ask sdk eval scenario-quality Skills/agent-ops/improve-agent-native --preview --json --robot"
    static let securityCommand = "./bin/ask sdk security risk-modes Skills/agent-ops/improve-agent-native --preview --json --robot"
    static let allSkillsInventoryCommand = "find Skills -name SKILL.md -print | sort"
    static func packageCommand(for skillPath: String) -> String {
        "./bin/ask skills package verify \(shellQuoted(skillPath)) --json --robot"
    }

    static func impactCommand(for skillPath: String) -> String {
        "./bin/ask sdk eval scenario-quality \(shellQuoted(skillPath)) --preview --json --robot"
    }

    static func securityCommand(for skillPath: String) -> String {
        "./bin/ask sdk security risk-modes \(shellQuoted(skillPath)) --preview --json --robot"
    }

    static func localEvidenceCommand(root: URL, skillPath: String = defaultSkillPath) -> String {
        copyCommand(root: root, command: labelledCommand([
            ("quality package verify", packageCommand(for: skillPath)),
            ("impact scenario-quality", impactCommand(for: skillPath)),
            ("security risk-modes", securityCommand(for: skillPath))
        ]))
    }

    static func copyCommand(root: URL, command: String) -> String {
        "cd \(shellQuoted(root.path)) && \(command)"
    }

    private static func shellQuoted(_ value: String) -> String {
        "'\(value.replacingOccurrences(of: "'", with: "'\\''"))'"
    }

    private static func labelledCommand(_ steps: [(String, String)]) -> String {
        steps.map { label, command in
            "printf '\\n== \(label) ==\\n'; \(command)"
        }.joined(separator: "; ")
    }

    func load() async throws -> SkillDashboard {
        let root = try findRepoRoot()
        let selectedSkillPath = try findSelectedSkillPath(root: root)
        let metadata = try SkillMetadata.load(from: root.appendingPathComponent(selectedSkillPath))
        let registryPath = "jscraik/\(metadata.name)"
        let packageCommand = Self.packageCommand(for: selectedSkillPath)
        let impactCommand = Self.impactCommand(for: selectedSkillPath)
        let securityCommand = Self.securityCommand(for: selectedSkillPath)

        async let packageResult = run(root: root, command: packageCommand)
        async let scenarioResult = run(root: root, command: impactCommand)
        async let securityResult = run(root: root, command: securityCommand)
        async let tesslResult = tesslSignal(root: root, registryPath: registryPath)

        let package = await packageResult
        let scenario = await scenarioResult
        let security = await securityResult
        let tessl = await tesslResult

        return SkillDashboard(
            displayName: metadata.name,
            version: metadata.version,
            description: metadata.description,
            registryPath: registryPath,
            repoPath: root.path,
            installCommand: "tessl install \(registryPath)",
            localEvidenceCommand: Self.localEvidenceCommand(root: root, skillPath: selectedSkillPath),
            reviewedText: "Local SDK evidence",
            deltaText: tessl.ok ? "Tessl" : "Local SDK",
            quality: qualitySignal(from: package, root: root, command: packageCommand),
            impact: impactSignal(from: scenario, root: root, command: impactCommand),
            security: securitySignal(from: security, root: root, command: securityCommand),
            tessl: tessl,
            fleet: fleetSignal(root: root, selectedSkillPath: selectedSkillPath),
            refreshedAt: Date(),
            error: nil
        )
    }

    func loadSync() throws -> SkillDashboard {
        let root = try findRepoRoot()
        let selectedSkillPath = try findSelectedSkillPath(root: root)
        let metadata = try SkillMetadata.load(from: root.appendingPathComponent(selectedSkillPath))
        let registryPath = "jscraik/\(metadata.name)"
        let packageCommand = Self.packageCommand(for: selectedSkillPath)
        let impactCommand = Self.impactCommand(for: selectedSkillPath)
        let securityCommand = Self.securityCommand(for: selectedSkillPath)
        let package = Shell.run(packageCommand, cwd: root, timeout: 45)
        let scenario = Shell.run(impactCommand, cwd: root, timeout: 45)
        let security = Shell.run(securityCommand, cwd: root, timeout: 45)
        return SkillDashboard(
            displayName: metadata.name,
            version: metadata.version,
            description: metadata.description,
            registryPath: registryPath,
            repoPath: root.path,
            installCommand: "tessl install \(registryPath)",
            localEvidenceCommand: Self.localEvidenceCommand(root: root, skillPath: selectedSkillPath),
            reviewedText: "Local SDK evidence",
            deltaText: "Local SDK",
            quality: qualitySignal(from: package, root: root, command: packageCommand),
            impact: impactSignal(from: scenario, root: root, command: impactCommand),
            security: securitySignal(from: security, root: root, command: securityCommand),
            tessl: tesslSignalSync(root: root, registryPath: registryPath),
            fleet: fleetSignal(root: root, selectedSkillPath: selectedSkillPath),
            refreshedAt: Date(),
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

    private func findSelectedSkillPath(root: URL) throws -> String {
        let environment = ProcessInfo.processInfo.environment
        let rawPath = environment["AGENT_SKILL_PATH"] ?? environment["SELECTED_SKILL_PATH"] ?? Self.defaultSkillPath
        let relativePath = rawPath.hasPrefix(root.path + "/")
            ? String(rawPath.dropFirst(root.path.count + 1))
            : rawPath
        guard relativePath.hasPrefix("Skills/"),
              relativePath.hasSuffix("/SKILL.md"),
              FileManager.default.fileExists(atPath: root.appendingPathComponent(relativePath).path) else {
            return Self.defaultSkillPath
        }
        return relativePath
    }

    private func run(root: URL, command: String) async -> CommandResult {
        await Task.detached(priority: .utility) { Shell.run(command, cwd: root, timeout: 45) }.value
    }

    private func fleetSignal(root: URL, selectedSkillPath: String) -> FleetSignal {
        let skillsRoot = root.appendingPathComponent("Skills")
        let fileManager = FileManager.default
        guard let enumerator = fileManager.enumerator(
            at: skillsRoot,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        ) else {
            return FleetSignal(
                skillCount: 0,
                groupCount: 0,
                largestGroupName: "missing",
                largestGroupCount: 0,
                metadataCount: 0,
                referencesCount: 0,
                evalsCount: 0,
                selectedSkillPath: selectedSkillPath,
                inventoryCommand: Self.copyCommand(root: root, command: Self.allSkillsInventoryCommand)
            )
        }

        var groups: [String: Int] = [:]
        var skillCount = 0
        var metadataCount = 0
        var referencesCount = 0
        var evalsCount = 0
        for case let url as URL in enumerator where url.lastPathComponent == "SKILL.md" {
            skillCount += 1
            let text = (try? String(contentsOf: url, encoding: .utf8)) ?? ""
            if text.contains("\nmetadata:") || text.hasPrefix("metadata:") {
                metadataCount += 1
            }
            let referencesURL = url.deletingLastPathComponent().appendingPathComponent("references")
            var isDirectory: ObjCBool = false
            if fileManager.fileExists(atPath: referencesURL.path, isDirectory: &isDirectory), isDirectory.boolValue {
                referencesCount += 1
                if fileManager.fileExists(atPath: referencesURL.appendingPathComponent("evals.yaml").path) {
                    evalsCount += 1
                }
            }
            let relative = url.path.replacingOccurrences(of: root.path + "/", with: "")
            let parts = relative.split(separator: "/")
            let group = parts.dropFirst().first.map(String.init) ?? "unknown"
            groups[group, default: 0] += 1
        }
        let largest = groups.sorted { lhs, rhs in
            if lhs.value == rhs.value { return lhs.key < rhs.key }
            return lhs.value > rhs.value
        }.first

        return FleetSignal(
            skillCount: skillCount,
            groupCount: groups.count,
            largestGroupName: largest?.key ?? "none",
            largestGroupCount: largest?.value ?? 0,
            metadataCount: metadataCount,
            referencesCount: referencesCount,
            evalsCount: evalsCount,
            selectedSkillPath: selectedSkillPath,
            inventoryCommand: Self.copyCommand(root: root, command: Self.allSkillsInventoryCommand)
        )
    }

    private func tesslSignal(root: URL, registryPath: String) async -> TesslSignal {
        await Task.detached(priority: .utility) {
            tesslSignalSync(root: root, registryPath: registryPath)
        }.value
    }

    private func tesslSignalSync(root: URL, registryPath: String) -> TesslSignal {
        if let fixture = tesslFixtureSignal(registryPath: registryPath) {
            return fixture
        }

        let cli = Shell.run("command -v tessl", cwd: root, timeout: 5)
        guard cli.exitCode == 0 else {
            return TesslSignal(
                ok: false,
                cliAvailable: false,
                authenticated: false,
                displayStatus: "CLI missing",
                detail: "Tessl CLI was not found on PATH.",
                cliVersion: nil,
                registryScore: nil,
                registryVersion: nil,
                registryQualityScore: nil,
                registryImpactScore: nil,
                registrySecurityLabel: nil,
                registryEvalCount: nil,
                registryImprovementMultiplier: nil,
                recoveryCommand: "tessl doctor"
            )
        }

        let version = Shell.run("tessl --version", cwd: root, timeout: 5).stdout.trimmingCharacters(in: .whitespacesAndNewlines)
        let whoami = Shell.run("tessl whoami", cwd: root, timeout: 15)
        guard whoami.exitCode == 0 else {
            let authExpired = whoami.combinedOutput.localizedCaseInsensitiveContains("401")
                || whoami.combinedOutput.localizedCaseInsensitiveContains("login")
            return TesslSignal(
                ok: false,
                cliAvailable: true,
                authenticated: false,
                displayStatus: authExpired ? "Auth expired" : "Auth blocked",
                detail: whoami.shortFailure,
                cliVersion: version.isEmpty ? nil : version,
                registryScore: nil,
                registryVersion: nil,
                registryQualityScore: nil,
                registryImpactScore: nil,
                registrySecurityLabel: nil,
                registryEvalCount: nil,
                registryImprovementMultiplier: nil,
                recoveryCommand: "tessl login"
            )
        }

        let searchCommand = "tessl search --json --type skills \(Self.shellQuoted(registryPath))"
        let search = Shell.run(searchCommand, cwd: root, timeout: 20)
        guard search.exitCode == 0 else {
            return TesslSignal(
                ok: false,
                cliAvailable: true,
                authenticated: true,
                displayStatus: "Search blocked",
                detail: search.shortFailure,
                cliVersion: version.isEmpty ? nil : version,
                registryScore: nil,
                registryVersion: nil,
                registryQualityScore: nil,
                registryImpactScore: nil,
                registrySecurityLabel: nil,
                registryEvalCount: nil,
                registryImprovementMultiplier: nil,
                recoveryCommand: "tessl search --type skills \(registryPath)"
            )
        }
        let payload = search.json
        let registryScore = registryScore(from: payload)
        let registryVersion = payload?.firstString(for: ["latestVersion", "version", "latest_version", "published_version", "package_version"])
        let registryQualityScore = registryPercent(from: payload, key: "quality")
        let registryImpactScore = registryPercent(from: payload, key: "impact")
        let registrySecurityLabel = payload?.firstString(for: ["security"])
        let registryEvalCount = payload?.firstInt(for: ["count"])
        let registryImprovementMultiplier = payload?.firstDouble(for: ["improvementMultiplier"])

        return TesslSignal(
            ok: true,
            cliAvailable: true,
            authenticated: true,
            displayStatus: registryScore == nil ? "Connected" : "Scored",
            detail: registryScore.map { "Registry returned score \($0); local evidence remains separate." } ?? "Registry search returned metadata for this authenticated Tessl session.",
            cliVersion: version.isEmpty ? nil : version,
            registryScore: registryScore,
            registryVersion: registryVersion,
            registryQualityScore: registryQualityScore,
            registryImpactScore: registryImpactScore,
            registrySecurityLabel: registrySecurityLabel,
            registryEvalCount: registryEvalCount,
            registryImprovementMultiplier: registryImprovementMultiplier,
            recoveryCommand: "tessl install \(registryPath)"
        )
    }

    private func registryScore(from payload: JSONNode?) -> Int? {
        guard let payload else { return nil }
        for key in ["aggregate", "validated_score", "validation_score", "quality_score", "score", "rating"] {
            if let rawScore = payload.firstDouble(for: [key]) {
                let normalizedScore = rawScore <= 1.0 ? rawScore * 100.0 : rawScore
                let score = Int(normalizedScore.rounded())
                if (0...100).contains(score) { return score }
            }
        }
        for key in ["validated_score", "validation_score", "quality_score", "score", "rating"] {
            if let score = payload.firstInt(for: [key]), (0...100).contains(score) {
                return score
            }
        }
        return nil
    }

    private func registryPercent(from payload: JSONNode?, key: String) -> Int? {
        guard let rawValue = payload?.firstDouble(for: [key]) else { return nil }
        let normalizedValue = rawValue <= 1.0 ? rawValue * 100.0 : rawValue
        let value = Int(normalizedValue.rounded())
        return (0...100).contains(value) ? value : nil
    }

    private func tesslFixtureSignal(registryPath: String) -> TesslSignal? {
        let environment = ProcessInfo.processInfo.environment
        guard environment["TESSL_REGISTRY_FIXTURE"] == "1"
                || environment["TESSL_REGISTRY_FIXTURE_SCORE"] != nil else { return nil }
        let rawScore = environment["TESSL_REGISTRY_FIXTURE_SCORE"]
        let score = rawScore.flatMap(Int.init).flatMap { (0...100).contains($0) ? $0 : nil }
        return TesslSignal(
            ok: true,
            cliAvailable: true,
            authenticated: true,
            displayStatus: score == nil ? "Connected" : "Scored",
            detail: score.map { "Fixture registry score \($0); local evidence remains separate." } ?? "Fixture registry metadata connected; local evidence remains separate.",
            cliVersion: environment["TESSL_REGISTRY_FIXTURE_CLI_VERSION"] ?? "fixture",
            registryScore: score,
            registryVersion: environment["TESSL_REGISTRY_FIXTURE_VERSION"],
            registryQualityScore: environment["TESSL_REGISTRY_FIXTURE_QUALITY"].flatMap(Int.init),
            registryImpactScore: environment["TESSL_REGISTRY_FIXTURE_IMPACT"].flatMap(Int.init),
            registrySecurityLabel: environment["TESSL_REGISTRY_FIXTURE_SECURITY"],
            registryEvalCount: environment["TESSL_REGISTRY_FIXTURE_EVALS"].flatMap(Int.init),
            registryImprovementMultiplier: environment["TESSL_REGISTRY_FIXTURE_MULTIPLIER"].flatMap(Double.init),
            recoveryCommand: "tessl install \(registryPath)"
        )
    }

    private func qualitySignal(from result: CommandResult, root: URL, command rawCommand: String) -> MetricSignal {
        let command = Self.copyCommand(root: root, command: rawCommand)
        guard result.exitCode == 0, let payload = result.json else {
            return MetricSignal(
                score: nil,
                detail: "Blocked: \(result.shortFailure)",
                source: "Local SDK package verify",
                command: command
            )
        }
        let status = payload.firstString(for: ["status"]) ?? "unknown"
        return MetricSignal(
            score: status == "success" ? 100 : 70,
            detail: "Package verify reported \(status).",
            source: "Local SDK package verify",
            command: command
        )
    }

    private func impactSignal(from result: CommandResult, root: URL, command rawCommand: String) -> MetricSignal {
        let command = Self.copyCommand(root: root, command: rawCommand)
        guard result.exitCode == 0, let payload = result.json else {
            return MetricSignal(
                score: nil,
                detail: "Blocked: \(result.shortFailure)",
                source: "Local SDK scenario-quality",
                command: command
            )
        }
        let total = payload.firstInt(for: ["scenario_count", "case_count", "total"])
        let ready = payload.firstInt(for: ["promotion_ready_count", "passed_count", "ready_count"])
        if let total, let ready, total > 0 {
            let score = Int((Double(ready) / Double(total) * 100.0).rounded())
            return MetricSignal(
                score: score,
                detail: "\(ready)/\(total) eval scenarios available.",
                source: "Local SDK scenario-quality",
                command: command,
                statusOverride: "\(ready)/\(total)"
            )
        }
        let status = payload.firstString(for: ["status"]) ?? "success"
        return MetricSignal(
            score: nil,
            detail: "Inspect: scenario-quality returned \(status), but count fields were unavailable.",
            source: "Local SDK scenario-quality",
            command: command
        )
    }

    private func securitySignal(from result: CommandResult, root: URL, command rawCommand: String) -> SecuritySignal {
        let inspectCommand = Self.copyCommand(root: root, command: rawCommand)
        guard result.exitCode == 0, let payload = result.json else {
            return SecuritySignal(
                score: nil,
                status: "Pending",
                detail: "Blocked: \(result.shortFailure)",
                sourceLabel: "Local SDK",
                segmentCount: 0,
                inspectCommand: inspectCommand
            )
        }
        let receiptPath = ["data", "skills_sdk_risk_mode_taxonomy", "receipt"]
        let status = payload.string(at: receiptPath + ["status"]) ?? payload.firstString(for: ["status"]) ?? "success"
        let detectedModes = Set(payload.stringArray(at: receiptPath + ["detected_modes"]))
        let detectedRows = payload.arrayOfDictionaries(at: receiptPath + ["mode_results"]).filter { row in
            guard (row["status"] as? String) == "detected" else { return false }
            guard !detectedModes.isEmpty, let mode = row["mode"] as? String else { return true }
            return detectedModes.contains(mode)
        }
        let severities = detectedRows.compactMap { $0["severity"] as? String }
        if !detectedRows.isEmpty {
            let score = securityScore(for: severities)
            let detail = "\(detectedRows.count) risk modes: \(severitySummary(for: severities))."
            return SecuritySignal(
                score: score,
                status: "Flagged",
                detail: detail,
                sourceLabel: "Local SDK risk-modes",
                segmentCount: min(max(detectedRows.count, 1), 5),
                inspectCommand: inspectCommand
            )
        }
        let detail = "No risk mode signals detected."
        return SecuritySignal(
            score: status == "success" ? 100 : 70,
            status: status == "success" ? "Passed" : status.capitalized,
            detail: detail,
            sourceLabel: "Local SDK risk-modes",
            segmentCount: status == "success" ? 4 : 2,
            inspectCommand: inspectCommand
        )
    }

    private func securityScore(for severities: [String]) -> Int {
        let penalty = severities.reduce(0) { total, severity in
            switch severity.lowercased() {
            case "critical": return total + 35
            case "high": return total + 15
            case "medium": return total + 8
            case "low": return total + 4
            default: return total + 10
            }
        }
        return max(0, 100 - penalty)
    }

    private func severitySummary(for severities: [String]) -> String {
        let grouped = Dictionary(grouping: severities.map { $0.lowercased() }, by: { $0 })
        let order = ["critical", "high", "medium", "low"]
        let parts = order.compactMap { severity -> String? in
            guard let count = grouped[severity]?.count, count > 0 else { return nil }
            return "\(count) \(severity)"
        }
        return parts.isEmpty ? "severity unavailable" : parts.joined(separator: ", ")
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

    func firstDouble(for keys: [String]) -> Double? {
        for key in keys {
            if let double = findValue(named: key, in: value) as? Double { return double }
            if let int = findValue(named: key, in: value) as? Int { return Double(int) }
        }
        return nil
    }

    func allStrings(for key: String) -> [String] {
        var results: [String] = []
        collectStrings(named: key, from: value, into: &results)
        return results
    }

    func string(at path: [String]) -> String? {
        value(at: path) as? String
    }

    func stringArray(at path: [String]) -> [String] {
        value(at: path) as? [String] ?? []
    }

    func arrayOfDictionaries(at path: [String]) -> [[String: Any]] {
        value(at: path) as? [[String: Any]] ?? []
    }

    private func value(at path: [String]) -> Any? {
        var current: Any? = value
        for key in path {
            guard let dictionary = current as? [String: Any] else { return nil }
            current = dictionary[key]
        }
        return current
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
