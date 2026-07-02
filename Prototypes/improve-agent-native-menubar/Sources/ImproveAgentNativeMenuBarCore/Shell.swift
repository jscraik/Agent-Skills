import Foundation

public struct CommandResult: Sendable {
    public var exitCode: Int32
    public var stdout: String
    public var stderr: String

    public init(exitCode: Int32, stdout: String, stderr: String) {
        self.exitCode = exitCode
        self.stdout = stdout
        self.stderr = stderr
    }

    public var combinedOutput: String { stdout + "\n" + stderr }
    public var shortFailure: String { String((stderr.isEmpty ? stdout : stderr).prefix(110)).replacingOccurrences(of: "\n", with: " ") }
    public var json: JSONNode? {
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

public enum Shell {
    public static func run(_ command: String, cwd: URL, timeout: TimeInterval) -> CommandResult {
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
        let stdoutData = LockedData()
        let stderrData = LockedData()
        do {
            try process.run()
        } catch {
            return CommandResult(exitCode: -1, stdout: "", stderr: error.localizedDescription)
        }
        outputGroup.enter()
        DispatchQueue.global(qos: .utility).async {
            stdoutData.set(stdoutHandle.readDataToEndOfFile())
            outputGroup.leave()
        }
        outputGroup.enter()
        DispatchQueue.global(qos: .utility).async {
            stderrData.set(stderrHandle.readDataToEndOfFile())
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
            stdout: String(data: stdoutData.value, encoding: .utf8) ?? "",
            stderr: String(data: stderrData.value, encoding: .utf8) ?? ""
        )
    }
}

private final class LockedData: @unchecked Sendable {
    private let lock = NSLock()
    private var storage = Data()

    var value: Data {
        lock.lock()
        defer { lock.unlock() }
        return storage
    }

    func set(_ data: Data) {
        lock.lock()
        storage = data
        lock.unlock()
    }
}

public struct JSONNode {
    public var value: Any
    public init(_ value: Any) { self.value = value }

    public func firstString(for keys: [String]) -> String? {
        for key in keys {
            if let value = findValue(named: key, in: value) as? String { return value }
        }
        return nil
    }

    public func firstInt(for keys: [String]) -> Int? {
        for key in keys {
            if let int = findValue(named: key, in: value) as? Int { return int }
            if let double = findValue(named: key, in: value) as? Double { return Int(double) }
        }
        return nil
    }

    public func allStrings(for key: String) -> [String] {
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
