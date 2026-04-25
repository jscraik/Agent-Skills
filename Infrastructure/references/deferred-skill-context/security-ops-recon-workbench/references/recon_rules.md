# recon.rules -- Codex execpolicy sample (Starlark)

# Allow common read-only tooling
prefix_rule(pattern=["otool"], decision="allow")
prefix_rule(pattern=["nm"], decision="allow")
prefix_rule(pattern=["strings"], decision="allow")
prefix_rule(pattern=["codesign"], decision="allow")
prefix_rule(pattern=["xcrun"], decision="allow")

# Prompt for potentially sensitive operations
prefix_rule(pattern=["tcpdump"], decision="prompt")
prefix_rule(pattern=["lsof"], decision="prompt")

# Block outbound exfil by default outside sandbox
prefix_rule(pattern=["curl"], decision="forbidden")
prefix_rule(pattern=["ssh"], decision="forbidden")

# Injection/debug tools should be opt-in
prefix_rule(pattern=["lldb"], decision="prompt")

# Destructive commands blocked
prefix_rule(pattern=["rm"], decision="forbidden")
prefix_rule(pattern=["sudo"], decision="prompt")
