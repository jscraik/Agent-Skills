#!/usr/bin/env python3
"""Test GetAllSkills with a real (non-symlink) directory."""
import struct
import urllib.request

def encode_string_field(field_num, value):
    tag = (field_num << 3) | 2
    encoded_value = value.encode('utf-8') if isinstance(value, str) else value
    tag_bytes = []
    t = tag
    while t > 127:
        tag_bytes.append((t & 0x7F) | 0x80)
        t >>= 7
    tag_bytes.append(t)
    length = len(encoded_value)
    len_bytes = []
    while length > 127:
        len_bytes.append((length & 0x7F) | 0x80)
        length >>= 7
    len_bytes.append(length)
    return bytes(tag_bytes) + bytes(len_bytes) + encoded_value

def grpc_frame(msg):
    return bytes([0]) + struct.pack('>I', len(msg)) + msg

# Test with the real (no-symlink) temp dir
for label, path in [
    ("real_test_dir",   "/tmp/skills-test/"),
    ("agents_skills",   "/Users/jamiecraik/dev/agent-skills/.agents/skills/"),
    ("utilities_real",  "/Users/jamiecraik/dev/agent-skills/utilities/"),
    ("interview_real",  "/Users/jamiecraik/dev/agent-skills/interview/"),
]:
    msg = encode_string_field(3, path)   # field 3 = skills_paths (repeated)
    frame = grpc_frame(msg)
    req = urllib.request.Request(
        'http://localhost:55999/exa.language_server_pb.LanguageServerService/GetAllSkills',
        data=frame,
        headers={
            'Content-Type': 'application/grpc+proto',
            'x-codeium-csrf-token': '8aef9d57-da98-4dd8-a9e9-b634d78878ce',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read()
            # gRPC: 5-byte header, then protobuf payload
            payload = body[5:] if len(body) >= 5 else body
            print(f"[{label}] -> {len(body)} bytes | proto: {payload.hex()!r}")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")
