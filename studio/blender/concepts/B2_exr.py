# Minimal reader for Blender's uncompressed (codec NONE) multilayer OpenEXR (single- or multi-part, scanline, HALF/FLOAT).
# numpy only. Returns {"<part or ''>.<channel>": HxW float32}.
import struct, numpy as np

def _header(f, p):
    hdr = {}
    while f[p] != 0:
        e = f.index(b"\0", p); name = f[p:e].decode(); p = e + 1
        e = f.index(b"\0", p); typ = f[p:e].decode(); p = e + 1
        size = struct.unpack_from("<i", f, p)[0]; p += 4
        hdr[name] = (typ, f[p:p + size]); p += size
    return hdr, p + 1

def _chans(raw):
    ch = []; q = 0
    while raw[q] != 0:
        e = raw.index(b"\0", q); nm = raw[q:e].decode(); q = e + 1
        ch.append((nm, struct.unpack_from("<i", raw, q)[0])); q += 16
    return ch

def read_exr(path):
    f = open(path, "rb").read()
    assert struct.unpack_from("<i", f, 0)[0] == 20000630, "not an EXR"
    flags = struct.unpack_from("<i", f, 4)[0]; multi = bool(flags & 0x1000)
    p = 8; parts = []
    while True:
        hdr, p = _header(f, p); parts.append(hdr)
        if not multi or f[p] == 0: break
    if multi: p += 1
    infos = []
    for hdr in parts:
        assert hdr["compression"][1][0] == 0, "only uncompressed EXR supported"
        x0, y0, x1, y1 = struct.unpack("<4i", hdr["dataWindow"][1]); W = x1 - x0 + 1; H = y1 - y0 + 1
        nm = hdr["name"][1].decode().rstrip("\0") if "name" in hdr else ""
        infos.append((nm, _chans(hdr["channels"][1]), W, H, y0)); p += 8 * H
    sizes = {1: 2, 2: 4, 0: 4}; dt = {1: np.float16, 2: np.float32, 0: np.uint32}
    out = {}
    for nm, ch, W, H, _ in infos:
        for c, _t in ch: out[c] = np.empty((H, W), np.float32)
    while p < len(f):
        if multi: part = struct.unpack_from("<i", f, p)[0]; p += 4
        else: part = 0
        nm, ch, W, H, y0 = infos[part]
        y, n = struct.unpack_from("<2i", f, p); p += 8; o = p
        for c, t in ch:
            out[c][y - y0] = np.frombuffer(f, dt[t], W, o).astype(np.float32); o += sizes[t] * W
        p += n
    return out
