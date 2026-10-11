# Repository Layout & Structure

```
.
└── OSINT/
    └── The_Anonymous_Playlist/
        ├── README.md
        ├── assets/
        │   ├── 1_Try_Again.jpg
        │   ├── 2_Ignore_this.jpg
        │   ├── 3_Keep_digging.jpg
        │   ├── 4_Dont_ignore_this.jpg
        │   ├── 5_Just_Kidding.jpg
        │   ├── 6_Are_you_tired.jpg
        │   ├── 7_More_way_to_go.jpg
        │   ├── 8_Somethings_missing.jpg
        │   ├── 9_Put_Me_Together.jpg
        │   ├── qr_reconstructed.png
        │   └── qr_clean.png
        └── solution/
            └── solve.py
```

---

# `OSINT/The_Anonymous_Playlist/README.md`

## Challenge Metadata

| Field | Value |
| :--- | :--- |
| **Event** | V3CT0R CTF 2026 |
| **Category** | OSINT (Open-Source Intelligence) |
| **Author** | Cybernexus CTFd Team, NGPiTECH |
| **Target Identifier** | `@ctfanonnnn` |
| **Vulnerability Class** | Information Leakage / Multi-Stage Asset Fragmentation (CWE-200 / CWE-538) |
| **Flag** | `V3ct0r{h1d3_n_l3375}` |

---

## Executive Summary

**The Anonymous Playlist** is an OSINT challenge centered on cross-platform digital footprinting, metadata extraction, redirect analysis, and visual data reconstruction. 

The threat actor handle `@ctfanonnnn` left traces across public social media platforms. Initial enumeration identified a target profile on X (formerly Twitter) containing an HTTP link shortener URL (`t.co`). Resolving this link led to an obscure Spotify user profile containing nine public playlists with zero tracks. Each playlist featured customized cover art representing a fraction of a fragmented Version 2 (25×25) QR code. By determining the dimensional bounds and boundary alignment of the 3×3 tile matrix, the spatial array was reassembled into a valid QR code yielding the flag: `V3ct0r{h1d3_n_l3375}`.

---

## Technical Vulnerability Analysis

### Vulnerability Classification
* **CWE-200**: Exposure of Sensitive Information Through Sent Data
* **CWE-538**: Insertion of Sensitive Information into Externally-Accessible File or Directory

### Root Cause Analysis
The underlying vulnerability stems from an insecure operational security (OpSec) posture and sensitive data fragmentation across public infrastructure. While individual components (an X post, an anonymous Spotify profile, individual image tiles) appear innocuous, their aggregation allows an attacker to construct a complete secret via deterministic spatial reassembly.

### Payload & Spatial Mechanics
The 2D visual payload was divided into nine $300 \times 300$ pixel JPEG tiles. Reassembling the matrix required determining the mapping function $f: T \to M$, where $T = \{t_1, t_2, \dots, t_9\}$ is the ordered set of tiles obtained from the Spotify profile and $M \in \mathbb{R}^{3 \times 3}$ is the target spatial matrix:

$$M = \begin{bmatrix} m_{0,0} & m_{0,1} & m_{0,2} \\ m_{1,0} & m_{1,1} & m_{1,2} \\ m_{2,0} & m_{2,1} & m_{2,2} \end{bmatrix}$$

Boundary pixel density analysis revealed that the tiles were exported in **column-major order** ($T_{col}$), rather than standard row-major order ($T_{row}$):

$$M = \begin{bmatrix} t_1 & t_4 & t_7 \\ t_2 & t_5 & t_8 \\ t_3 & t_6 & t_9 \end{bmatrix}$$

The reconstructed matrix $M$ forms a valid Version 2 QR code ($25 \times 25$ modules) with module pitch $S_m = 34.5\text{ px}$.

> [!NOTE]
> Standard QR code architecture requires three $7 \times 7$ finder patterns located at the top-left $(0,0)$, top-right $(0,2)$, and bottom-left $(2,0)$ corners. The presence of finder patterns in tiles $t_1$, $t_7$, and $t_3$ provided structural verification for the column-major placement hypothesis.

---

## Step-by-Step Exploitation Walkthrough

### Phase 1: Cross-Platform Reconnaissance
An automated username search using `sherlock` was executed against `@ctfanonnnn` across major social media networks.

```bash
sherlock ctfanonnnn --timeout 10
```

The scan identified social media footprints on X (Twitter), Instagram, Threads, and Spotify. Querying the X profile via open-graph metadata scrapers extracted the primary link payload:

```bash
curl -s -A "Slackbot-LinkExpanding 1.0" "https://twitter.com/ctfanonnnn"
```

