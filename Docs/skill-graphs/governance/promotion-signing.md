# Promotion Decision Signing

## Table of Contents

- [Overview](#overview)
- [Option 1 (current): HMAC-SHA256 shared-secret signing](#option-1-current-hmac-sha256-shared-secret-signing)
- [Option 2 (migration path): Ed25519 asymmetric signing](#option-2-migration-path-ed25519-asymmetric-signing)
- [CI wiring](#ci-wiring)
- [Key rotation](#key-rotation)
- [Error codes](#error-codes)

---

## Overview

**Finding C-01** from the security best-practices report identified that the canonical
lesson write path lacked a cryptographic trust boundary: any process with write access
to `Infrastructure/artifacts/skill-graphs/runs/<run_id>/promotion_decision.json` could mutate the
decision without detection.

Signing closes this gap:

1. `human_promote_recursive_run.sh` signs the decision and writes `<decision_tmp>.sig`.
2. `validate_recursive_promotion.py` verifies the sig **before** any schema or policy check.
3. If verification fails, the run is blocked with `E_DECISION_SIG_MISMATCH`.

---

## Option 1 (current): HMAC-SHA256 shared-secret signing

### How it works

```
sign:   HMAC-SHA256(key=PROMOTION_SIGNING_KEY, msg=canonical_json(decision))
verify: constant-time compare via hmac.compare_digest
format: "hmac-sha256:<hex>\n" written to <decision_tmp>.sig
```

Canonical JSON: `json.dumps(obj, sort_keys=True, separators=(",", ":"))` — deterministic
across Python versions, no whitespace variation.

### Setup

1. Generate a strong random key (32+ bytes of entropy):

   ```bash
   openssl rand -hex 32
   ```

2. Store it as a GitHub Actions secret named `PROMOTION_SIGNING_KEY`.
3. Set `PROMOTION_SIG_REQUIRED=1` in CI to hard-fail on unsigned decisions.

### Threat model

| Threat                              | Mitigation                                                        |
| ----------------------------------- | ----------------------------------------------------------------- |
| Decision file mutated after signing | HMAC mismatch → `E_DECISION_SIG_MISMATCH` blocks canonical write  |
| Key leaked in logs                  | Key is never printed; only the hex MAC is written to the sig file |
| Timing attack on MAC comparison     | `hmac.compare_digest` (constant-time)                             |
| Key reuse across runs               | Each decision body is different; no nonce needed for integrity    |

### Limitations

- Shared secret: anyone with the key can forge a valid signature.
- Key must be distributed to every CI runner that calls the promotion script.
- Key rotation requires updating the secret and all outstanding unsigned runs.

---

## Option 2 (migration path): Ed25519 asymmetric signing

> **Status:** Planned. Implement when the team requires reviewer-identity binding
> (i.e. each reviewer signs with their own private key, verified against a public
> key checked into the repo).

### Design

```
sign:   ed25519.sign(private_key, sha256(canonical_json(decision)))
verify: ed25519.verify(public_key, sha256(canonical_json(decision)), sig)
format: base64url(sig) written to <decision_tmp>.sig
```

### Steps to migrate

1. **Generate a keypair per environment** (or per reviewer for full identity binding):

   ```bash
   # Using Python's built-in cryptography (pip install cryptography)
   python3 - <<'PY'
   from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
   from cryptography.hazmat.primitives.serialization import (
       Encoding, PublicFormat, PrivateFormat, NoEncryption
   )
   import base64, pathlib

   key = Ed25519PrivateKey.generate()
   priv_pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
   pub_pem  = key.public_key().private_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
   # NOTE: public_key() does NOT have private_bytes; use public_bytes() instead:
   pub_pem  = key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

   pathlib.Path("promotion-signing.pem").write_bytes(priv_pem)
   pathlib.Path("promotion-signing.pub.pem").write_bytes(pub_pem)
   print("Public key:", base64.b64encode(pub_pem).decode())
   PY
   ```

2. **Store private key** as a CI secret (`PROMOTION_SIGNING_PRIVATE_KEY_PEM`).
   Never commit private keys.

3. **Check public key into repo** at
   `docs/skill-graphs/governance/promotion-signing.pub.pem` alongside a sha256
   signature file (same pattern as `recursive-loop-approvers.sig`).

4. **Update `human_promote_recursive_run.sh`**: replace `hmac.new(...)` with
   `Ed25519PrivateKey.sign(sha256(canonical))`.

5. **Update `validate_recursive_promotion.py`**: replace `verify_decision_hmac`
   with an Ed25519 verify call using the checked-in public key.

6. **Dual-verify window**: during migration, accept both HMAC and Ed25519 sigs
   (check `hmac-sha256:` vs `ed25519:` prefix in the sig file).

### Advantages over option 1

- Private key never leaves the CI environment.
- Public key is auditable in the repo — no shared secret to distribute.
- Supports per-reviewer identity binding (each reviewer has their own keypair).

---

## CI wiring

Add to `.github/workflows/recursive-promotion-gate.yml` (job env):

```yaml
env:
  PROMOTION_SIGNING_KEY: ${{ secrets.PROMOTION_SIGNING_KEY }}
  PROMOTION_SIG_REQUIRED: "1"
```

The shell script picks up `PROMOTION_SIGNING_KEY` automatically.
The validator picks up `PROMOTION_SIG_REQUIRED` automatically (or pass `--require-sig`).

---

## Key rotation

1. Generate a new key: `openssl rand -hex 32`
2. Update the GitHub secret `PROMOTION_SIGNING_KEY`.
3. Any existing unsigned runs will continue to validate (backwards-compatible).
4. Any runs signed with the old key will **fail** verification — resign them by
   re-running `human_promote_recursive_run.sh` with the new key, or delete and
   regenerate the `.sig` files.

---

## Error codes

| Code                              | Meaning                                             |
| --------------------------------- | --------------------------------------------------- |
| `E_DECISION_SIG_MISSING`          | `--require-sig` set but no sig file provided        |
| `E_DECISION_SIG_READ_FAILED`      | Sig file exists but cannot be read                  |
| `E_DECISION_SIG_FORMAT`           | Sig file doesn't start with `hmac-sha256:`          |
| `E_DECISION_SIG_CANONICAL_FAILED` | Decision JSON cannot be parsed for canonicalisation |
| `E_DECISION_SIG_MISMATCH`         | MAC does not match — possible tampering             |
