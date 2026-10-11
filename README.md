# V3CT0R CTF 2026 — Technical Security Writeups

Technical security writeups, root-cause analyses, and proof-of-concept exploits for challenges completed during **V3CT0R CTF 2026**.

---

## Event Summary

| Parameter | Details |
| :--- | :--- |
| **Event Name** | V3CT0R CTF 2026 |
| **Organizer** | Cybernexus CTFd Team & NGPiTECH |
| **Format** | Jeopardy CTF |
| **Assessment Domains** | Web Application Security, Open-Source Intelligence (OSINT) |

---

## Technical Writeups Index

### Web Application Security

| Challenge | Target URL | Vulnerability Classification | Verified Flag | Writeup |
| :--- | :--- | :--- | :--- | :---: |
| **Meridian Password Reset** | `https://web2.cybernexus.live` | Broken Authentication / Insecure Password Recovery (CWE-640) | `V3ct0r{Recovery_Tokens_are_Trusted_Identifiers}` | [View Report](Web/Meridian_Password_Reset/README.md) |
| **Invoice #42** | `https://web3.cybernexus.live/` | Insecure Direct Object Reference (IDOR / CWE-639) | `V3ct0r{1D0R_0rd3r_1003}` | [View Report](Web/Invoice_42/README.md) |

### OSINT (Open-Source Intelligence)

| Challenge | Target Scope | Technique & Vector | Verified Flag | Writeup |
| :--- | :--- | :--- | :--- | :---: |
| **The Anonymous Playlist** | `@ctfanonnnn` | Multi-Stage Asset Fragmentation / QR Matrix Spatial Reassembly (CWE-200) | `V3ct0r{h1d3_n_l3375}` | [View Report](OSINT/The_Anonymous_Playlist/README.md) |

---

## Repository Structure

```text
.
├── README.md
├── OSINT/
│   └── The_Anonymous_Playlist/
│       ├── README.md
│       ├── assets/
│       └── solution/
│           └── solve.py
└── Web/
    ├── Invoice_42/
    │   └── README.md
    └── Meridian_Password_Reset/
        ├── README.md
        └── images/
            ├── guest-token.png
            ├── admin-token.png
            └── recovered-flag.png
```

---

## Tooling & Methodology

* **HTTP Traffic Analysis & Tampering:** Burp Suite Professional, cURL
* **OSINT & Asset Enumeration:** Sherlock, HTTP Link Shortener Expansion
* **Automation & Scripting:** Python 3.12 (Requests, PIL/Pillow, NumPy)
* **Cryptographic & Encoding Analysis:** CyberChef, OpenSSL

---

## Authorization & Compliance

All security assessments, vulnerability research, and PoC developments contained in this repository were conducted exclusively against designated CTF target infrastructure in accordance with event rules and explicit authorization.
