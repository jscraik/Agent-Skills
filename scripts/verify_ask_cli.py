#!/usr/bin/env python3
import subprocess
import json
import sys
from pathlib import Path

def run_ca_test(name, cmd):
    print(f"Running {name}...", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "--json" not in cmd:
        print("FAILED")
        print(f"Error: {result.stderr}")
        return False
    
    if "--json" in cmd:
        try:
            data = json.loads(result.stdout)
            if data.get("status") == "success":
                print("PASSED")
                return True
            else:
                # Some expected failures might have status: error
                if "ERR_PATH_TRAVERSAL" in str(data):
                    print("PASSED (Expected Error)")
                    return True
                print("FAILED")
                print(f"JSON Status: {data.get('status')}")
                return False
        except json.JSONDecodeError:
            print("FAILED (Invalid JSON)")
            return False
    
    print("PASSED")
    return True

def main():
    repo_root = Path(__file__).resolve().parents[1]
    ask_bin = str(repo_root / "bin" / "ask")
    
    tests = [
        ("CA1: JSON Envelope", [ask_bin, "skills", "list", "--json"]),
        ("CA1: Context Discovery", [ask_bin, "repo", "status", "--json"]),
        ("CA2: Dry-run Protection", [ask_bin, "skills", "sync", "--dry-run", "--json"]),
    ]
    
    success = True
    for name, cmd in tests:
        if not run_ca_test(name, cmd):
            success = False
            
    if success:
        print("\n✅ All CA tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