**Extracted Post Content:**
```text
Anonymous (@ctfanonnnn)
Check this out: https://t.co/d40vjx8ysL
```

---

### Phase 2: Metadata Extraction & Redirect Resolution
Inspecting the HTTP headers of the `t.co` URL revealed a HTTP 301 redirection target pointing to an anonymized Spotify user ID:

```bash
curl -s -I "https://t.co/d40vjx8ysL" | grep -i "location"
```

**Output:**
```http
location: https://open.spotify.com/user/31ssr74dhhufdkik2dniidoeqwrq
```

---

### Phase 3: Spotify Profile Scraping & Asset Extraction
Rendering the DOM of the target Spotify profile revealed 9 public playlists:

```json
[
  {"name": "Try Again", "id": "29OwF03v3LglkKID51mqAu"},
  {"name": "Ignore this", "id": "4sJzovwomZYWrB0JLjKgI4"},
  {"name": "Keep digging", "id": "6yqXE0wSmGnp3lqT98Zh06"},
  {"name": "Don't ignore this", "id": "0SIBH8cfxh6hQYOhlMCTow"},
  {"name": "Just Kidding", "id": "20efh64cs6QRzzWAlVKkHE"},
  {"name": "Are you tired?", "id": "5Kemo2Bqd552MzzJDeCn8T"},
  {"name": "More way to go", "id": "41IOdO6Vwsv4xlKR62mWtw"},
  {"name": "Something's missing", "id": "0oFGmwodtqdRCUvBH3xLcf"},
  {"name": "Put Me Together", "id": "7tBRL4XEwWG0kynpsCXuUN"}
]
```

All nine playlists contained 0 audio tracks, but each featured a unique $300 \times 300$ px cover image.

---

### Phase 4: Boundary Density Analysis & Spatial Reassembly
An analysis script was written to examine the boundary pixel density across all four edges of each image tile:

```python
# Boundary Pixel Sum Analysis (Threshold = 80)
1_Try_Again:         Top:   0, Left:   0, Bottom: 152, Right:  94
2_Ignore_this:       Top: 155, Left:   0, Bottom: 125, Right:  95
3_Keep_digging:      Top: 125, Left:   0, Bottom:   0, Right: 156
4_Dont_ignore_this:  Top:   0, Left:  95, Bottom: 212, Right: 127
5_Just_Kidding:      Top: 217, Left:  96, Bottom: 123, Right: 212
6_Are_you_tired:     Top: 123, Left: 158, Bottom:   0, Right: 225
7_More_way_to_go:    Top:   0, Left: 121, Bottom:  63, Right:   0
8_Somethings_missing:Top:  65, Left: 200, Bottom: 223, Right:   0
9_Put_Me_Together:   Top: 223, Left: 213, Bottom:   0, Right:   0
```

**Key Observations:**
1. **Vertical Continuities:** $t_1 \text{ Bottom} \approx t_2 \text{ Top}$, $t_2 \text{ Bottom} \approx t_3 \text{ Top}$
2. **Horizontal Continuities:** $t_1 \text{ Right} \approx t_4 \text{ Left}$, $t_4 \text{ Right} \approx t_7 \text{ Left}$
3. **Corner Quiet Zones:** Tiles $t_1, t_3, t_7, t_9$ contain $0$-density outer boundaries corresponding to QR code quiet zones.

This proves that the tiles were stored in column-major order.

---

### Phase 5: Automated Solution Script

The solution script in `solution/solve.py` automates downloading, matrix reassembly, module binarization, and flag decoding.

---

## Remediation & Defensive Guidelines

To mitigate information leakage and steganographic data exposure across public platforms, organizations and researchers should enforce the following operational controls:

### 1. Operational Security (OpSec) & Footprint Minimization
* **Handle Disassociation:** Avoid re-using identical handles (`@ctfanonnnn`) across separate platforms and testing environments.
* **Link Shortener Auditing:** Prohibit the use of public link shorteners (`t.co`, `bit.ly`) for sensitive or unindexed assets; shortener domains are continuously indexed and archived by global crawlers.

### 2. Privacy & Access Control Configurations
* **Social Profile Hardening:** Configure streaming platform profiles (e.g., Spotify, SoundCloud) to private by default, restricting playlist visibility and profile indexing.
* **Metadata Sanitization:** Strip EXIF, IPTC, and custom steganographic layer data from public profile images prior to deployment.

### 3. Cryptographic Secret Management
* Secrets and sensitive tokens must **never** be embedded into visual artifacts or distributed across public third-party SaaS infrastructure.
* Secrets should be stored in dedicated Secret Management Services (e.g., HashiCorp Vault, AWS Secrets Manager) protected by strong identity and access management (IAM) policies.
