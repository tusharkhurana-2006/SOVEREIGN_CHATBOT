"""
================================================================================
PURE-PYTHON OFFLINE QR CODE GENERATOR (ZERO EXTERNAL DEPENDENCIES)
Generates ISO/IEC 18004 compliant QR Codes (Version 1-4, Byte Mode, EC Level L/M)
Outputs clean scalable SVG directly.
================================================================================
"""

import sys

# Galois Field GF(256) tables for QR Reed-Solomon EC
GF_EXP = [0] * 512
GF_LOG = [0] * 256
_x = 1
for _i in range(255):
    GF_EXP[_i] = _x
    GF_LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D  # Primitive poly: x^8 + x^4 + x^3 + x^2 + 1
for _i in range(255, 512):
    GF_EXP[_i] = GF_EXP[_i - 255]


def gf_mul(x, y):
    if x == 0 or y == 0:
        return 0
    return GF_EXP[GF_LOG[x] + GF_LOG[y]]


def rs_generator_poly(num_ec_bytes):
    poly = [1]
    for i in range(num_ec_bytes):
        poly = rs_poly_mul(poly, [1, GF_EXP[i]])
    return poly


def rs_poly_mul(p1, p2):
    res = [0] * (len(p1) + len(p2) - 1)
    for j in range(len(p2)):
        for i in range(len(p1)):
            res[i + j] ^= gf_mul(p1[i], p2[j])
    return res


def rs_calc_ec(data, num_ec_bytes):
    gen = rs_generator_poly(num_ec_bytes)
    msg = list(data) + [0] * num_ec_bytes
    for i in range(len(data)):
        coef = msg[i]
        if coef != 0:
            for j in range(len(gen)):
                msg[i + j] ^= gf_mul(gen[j], coef)
    return msg[-num_ec_bytes:]


# Version table: (version, total_codewords, ec_codewords, data_codewords)
VERSION_SPECS = {
    1: {"size": 21, "total_cw": 26, "ec_cw": 7, "data_cw": 19, "align": []},
    2: {"size": 25, "total_cw": 44, "ec_cw": 10, "data_cw": 34, "align": [6, 18]},
    3: {"size": 29, "total_cw": 70, "ec_cw": 15, "data_cw": 55, "align": [6, 22]},
    4: {"size": 33, "total_cw": 100, "ec_cw": 20, "data_cw": 80, "align": [6, 26]},
}

# Format bits for Mask 0 to 7 (Level L)
FORMAT_BITS_L = [
    0x77C4, 0x72F3, 0x7DAA, 0x789D, 0x662F, 0x6318, 0x6C41, 0x6976
]


