import Foundation
import ImproveAgentNativeMenuBarCore
import XCTest

final class ShellTests: XCTestCase {
    func testRunCapturesLargeStdoutAndStderrWithoutDeadlock() {
        let byteCount = 3_000_000
        let command = """
        python3 - <<'PY'
        import sys
        count = \(byteCount)
        sys.stdout.write("x" * count)
        sys.stdout.flush()
        sys.stderr.write("y" * count)
        sys.stderr.flush()
        PY
        """

        let result = Shell.run(command, cwd: URL(fileURLWithPath: "/private/tmp"), timeout: 10)

        XCTAssertEqual(result.exitCode, 0)
        XCTAssertEqual(result.stdout.utf8.count, byteCount)
        XCTAssertEqual(result.stderr.utf8.count, byteCount)
        XCTAssertTrue(result.stdout.allSatisfy { $0 == "x" })
        XCTAssertTrue(result.stderr.allSatisfy { $0 == "y" })
    }
}
