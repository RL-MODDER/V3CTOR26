# V3CT0R CTF 2026 — Security Assessment & Writeups

Publication-ready technical writeups, proof-of-concept scripts, and root-cause analyses for verified challenges solved during **V3CT0R CTF 2026**.

---

## Event Summary

| Parameter | Details |
| :--- | :--- |
| **Event Name** | V3CT0R CTF 2026 |
| **Organizer** | Cybernexus CTFd Team & NGPiTECH |
| **Format** | Jeopardy CTF |
| **Categories Solved** | Web Security, Open-Source Intelligence (OSINT) |
| **Total Solved Points** | 1,032 pts |

---

## Solved Challenge Index

### Web Security

| Challenge | Points | Solves | Vulnerability Classification | Verified Flag | Writeup Link |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **The Forgotten Reset** | 490 | 11 | Broken Authentication / Insecure Password Recovery (CWE-640) | `V3ct0r{Recovery_Tokens_are_Trusted_Identifiers}` | [README](Web/The_Forgotten_Reset/README.md) |
| **Invoice #42** | 492 | 9 | Insecure Direct Object Reference (IDOR / CWE-639) | `V3ct0r{1D0R_0rd3r_1003}` | [README](Web/Invoice_42/README.md) |

### OSINT (Open-Source Intelligence)

| Challenge | Points | Solves | Primary Technique | Verified Flag | Writeup Link |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **The Anonymous Playlist** | 50 | 3 | Multi-Stage Asset Fragmentation / QR Matrix Spatial Reassembly (CWE-200) | `V3ct0r{h1d3_n_l3375}` | [README](OSINT/The_Anonymous_Playlist/README.md) |

---

## Repository Structure

```text
.
├── README.md
├── OSINT/
│   └── The_Anonymous_Playlist/
│       ├── README.md
│       ├── assets/
│       │   ├── 1_Try_Again.jpg ... 9_Put_Me_Together.jpg
│       │   ├── qr_clean.png
│       │   └── qr_reconstructed.png
│       └── solution/
│           └── solve.py
└── Web/
    ├── Invoice_42/
    │   └── README.md
    └── The_Forgotten_Reset/
        └── README.md
```

---

## Tooling & Methodology

* **HTTP Traffic Analysis & Tampering:** Burp Suite Professional, cURL
* **OSINT & Asset Enumeration:** Sherlock, HTTP Link Shortener Expansion
* **Automation & Scripting:** Python 3.12 (Requests, PIL/Pillow, NumPy)
* **Cryptographic & Encoding Analysis:** CyberChef, OpenSSL

---

## Authorization & Compliance

All vulnerability assessments, proof-of-concept exploits, and flag retrievals documented in this repository were conducted exclusively against designated V3CT0R CTF 2026 infrastructure in accordance with event terms and explicit testing authorization.
