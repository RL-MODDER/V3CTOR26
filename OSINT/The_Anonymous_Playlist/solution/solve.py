#!/usr/bin/env python3
"""
Solution Script for V3CT0R CTF 2026 - The Anonymous Playlist
Author: Principal Security Researcher
"""

import json
import os
import re
import urllib.request
import numpy as np
from PIL import Image

# Target Playlist Identifiers
PLAYLISTS = [
    ("1_Try_Again", "29OwF03v3LglkKID51mqAu"),
    ("2_Ignore_this", "4sJzovwomZYWrB0JLjKgI4"),
    ("3_Keep_digging", "6yqXE0wSmGnp3lqT98Zh06"),
    ("4_Dont_ignore_this", "0SIBH8cfxh6hQYOhlMCTow"),
    ("5_Just_Kidding", "20efh64cs6QRzzWAlVKkHE"),
    ("6_Are_you_tired", "5Kemo2Bqd552MzzJDeCn8T"),
    ("7_More_way_to_go", "41IOdO6Vwsv4xlKR62mWtw"),
    ("8_Somethings_missing", "0oFGmwodtqdRCUvBH3xLcf"),
    ("9_Put_Me_Together", "7tBRL4XEwWG0kynpsCXuUN")
]

# Column-Major Reassembly Matrix
MATRIX_LAYOUT = [
    ["1_Try_Again", "4_Dont_ignore_this", "7_More_way_to_go"],
    ["2_Ignore_this", "5_Just_Kidding", "8_Somethings_missing"],
    ["3_Keep_digging", "6_Are_you_tired", "9_Put_Me_Together"]
]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)

    images = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print("[*] Downloading playlist cover art...")
    for name, pid in PLAYLISTS:
        asset_path = os.path.join(assets_dir, f"{name}.jpg")
        if not os.path.exists(asset_path):
            url = f"https://open.spotify.com/embed/playlist/{pid}"
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req).read().decode("utf-8")
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if match:
                data = json.loads(match.group(1))
                entity = data["props"]["pageProps"]["state"]["data"]["entity"]
                img_url = entity["coverArt"]["sources"][0]["url"].replace("ab67706c0000da84", "ab67706c0000bebb")
                img_data = urllib.request.urlopen(img_url).read()
                with open(asset_path, "wb") as f:
                    f.write(img_data)
        images[name] = Image.open(asset_path).convert("RGB")
        print(f"  [+] Loaded {name}.jpg")

    print("[*] Reassembling 3x3 visual spatial matrix...")
    canvas = Image.new("RGB", (900, 900))
    for r in range(3):
        for c in range(3):
            tile_name = MATRIX_LAYOUT[r][c]
            canvas.paste(images[tile_name], (c * 300, r * 300))

    reconstructed_path = os.path.join(assets_dir, "qr_reconstructed.png")
    canvas.save(reconstructed_path)
    print(f"[+] Reconstructed QR saved to {reconstructed_path}")

    # Binarize 25x25 QR Matrix
    arr = np.array(canvas)
    green_mask = (arr[:, :, 1] > 100) & (arr[:, :, 0] < 100)
    
    N = 25
    matrix = np.zeros((N, N), dtype=int)
    xs = [int(round(34.5 + i * 34.5)) for i in range(N)]
    ys = [int(round(34.5 + i * 34.5)) for i in range(N)]

    for r in range(N):
        for c in range(N):
            patch = green_mask[ys[r]-5:ys[r]+6, xs[c]-5:xs[c]+6]
            matrix[r, c] = 1 if patch.mean() > 0.5 else 0

    # Build clean monochrome QR image
    clean_qr = Image.new("L", (N + 8, N + 8), 255)
    for r in range(N):
        for c in range(N):
            if matrix[r, c] == 1:
                clean_qr.putpixel((c + 4, r + 4), 0)

    clean_qr = clean_qr.resize(((N + 8) * 16, (N + 8) * 16), Image.NEAREST)
    clean_qr_path = os.path.join(assets_dir, "qr_clean.png")
    clean_qr.save(clean_qr_path)
    print(f"[+] Binarized monochrome QR saved to {clean_qr_path}")

    print("\n[+] Flag: V3ct0r{h1d3_n_l3375}")

if __name__ == "__main__":
    main()
