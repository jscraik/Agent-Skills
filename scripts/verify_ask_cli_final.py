#!/usr/bin/env python3
import subprocess
import json
import sys
from pathlib import Path

def run_ca_test(name, cmd):
    print(f"Running {name}...", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "--json" in cmd:
        try:
            data = json.loads(result.stdout)
            if data.get("status") == "success":
                print("PASSED")
                return True
            else:
                print(f"FAILED (Status: {data.get('status')})")
                if data.get("errors"):
                    print(f"  Error: {data['errors'][0]['message']}")
                return False
        except json.JSONDecodeError as e:
            print(f"FAILED (Invalid JSON: {e})")
            print(f"STDOUT: {result.stdout}")
            return False
    
    if result.returncode == 0:
        print("PASSED")
        return True
    else:
        print(f"FAILED (Exit Code: {result.returncode})")
        return False

def main():
    repo_root = Path(__file__).resolve().parents[1]
    ask_bin = str(repo_root / "bin" / "ask")
    
    tests = [
        ("CA1: JSON Envelope", [ask_bin, "skills", "list", "--json"]),
        ("CA1: Context Discovery", [ask_bin, "repo", "status", "--json"]),
        ("CA2: Dry-run Protection", [ask_bin, "skills", "sync", "--dry-run", "--json"]),
        ("CA4: Error Mapping", [ask_bin, "skills", "audit", "/etc/passwd", "--json"]),
        ("CA5: Redundancy Catch", [ask_bin, "skills", "fold", "resolve-todo-parallel", "resolve-pr-parallel", "--json"]),
    ]
    
    success = True
    for name, cmd in tests:
        test_passed = run_ca_test(name, cmd)
        if "CA4" in name:
            # CA4 tests error handling - we expect it to fail (return False)
            # If it returns True, the error mapping isn't working correctly
            if test_passed:
                print("  -> CA4 unexpectedly passed - error mapping may be broken")
                success = False
            else:
                print("  -> CA4 correctly detected invalid path (expected failure)")
        elif not test_passed:
            success = False
            
    if success:
        print("\n✅ All core CA tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
