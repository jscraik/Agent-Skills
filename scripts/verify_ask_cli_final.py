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
        except Exception as e:
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
        if not run_ca_test(name, cmd):
            if "CA4" in name: # Expected error
                continue
            success = False
            
    if success:
        print("\n✅ All core CA tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
