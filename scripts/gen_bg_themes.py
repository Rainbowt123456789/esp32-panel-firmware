# -*- coding: utf-8 -*-
"""
按 gen_bg.py 同款算法 (2D Floyd-Steinberg 误差扩散抖动 + RGB565 预量化)
生成 深紫 / 深粉 两套背景渐变, 保证转到 RGB565 后不出现色带分栏。
深蓝图 bg_grad.png 由 gen_bg.py 生成, 本脚本不覆盖它。
输出: images/bg_grad_light.png (深紫), images/bg_grad_pink.png (深粉)  480x480
"""
from pathlib import Path
from PIL import Image

W = H = 480

# 每个主题: 三个颜色节点 (y 位置 0.0 / 0.5 / 1.0)
THEMES = {
    "bg_grad_light.png": [
        (0.0, (0x16, 0x0A, 0x22)),   # 顶 深紫罗兰 (R/B 双高, G 压低, 与深蓝拉开)
        (0.5, (0x2C, 0x12, 0x40)),   # 中 紫
        (1.0, (0x48, 0x20, 0x60)),   # 底 亮紫
    ],
    "bg_grad_pink.png": [
        (0.0, (0x28, 0x10, 0x24)),   # 顶 深粉 (B 更靠近 R, 更柔粉)
        (0.5, (0x46, 0x18, 0x3E)),   # 中 粉
        (1.0, (0x70, 0x2C, 0x5C)),   # 底 亮粉
    ],
}

OUT_DIR = Path(__file__).resolve().parent.parent / "images"


def sample_color(stops, y):
    t = y / (H - 1)
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(c0[k] + (c1[k] - c0[k]) * f for k in range(3))
    return stops[-1][1]


def quant565(c):
    return round(c[0] / 8) * 8, round(c[1] / 4) * 4, round(c[2] / 8) * 8


def add(err, y, x, e, frac):
    for k in range(3):
        err[y][x][k] += e[k] * frac


def build(stops, out_path: Path):
    img = Image.new("RGB", (W, H))
    px = img.load()
    err = [[[0.0, 0.0, 0.0] for _ in range(W)] for _ in range(H)]

    for y in range(H):
        serpentine = (y % 2 == 1)
        xrange = range(W - 1, -1, -1) if serpentine else range(W)
        for x in xrange:
            base = sample_color(stops, y)
            c = [base[k] + err[y][x][k] for k in range(3)]
            q = quant565(c)
            e = [c[k] - q[k] for k in range(3)]
            if serpentine:
                if x > 0:
                    add(err, y, x - 1, e, 7 / 16)
                if y + 1 < H:
                    if x > 0:
                        add(err, y + 1, x - 1, e, 3 / 16)
                    add(err, y + 1, x, e, 5 / 16)
                    if x + 1 < W:
                        add(err, y + 1, x + 1, e, 1 / 16)
            else:
                if x + 1 < W:
                    add(err, y, x + 1, e, 7 / 16)
                if y + 1 < H:
                    if x > 0:
                        add(err, y + 1, x - 1, e, 3 / 16)
                    add(err, y + 1, x, e, 5 / 16)
                    if x + 1 < W:
                        add(err, y + 1, x + 1, e, 1 / 16)
            px[x, y] = q

    img.save(out_path, "PNG")
    jumps = 0
    for y in range(1, H):
        a = px[0, y - 1]
        b = px[0, y]
        if any(abs(a[k] - b[k]) >= 4 for k in range(3)):
            jumps += 1
    print(f"生成: {out_path.name}  顶 {px[0,0]} 底 {px[0,H-1]}  相邻行突变 {jumps}/{H}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, stops in THEMES.items():
        build(stops, OUT_DIR / name)


if __name__ == "__main__":
    main()
