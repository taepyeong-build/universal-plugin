#!/usr/bin/env python3
"""Zero-dependency 512x512 square PNG icon generator (Python stdlib only)."""

from __future__ import annotations

import pathlib
import struct
import sys
import zlib


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def generate_icon_png(output_path: pathlib.Path, size: int = 512) -> None:
    """Generate a clean geometric 512x512 RGB PNG icon (< 20 KB) for 3-CLI compatibility."""
    if size < 512 or size > 2048:
        raise ValueError("Icon size must be between 512 and 2048 pixels.")

    cx = size / 2.0
    cy = size / 2.0
    r_outer = size * 0.36
    r_inner = size * 0.22
    r_core = size * 0.09

    # Deep indigo background, crisp cyan/violet geometric diamond-hex emblem
    rows = bytearray()
    for y in range(size):
        rows.append(0)  # filter type 0 (None)
        dy = abs(y - cy)
        row = bytearray(size * 3)
        bg_b = int(38 + (y / size) * 26)
        bg_g = int(20 + (y / size) * 14)
        bg_r = int(18 + (y / size) * 12)
        for x in range(size):
            dx = abs(x - cx)
            # Octagonal / hex-inspired distance metric for clean geometric emblem
            dist_oct = max(dx, dy, (dx + dy) * 0.72)
            dist_dia = dx + dy
            idx = x * 3
            if dist_dia <= r_core:
                # Bright white-cyan core
                row[idx] = 224
                row[idx + 1] = 247
                row[idx + 2] = 255
            elif r_inner - 14 <= dist_oct <= r_inner + 14:
                # Inner ring (electric cyan)
                row[idx] = 56
                row[idx + 1] = 189
                row[idx + 2] = 248
            elif r_outer - 18 <= dist_oct <= r_outer + 18:
                # Outer ring (indigo-violet accent)
                row[idx] = 129
                row[idx + 1] = 140
                row[idx + 2] = 248
            elif dist_oct < r_outer:
                # Subtle dark slate inner field
                row[idx] = 26
                row[idx + 1] = 32
                row[idx + 2] = 56
            else:
                row[idx] = bg_r
                row[idx + 1] = bg_g
                row[idx + 2] = bg_b
        rows.extend(row)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    idat = zlib.compress(bytes(rows), level=9)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", idat)
        + _png_chunk(b"IEND", b"")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(png_bytes)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 tools/icon.py <output.png>", file=sys.stderr)
        return 2
    out = pathlib.Path(sys.argv[1])
    generate_icon_png(out)
    print(f"Generated 512x512 icon: {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