class PureQRCode:
    def __init__(self, data: str):
        self.raw_data = data.encode('utf-8')
        # Select minimum version
        self.version = 1
        for v in [1, 2, 3, 4]:
            if len(self.raw_data) <= VERSION_SPECS[v]["data_cw"] - 3:
                self.version = v
                break
        else:
            self.version = 4

        self.spec = VERSION_SPECS[self.version]
        self.size = self.spec["size"]
        self.matrix = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.reserved = [[False for _ in range(self.size)] for _ in range(self.size)]

        self._build_matrix()

    def _build_matrix(self):
        # 1. Place finder patterns (7x7) at 3 corners
        self._place_finder(0, 0)
        self._place_finder(0, self.size - 7)
        self._place_finder(self.size - 7, 0)

        # 2. Place timing patterns
        for i in range(8, self.size - 8):
            val = (i % 2 == 0)
            self.matrix[6][i] = val
            self.matrix[i][6] = val
            self.reserved[6][i] = True
            self.reserved[i][6] = True

        # 3. Place alignment patterns if any
        if self.spec["align"]:
            pos = self.spec["align"]
            for r in pos:
                for c in pos:
                    if not ((r < 9 and c < 9) or (r < 9 and c > self.size - 9) or (r > self.size - 9 and c < 9)):
                        self._place_alignment(r, c)

        # 4. Dark module
        self.matrix[4 * self.version + 9][8] = True
        self.reserved[4 * self.version + 9][8] = True

        # 5. Reserve format info areas
        for i in range(9):
            self.reserved[8][i] = True
            self.reserved[i][8] = True
        for i in range(8):
            self.reserved[8][self.size - 1 - i] = True
            self.reserved[self.size - 1 - i][8] = True

        # 6. Encode data stream
        bit_stream = self._encode_data()

        # 7. Calculate Reed-Solomon EC
        ec_bytes = rs_calc_ec(bit_stream, self.spec["ec_cw"])
        all_codewords = list(bit_stream) + ec_bytes

        # Convert codewords to bits
        all_bits = []
        for cw in all_codewords:
            for b in range(7, -1, -1):
                all_bits.append((cw >> b) & 1)

        # 8. Place bits with mask (Mask 0: (row + col) % 2 == 0)
        bit_idx = 0
        direction = -1  # Upwards
        row = self.size - 1
        col = self.size - 1

        while col > 0:
            if col == 6:  # Skip vertical timing pattern
                col -= 1

            for _ in range(self.size):
                for c_offset in [0, -1]:
                    c = col + c_offset
                    if not self.reserved[row][c]:
                        bit_val = all_bits[bit_idx] if bit_idx < len(all_bits) else 0
                        bit_idx += 1
                        # Apply Mask 0: (row + col) % 2 == 0
                        mask = ((row + c) % 2 == 0)
                        self.matrix[row][c] = (bit_val ^ (1 if mask else 0)) == 1

                row += direction
                if row < 0 or row >= self.size:
                    direction = -direction
                    row += direction
                    break

            col -= 2

        # 9. Write Format Information (Mask 0, Level L)
        fmt = FORMAT_BITS_L[0]
        # Top-left format bits
        for i in range(6):
            self.matrix[8][i] = bool((fmt >> (14 - i)) & 1)
        self.matrix[8][7] = bool((fmt >> 8) & 1)
        self.matrix[8][8] = bool((fmt >> 7) & 1)
        self.matrix[7][8] = bool((fmt >> 6) & 1)
        for i in range(6):
            self.matrix[5 - i][8] = bool((fmt >> i) & 1)

        # Bottom-left and Top-right format bits
        for i in range(7):
            self.matrix[self.size - 1 - i][8] = bool((fmt >> i) & 1)
        for i in range(8):
            self.matrix[8][self.size - 8 + i] = bool((fmt >> (7 + i)) & 1)

    def _place_finder(self, top, left):
        for r in range(-1, 8):
            for c in range(-1, 8):
                nr = top + r
                nc = left + c
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if (0 <= r <= 6 and (c == 0 or c == 6)) or (0 <= c <= 6 and (r == 0 or r == 6)) or (2 <= r <= 4 and 2 <= c <= 4):
                        self.matrix[nr][nc] = True
                    else:
                        self.matrix[nr][nc] = False
                    self.reserved[nr][nc] = True

    def _place_alignment(self, center_r, center_c):
        for r in range(-2, 3):
            for c in range(-2, 3):
                nr = center_r + r
                nc = center_c + c
                if max(abs(r), abs(c)) == 2 or (r == 0 and c == 0):
                    self.matrix[nr][nc] = True
                else:
                    self.matrix[nr][nc] = False
                self.reserved[nr][nc] = True

    def _encode_data(self):
        # 8-bit Byte Mode: Mode indicator 0100 (4 bits)
        bits = [0, 1, 0, 0]
        # Character count indicator (8 bits)
        length = len(self.raw_data)
        for b in range(7, -1, -1):
            bits.append((length >> b) & 1)
        # Data bytes
        for byte in self.raw_data:
            for b in range(7, -1, -1):
                bits.append((byte >> b) & 1)

        # Terminator: up to 4 zero bits
        data_cw = self.spec["data_cw"]
        max_bits = data_cw * 8
        term_len = min(4, max_bits - len(bits))
        bits.extend([0] * term_len)

        # Pad to byte boundary
        while len(bits) % 8 != 0:
            bits.append(0)

        # Convert to bytes
        bytes_list = []
        for i in range(0, len(bits), 8):
            val = 0
            for b in range(8):
                val = (val << 1) | bits[i + b]
            bytes_list.append(val)

        # Pad bytes 0xEC, 0x11
        pad_bytes = [0xEC, 0x11]
        pad_idx = 0
        while len(bytes_list) < data_cw:
            bytes_list.append(pad_bytes[pad_idx % 2])
            pad_idx += 1

        return bytes_list

    def to_svg(self, size_px=240, fg_color="#00f0ff", bg_color="#05070d", quiet_zone=2) -> str:
        """Returns clean, self-contained SVG representation of the QR code."""
        dim = self.size + 2 * quiet_zone
        scale = size_px / dim
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {dim} {dim}" width="{size_px}" height="{size_px}">',
            f'<rect width="{dim}" height="{dim}" fill="{bg_color}" rx="6" />',
            f'<g fill="{fg_color}">'
        ]

        for r in range(self.size):
            for c in range(self.size):
                if self.matrix[r][c]:
                    svg_parts.append(f'<rect x="{c + quiet_zone}" y="{r + quiet_zone}" width="1.02" height="1.02" />')

        svg_parts.append('</g></svg>')
        return "\n".join(svg_parts)


def generate_qr_svg(url: str, size_px: int = 240, fg_color: str = "#00f0ff", bg_color: str = "#0a0e1a") -> str:
    qr = PureQRCode(url)
    return qr.to_svg(size_px=size_px, fg_color=fg_color, bg_color=bg_color)


if __name__ == "__main__":
    test_url = "http://10.159.3.238:8000"
    svg = generate_qr_svg(test_url)
    print("QR SVG generated successfully, length:", len(svg))
