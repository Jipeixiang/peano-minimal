"""
Draw the LEGO analogy illustrations used by the tutorials, in Chinese and English.

    python3 make_images.py

Writes <name>.zh-CN.svg and <name>.en.svg next to this script. All drawings are original,
simplified sketches (no LEGO artwork is copied). Needs Pillow for the pixelated excavators.
"""

import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans SC', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"

C = {
    "bg": "#f6f8fc", "frame": "#d9dfe8", "ink": "#16202e", "muted": "#5a6779",
    "grey": "#a3a9ad", "grey_d": "#6f767b", "black": "#2b2d30", "blue": "#2f6fd0", "blue_d": "#1d4f9e",
    "provide": "#2e9e6b", "need": "#d9822b", "accent": "#1f5fbf",
    "body": "#e9e4d4", "body_s": "#8d8774", "track": "#3b3f44", "soil": "#b48a5a", "soil_d": "#8a6538",
    "glass": "#bcd3ee", "bag": "#eef2f8", "bag_s": "#9fb0c6", "hub": "#d9822b",
}

L = {
    "zh-CN": {
        "ov": ["0 通用零件", "1a 设计这一套", "1b 压零件、拼整车", "2 开机挖土", "3 对照检查"],
        "ov_sub": ["cmake → .a", "Python → C++", "make → 可执行文件", "./gauge-wave", "check.py"],
        "plate": "1×2 板（3023）", "pin_s": "黑色短摩擦销（2780）", "pin_l": "蓝色长摩擦销（6558）",
        "parts_note": "通用零件：挖掘机、跑车、城堡都要用 —— 对应第 0 步的库",
        "mould": "模具 = 一个 .cpp", "shot": "一次压出的一板零件 = 一个 .o", "inject": "注塑 = 编译",
        "func": "每个零件 = 一个函数", "studs": "凸点：我提供什么", "holes": "孔：我还缺什么",
        "linker": "链接器按顺序翻分包，翻过去就不回头",
        "bags": ["ExaGRyPE", "ExaHyPE 2", "Toolbox", "Peano4"], "tarch": "Tarch",
        "needs": "要用", "smallbag": "小分包：2780、6558 这类到处都要用的销子 → 放在最后",
        "static": "静态库：零件已经卡进车里", "dynamic": "动态库：开机时才连上 app",
        "static_sub": "分包袋扔掉也照样能玩", "dynamic_sub": "没装 app → Library not loaded",
        "hubs": "2 个 Smart Hub", "app": "Control+ app",
        "snap": "每隔一段时间拍一张 = 快照（output/）", "check": "和真挖掘机对照 = check.py",
        "chain": [("源码", ".cpp / .h"), ("目标文件", ".o"), ("静态库", ".a"), ("可执行文件", "gauge-wave")],
        "chain_ops": ["编译", "打包（ar）", "链接"],
        "scales": ["9 点", "27 点", "81 点"], "scale_note": "零件边长每次缩小到 1/3，和真车的差别缩小到约 1/81",
        "brief_title": "需求单：gauge-wave.py",
        "brief": ["CCZ4 方程 · 58 个未知量", "FD4 差分 · patch 9×9×9", "halo 宽 3 层", "RK4 · 推进到 t = 1", "周期边界"],
        "designer": "设计师 = generate()", "booklet": "说明书：code/ 里的 C++",
        "dims": ["15 孔梁", "3 单位销", "9×9×9", "比例 1:20"], "fixed": "尺寸全部写死 = 编译期常数",
        "brief_note": "Python 只画图、写说明书，自己不拼，也不做任何计算",
        "cards": [("Constants.h", "封面上的尺寸和比例"), ("AbstractCCZ4.h/.cpp", "底盘和车架，尺寸已定死"),
                  ("kernels/", "回转机构、动臂和挖斗\n真正干活的部分"), ("celldata/  facedata/", "每个模块装什么\n接合处留哪些孔"),
                  ("observers/", "每一页上的步骤"), ("repositories/", "页码：先拼哪页、后拼哪页"),
                  ("gauge-wave-main.cpp", "第 1 页：从这里开始"), ("CMakeLists.txt  Makefile", "封底零件清单：用哪些分包")],
        "start": "从这里开始",
        "act": ["收回", "伸出"], "act_in": "马达转动输入轴", "act_part": "线性执行器（伸缩杆）",
        "act_use": "装在车上：推动动臂和斗杆",
        "act_note": "为特定机构准备的零件 —— 就像 1b 编译出来、只给这一台用的专属零件",
        "drive": ["马达", "齿轮减速", "离合齿轮", "回转台", "挖斗"],
        "drive_sub": ["Control+ 马达", "小齿轮带大齿轮", "力太大时打滑", "上车整体回转", "挖土"],
        "drive_note": "传动链：从马达到挖斗，真正干活的部分 —— 对应 kernels/（FD4 差分、RK 线性组合）",
        "halo_a": "模块 A：自己的 9 个孔", "halo_b": "模块 B：自己的 9 个孔",
        "halo_copy": "halo：从 B 抄来的 3 个孔", "halo_copy_b": "halo：从 A 抄来的 3 个孔",
        "halo_note": "算靠边的孔要用到隔壁模块的值，所以每个模块两边各多留 3 个孔（halo），每一步开始前先从邻居那里抄过来",
    },
    "en": {
        "ov": ["0 standard parts", "1a design the set", "1b mould and build", "2 switch on and dig", "3 check"],
        "ov_sub": ["cmake → .a", "Python → C++", "make → executable", "./gauge-wave", "check.py"],
        "plate": "1×2 plate (3023)", "pin_s": "black short friction pin (2780)", "pin_l": "blue long friction pin (6558)",
        "parts_note": "Standard parts: excavators, cars and castles all use them, like the step 0 libraries",
        "mould": "mould = one .cpp", "shot": "one shot of parts = one .o", "inject": "moulding = compiling",
        "func": "each part = one function", "studs": "studs: what I provide", "holes": "holes: what I still need",
        "linker": "the linker opens the bags in order and never goes back",
        "bags": ["ExaGRyPE", "ExaHyPE 2", "Toolbox", "Peano4"], "tarch": "Tarch",
        "needs": "needs", "smallbag": "small bag: pins like 2780 and 6558 that every bag needs → goes last",
        "static": "static library: parts clicked into the model", "dynamic": "dynamic library: app connected at switch-on",
        "static_sub": "throw the bags away, it still works", "dynamic_sub": "no app → Library not loaded",
        "hubs": "2 Smart Hubs", "app": "Control+ app",
        "snap": "a photo every so often = snapshots (output/)", "check": "compare with the real machine = check.py",
        "chain": [("source", ".cpp / .h"), ("object files", ".o"), ("static library", ".a"), ("executable", "gauge-wave")],
        "chain_ops": ["compile", "pack (ar)", "link"],
        "scales": ["9 points", "27 points", "81 points"], "scale_note": "parts a third of the size → about 81 times closer to the real machine",
        "brief_title": "The brief: gauge-wave.py",
        "brief": ["CCZ4 equations · 58 unknowns", "FD4 · 9×9×9 patches", "halo 3 layers wide", "RK4 · up to t = 1", "periodic boundaries"],
        "designer": "designer = generate()", "booklet": "booklet: the C++ in code/",
        "dims": ["15-hole beam", "3-unit pin", "9×9×9", "scale 1:20"], "fixed": "every size fixed = compile-time constants",
        "brief_note": "Python only draws and writes the booklet; it builds nothing and computes nothing",
        "cards": [("Constants.h", "sizes and scale on the cover"), ("AbstractCCZ4.h/.cpp", "chassis and frame, sizes fixed"),
                  ("kernels/", "slewing ring, boom, bucket: the working parts"), ("celldata/  facedata/", "what each module holds, which holes the joints keep"),
                  ("observers/", "the steps on each page"), ("repositories/", "page order: which page comes first"),
                  ("gauge-wave-main.cpp", "page 1: start here"), ("CMakeLists.txt  Makefile", "parts list on the back: which bags")],
        "start": "start here",
        "act": ["retracted", "extended"], "act_in": "motor turns the input axle", "act_part": "linear actuator",
        "act_use": "on the machine: pushes the boom and the stick",
        "act_note": "a part made for one specific mechanism, like the set-specific parts 1b compiles for this one machine",
        "drive": ["motor", "reduction", "clutch gear", "turntable", "bucket"],
        "drive_sub": ["Control+ motor", "small gear drives big", "slips under overload", "slews the upper body", "digs"],
        "drive_note": "The drive train from motor to bucket, the parts that do the work, like kernels/ (FD4 differences, RK combinations)",
        "halo_a": "module A: its own 9 holes", "halo_b": "module B: its own 9 holes",
        "halo_copy": "halo: 3 holes copied from B", "halo_copy_b": "halo: 3 holes copied from A",
        "halo_note": "holes near the edge need values from the next module, so each module keeps 3 extra holes (the halo) on each side and copies them from its neighbour before every step",
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13, color=None, anchor="middle", weight=400, mono=False):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color or C["ink"]}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{MONO if mono else FONT}">{esc(s)}</text>')


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{C["muted"]}"/></marker></defs>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{C["bg"]}" stroke="{C["frame"]}"/>'
            + body + "</svg>\n")


def arrow(x1, y1, x2, y2, dashed=False, color=None):
    d = ' stroke-dasharray="5 4"' if dashed else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["muted"]}" stroke-width="1.8"{d} '
            f'marker-end="url(#ah)"/>')


# ------------------------------------------------------------------ parts


def plate(x, y, u=70):
    """1x2 plate, side view. (x, y) = bottom-left. u = stud pitch in px."""
    h = 0.4 * u
    out = [f'<rect x="{x}" y="{y-h}" width="{2*u}" height="{h}" rx="3" fill="{C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.5"/>',
           f'<line x1="{x+3}" y1="{y-h+4}" x2="{x+2*u-3}" y2="{y-h+4}" stroke="#c9cdd0" stroke-width="2"/>']
    for i in range(2):
        cx = x + (i + 0.5) * u
        sw, sh = 0.6 * u, 0.22 * u
        out.append(f'<rect x="{cx-sw/2}" y="{y-h-sh}" width="{sw}" height="{sh+2}" rx="2" fill="{C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.5"/>')
    return "".join(out)


def pin(x, y, length, collar_at, color, dark, u=60):
    """Technic pin, side view, centred on y. length and collar_at in units of u."""
    d = 0.6 * u
    w = length * u
    out = [f'<rect x="{x}" y="{y-d/2}" width="{w}" height="{d}" rx="{d/2.5}" fill="{color}" stroke="{dark}" stroke-width="1.5"/>',
           f'<line x1="{x+6}" y1="{y-d/2+5}" x2="{x+w-6}" y2="{y-d/2+5}" stroke="#ffffff" stroke-opacity="0.35" stroke-width="2"/>']
    for k in range(int(length)):  # friction ridges on each unit
        for j in range(3):
            rx = x + (k + 0.25) * u + j * 6
            if abs(rx - (x + collar_at * u)) > 10:
                out.append(f'<line x1="{rx}" y1="{y-d/2+3}" x2="{rx}" y2="{y+d/2-3}" stroke="{dark}" stroke-width="1"/>')
    cx = x + collar_at * u
    out.append(f'<rect x="{cx-5}" y="{y-d/2-5}" width="10" height="{d+10}" rx="3" fill="{color}" stroke="{dark}" stroke-width="1.5"/>')
    out.append(f'<line x1="{x+2}" y1="{y}" x2="{x+12}" y2="{y}" stroke="{dark}" stroke-width="1.5"/>')
    out.append(f'<line x1="{x+w-12}" y1="{y}" x2="{x+w-2}" y2="{y}" stroke="{dark}" stroke-width="1.5"/>')
    return "".join(out)


def gear(cx, cy, r, teeth=12, color=None, dark=None):
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.8
        pts.append(f"{cx+rr*math.cos(a):.1f},{cy+rr*math.sin(a):.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="{color or C["grey"]}" stroke="{dark or C["grey_d"]}" stroke-width="1.3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.25}" fill="{C["bg"]}" stroke="{dark or C["grey_d"]}"/>')


def beam(x, y, holes, u=26, color=None):
    w = holes * u
    out = [f'<rect x="{x}" y="{y-u/2}" width="{w}" height="{u}" rx="{u/2}" fill="{color or C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.3"/>']
    for i in range(holes):
        out.append(f'<circle cx="{x+(i+0.5)*u}" cy="{y}" r="{u*0.27}" fill="{C["bg"]}" stroke="{C["grey_d"]}"/>')
    return "".join(out)


# ------------------------------------------------------------------ excavator geometry (units)

def excavator_prims(pose="up"):
    if pose == "dig":
        boom, stick = (36, 23, 62, 8), (62, 8, 80, 40)
        bucket = [(72, 38), (88, 38), (91, 50), (80, 54), (73, 47)]
        cyl2 = (56, 10, 72, 26)
    else:
        boom, stick = (36, 23, 64, 3), (64, 3, 80, 24)
        bucket = [(74, 22), (88, 22), (90, 34), (80, 37), (75, 30)]
        cyl2 = (58, 6, 74, 16)
    return [
        ("rrect", (0, 40, 64, 12, 6), "track"),
        ("circles", ([(8 + i * 9.6, 46) for i in range(6)], 3.2), "wheel"),
        ("rect", (24, 34, 16, 6), "track"),
        ("rect", (2, 24, 12, 10), "cw"),
        ("rect", (10, 22, 32, 12), "body"),
        ("rect", (38, 8, 14, 14), "body"),
        ("rect", (41, 10, 9, 7), "glass"),
        ("line", (*boom, 6), "body"),
        ("line", (*stick, 5), "body"),
        ("poly", bucket, "bucket"),
        ("line", (30, 27, 54, 11, 2.6), "cyl"),
        ("line", (*cyl2, 2.2), "cyl"),
    ]


STYLE = {"track": (C["track"], C["track"]), "wheel": (C["grey_d"], C["track"]), "cw": (C["body_s"], C["body_s"]),
         "body": (C["body"], C["body_s"]), "glass": (C["glass"], C["body_s"]), "bucket": (C["track"], C["track"]),
         "cyl": (C["grey_d"], C["grey_d"])}


def excavator(ox, oy, s, pose="up", hubs=False):
    """SVG excavator; (ox, oy) top-left in px, s px per unit."""
    out = []
    for kind, g, role in excavator_prims(pose):
        fill, stroke = STYLE[role]
        if kind == "rrect":
            x, y, w, h, r = g
            out.append(f'<rect x="{ox+x*s:.1f}" y="{oy+y*s:.1f}" width="{w*s:.1f}" height="{h*s:.1f}" rx="{r*s:.1f}" fill="{fill}" stroke="{stroke}"/>')
        elif kind == "rect":
            x, y, w, h = g
            out.append(f'<rect x="{ox+x*s:.1f}" y="{oy+y*s:.1f}" width="{w*s:.1f}" height="{h*s:.1f}" rx="{s*0.8:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        elif kind == "circles":
            pts, r = g
            for (cx, cy) in pts:
                out.append(f'<circle cx="{ox+cx*s:.1f}" cy="{oy+cy*s:.1f}" r="{r*s:.1f}" fill="{fill}" stroke="#1f2226"/>')
        elif kind == "line":
            x1, y1, x2, y2, w = g
            if role != "cyl":
                out.append(f'<line x1="{ox+x1*s:.1f}" y1="{oy+y1*s:.1f}" x2="{ox+x2*s:.1f}" y2="{oy+y2*s:.1f}" stroke="{stroke}" stroke-width="{w*s+2.4:.1f}" stroke-linecap="round"/>')
            out.append(f'<line x1="{ox+x1*s:.1f}" y1="{oy+y1*s:.1f}" x2="{ox+x2*s:.1f}" y2="{oy+y2*s:.1f}" stroke="{fill}" stroke-width="{w*s:.1f}" stroke-linecap="round"/>')
        elif kind == "poly":
            pts = " ".join(f"{ox+x*s:.1f},{oy+y*s:.1f}" for x, y in g)
            out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-linejoin="round"/>')
    if hubs:
        for hx in (16, 28):
            out.append(f'<rect x="{ox+hx*s:.1f}" y="{oy+25*s:.1f}" width="{8*s:.1f}" height="{6*s:.1f}" rx="2" fill="{C["hub"]}" stroke="#a65e17"/>')
    return "".join(out)


def excavator_mask(scale=10, pose="up", w=92, h=56):
    img = Image.new("L", (w * scale, h * scale), 0)
    d = ImageDraw.Draw(img)
    for kind, g, role in excavator_prims(pose):
        if kind == "rrect":
            x, y, ww, hh, r = g
            d.rounded_rectangle([x * scale, y * scale, (x + ww) * scale, (y + hh) * scale], r * scale, fill=255)
        elif kind == "rect":
            x, y, ww, hh = g
            d.rectangle([x * scale, y * scale, (x + ww) * scale, (y + hh) * scale], fill=255)
        elif kind == "circles":
            pts, r = g
            for cx, cy in pts:
                d.ellipse([(cx - r) * scale, (cy - r) * scale, (cx + r) * scale, (cy + r) * scale], fill=255)
        elif kind == "line":
            x1, y1, x2, y2, ww = g
            d.line([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=255, width=int(ww * scale))
            for px, py in ((x1, y1), (x2, y2)):
                r = ww * scale / 2
                d.ellipse([px * scale - r, py * scale - r, px * scale + r, py * scale + r], fill=255)
        elif kind == "poly":
            d.polygon([(x * scale, y * scale) for x, y in g], fill=255)
    return img


def pixelated(ox, oy, s, n, w=92, h=56):
    """The excavator drawn with n blocks across its width."""
    scale = 10
    mask = excavator_mask(scale, w=w, h=h)
    cell = w / n
    rows = math.ceil(h / cell)
    out = []
    for j in range(rows):
        for i in range(n):
            box = (int(i * cell * scale), int(j * cell * scale), int((i + 1) * cell * scale), int(min((j + 1) * cell, h) * scale))
            if box[3] <= box[1]:
                continue
            region = mask.crop(box)
            mean = sum(region.tobytes()) / (255.0 * region.width * region.height)
            if mean > 0.45:
                out.append(f'<rect x="{ox+i*cell*s:.2f}" y="{oy+j*cell*s:.2f}" width="{cell*s+0.3:.2f}" height="{cell*s+0.3:.2f}" fill="{C["blue"]}"/>')
    return "".join(out)


# ------------------------------------------------------------------ figures


def fig_overview(t):
    w, h = 900, 210
    out = []
    xs = [20 + i * 176 for i in range(5)]
    for i, x in enumerate(xs):
        out.append(f'<rect x="{x}" y="22" width="150" height="120" rx="10" fill="#ffffff" stroke="{C["frame"]}"/>')
        cx, cy = x + 75, 82
        if i == 0:
            out.append(plate(x + 18, 70, u=26) + pin(x + 78, 62, 2, 1, C["black"], "#000", u=26) + pin(x + 30, 108, 3, 1, C["blue"], C["blue_d"], u=28))
        elif i == 1:
            out.append(f'<rect x="{x+20}" y="34" width="110" height="96" rx="4" fill="#eaf1fb" stroke="{C["accent"]}"/>')
            for k in range(6):
                out.append(f'<line x1="{x+20}" y1="{40+k*16}" x2="{x+130}" y2="{40+k*16}" stroke="#cfdcf0"/>')
            out.append(excavator(x + 30, 50, 1.0).replace('fill="', 'fill-opacity="0" fill="').replace('stroke="', f'stroke-dasharray="3 2" stroke="'))
        elif i == 2:
            out.append(excavator(x + 22, 40, 1.15))
            out.append(gear(x + 120, 118, 9) + beam(x + 14, 122, 3, u=12))
        elif i == 3:
            out.append(f'<path d="M{x+90} 132 q 30 -26 56 0 z" fill="{C["soil"]}" stroke="{C["soil_d"]}"/>')
            out.append(excavator(x + 20, 46, 1.15, pose="dig"))
            out.append(f'<line x1="{x+10}" y1="132" x2="{x+142}" y2="132" stroke="{C["soil_d"]}" stroke-width="2"/>')
        else:
            out.append(f'<rect x="{x+22}" y="40" width="80" height="62" rx="4" fill="#ffffff" stroke="{C["grey_d"]}"/>')
            out.append(excavator(x + 30, 50, 0.7, pose="dig"))
            out.append(f'<circle cx="{x+104}" cy="104" r="18" fill="#eaf1fb" fill-opacity="0.6" stroke="{C["accent"]}" stroke-width="3"/>'
                       f'<line x1="{x+117}" y1="117" x2="{x+134}" y2="134" stroke="{C["accent"]}" stroke-width="5" stroke-linecap="round"/>')
        out.append(text(cx, 166, t["ov"][i], 14, weight=600))
        out.append(text(cx, 188, t["ov_sub"][i], 12, C["muted"], mono=True))
        if i < 4:
            out.append(arrow(x + 152, 82, x + 174, 82))
    return svg(w, h, "".join(out))


def fig_parts(t):
    w, h = 760, 230
    out = [plate(60, 120, u=70),
           pin(290, 104, 2, 1, C["black"], "#000000", u=60),
           pin(480, 104, 3, 1, C["blue"], C["blue_d"], u=60),
           text(130, 160, t["plate"], 14, weight=600),
           text(350, 160, t["pin_s"], 14, weight=600),
           text(570, 160, t["pin_l"], 14, weight=600),
           text(w / 2, 202, t["parts_note"], 13, C["muted"])]
    return svg(w, h, "".join(out))


def fig_mould(t):
    w, h = 820, 330
    out = []
    # the mould
    out.append(f'<rect x="30" y="60" width="170" height="170" rx="8" fill="#c7ced6" stroke="{C["grey_d"]}" stroke-width="2"/>')
    out.append(f'<rect x="45" y="75" width="140" height="140" rx="6" fill="#aab3bd" stroke="{C["grey_d"]}"/>')
    for (cx, cy) in ((80, 110), (150, 110), (80, 180), (150, 180)):
        out.append(f'<rect x="{cx-22}" y="{cy-18}" width="44" height="36" rx="6" fill="#8e98a3" stroke="{C["grey_d"]}"/>')
    out.append(text(115, 255, t["mould"], 14, weight=600))
    out.append(arrow(215, 145, 285, 145))
    out.append(text(250, 132, t["inject"], 12, C["muted"]))
    # the shot: runner frame with four different parts
    out.append(f'<rect x="300" y="40" width="490" height="210" rx="10" fill="none" stroke="{C["grey_d"]}" stroke-width="5"/>')
    out.append(f'<line x1="545" y1="40" x2="545" y2="250" stroke="{C["grey_d"]}" stroke-width="5"/>')
    out.append(f'<line x1="300" y1="145" x2="790" y2="145" stroke="{C["grey_d"]}" stroke-width="5"/>')
    # parts
    out.append(plate(350, 112, u=48))                        # top-left: plate (studs)
    out.append(beam(585, 95, 5, u=30))                       # top-right: beam (holes)
    out.append(gear(420, 198, 34))                           # bottom-left: gear
    out.append(pin(590, 198, 3, 1, C["grey"], C["grey_d"], u=50))  # bottom-right: pin
    # function names
    for (x, y, name) in ((398, 70, "flux()"), (660, 70, "source()"), (480, 240, "ncp()"), (668, 240, "eigenvalue()")):
        out.append(text(x, y, name, 12, C["accent"], mono=True))
    # studs = provide, holes = need
    out.append(f'<circle cx="374" cy="88" r="14" fill="none" stroke="{C["provide"]}" stroke-width="2.5"/>')
    out.append(f'<circle cx="615" cy="95" r="13" fill="none" stroke="{C["need"]}" stroke-width="2.5"/>')
    out.append(text(300, 285, "● " + t["studs"], 13, C["provide"], anchor="start", weight=600))
    out.append(text(560, 285, "● " + t["holes"], 13, C["need"], anchor="start", weight=600))
    out.append(text(545, 26, t["shot"] + "  ·  " + t["func"], 14, weight=600))
    return svg(w, h, "".join(out))


def bag(x, y, w, h, label, number=None, small=False):
    seal = "".join(f"L{x + i * w / 12:.1f} {y + (4 if i % 2 else 0):.1f} " for i in range(13))
    out = [f'<path d="M{x} {y} {seal} L{x+w} {y+h-10} Q{x+w} {y+h} {x+w-10} {y+h} L{x+10} {y+h} Q{x} {y+h} {x} {y+h-10} Z" '
           f'fill="{C["bag"]}" stroke="{C["bag_s"]}" stroke-width="1.6"/>']
    if number is not None:
        out.append(f'<circle cx="{x+22}" cy="{y+26}" r="13" fill="{C["accent"]}"/>' + text(x + 22, y + 31, str(number), 14, "#ffffff", weight=700))
    out.append(text(x + w / 2, y + h - 16, label, 13 if small else 14, weight=600))
    return "".join(out)


def fig_bags(t):
    w, h = 900, 350
    out = [arrow(40, 34, 860, 34, color=C["accent"]), text(450, 24, t["linker"], 13, C["accent"], weight=600)]
    xs = [40, 220, 400, 580]
    for i, x in enumerate(xs):
        out.append(bag(x, 60, 150, 150, t["bags"][i], number=i + 1))
        # a few parts drawn inside each bag
        out.append(beam(x + 40, 110, 3, u=18) + gear(x + 100, 140, 14))
    # small Tarch bag with pins
    out.append(bag(760, 110, 100, 100, t["tarch"], small=True))
    out.append(pin(772, 140, 2, 1, C["black"], "#000", u=18) + pin(772, 165, 3, 1, C["blue"], C["blue_d"], u=18))
    # needs arrows (dashed, curved) from left to right
    def needs(x1, x2, y=225, lift=40):
        return (f'<path d="M{x1} {y} Q{(x1+x2)/2} {y+lift} {x2} {y}" fill="none" stroke="{C["need"]}" stroke-width="1.8" '
                f'stroke-dasharray="5 4" marker-end="url(#ah)"/>')
    out.append(needs(115, 285, lift=34) + text(200, 262, t["needs"], 12, C["need"]))
    for x1, lift in ((295, 90), (475, 66), (655, 42)):
        out.append(needs(x1, 805, y=218, lift=lift))
    out.append(text(560, 300, t["needs"], 12, C["need"]))
    out.append(text(450, 336, t["smallbag"], 13, C["muted"]))
    return svg(w, h, "".join(out))


def fig_app(t):
    w, h = 900, 320
    out = []
    # left: static
    out.append(f'<rect x="20" y="20" width="400" height="280" rx="10" fill="#ffffff" stroke="{C["frame"]}"/>')
    out.append(excavator(90, 60, 2.6))
    out.append(text(220, 258, t["static"], 14, weight=600))
    out.append(text(220, 282, t["static_sub"], 12, C["muted"]))
    # right: dynamic
    out.append(f'<rect x="440" y="20" width="440" height="280" rx="10" fill="#ffffff" stroke="{C["frame"]}"/>')
    out.append(excavator(460, 70, 2.3, hubs=True))
    out.append(text(520, 200, t["hubs"], 11, C["hub"], weight=600))
    # phone with two joysticks and two dials (generic)
    px, py = 760, 60
    out.append(f'<rect x="{px}" y="{py}" width="96" height="150" rx="14" fill="{C["black"]}"/>'
               f'<rect x="{px+7}" y="{py+12}" width="82" height="126" rx="6" fill="#e9eef5"/>')
    for (cx, cy) in ((px + 28, py + 100), (px + 68, py + 100)):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="15" fill="#ffffff" stroke="{C["grey_d"]}"/><circle cx="{cx}" cy="{cy-4}" r="6" fill="{C["accent"]}"/>')
    for k, sy in enumerate((py + 34, py + 56)):
        out.append(f'<line x1="{px+18}" y1="{sy}" x2="{px+78}" y2="{sy}" stroke="{C["grey_d"]}" stroke-width="3" stroke-linecap="round"/>'
                   f'<circle cx="{px+38+k*22}" cy="{sy}" r="6" fill="#ffffff" stroke="{C["accent"]}" stroke-width="2.5"/>')
    out.append(text(px + 48, py + 168, t["app"], 12, C["accent"], weight=600))
    # wireless waves
    for k in range(3):
        r = 14 + k * 12
        out.append(f'<path d="M{735 - r * 0.0} {140 - r} A {r} {r} 0 0 0 {735} {140 + r}" fill="none" stroke="{C["accent"]}" stroke-width="2" opacity="{0.9 - k*0.25}"/>')
    out.append(text(660, 258, t["dynamic"], 14, weight=600))
    out.append(text(660, 282, t["dynamic_sub"], 12, C["need"], mono=False))
    return svg(w, h, "".join(out))


def fig_dig(t):
    w, h = 900, 320
    out = []
    # timeline with cameras
    out.append(f'<line x1="60" y1="60" x2="840" y2="60" stroke="{C["muted"]}" stroke-width="2"/>')
    for i in range(11):
        x = 60 + i * 78
        out.append(f'<line x1="{x}" y1="54" x2="{x}" y2="66" stroke="{C["muted"]}" stroke-width="2"/>')
        out.append(text(x, 84, f"t={i/10:.1f}", 11, C["muted"], mono=True))
        if i % 2 == 0:
            out.append(f'<rect x="{x-11}" y="28" width="22" height="15" rx="3" fill="{C["ink"]}"/><circle cx="{x}" cy="35.5" r="4.5" fill="#ffffff"/>'
                       f'<rect x="{x-5}" y="24" width="8" height="5" rx="1" fill="{C["ink"]}"/>')
    out.append(text(450, 18, t["snap"], 13, weight=600))
    # ground, soil pile, excavator digging
    out.append(f'<path d="M430 270 q 70 -60 150 0 z" fill="{C["soil"]}" stroke="{C["soil_d"]}"/>')
    out.append(excavator(190, 132, 2.6, pose="dig"))
    out.append(f'<line x1="40" y1="270" x2="860" y2="270" stroke="{C["soil_d"]}" stroke-width="3"/>')
    # check: magnifier
    out.append(f'<circle cx="720" cy="180" r="34" fill="#eaf1fb" fill-opacity="0.7" stroke="{C["accent"]}" stroke-width="4"/>'
               f'<line x1="744" y1="204" x2="772" y2="232" stroke="{C["accent"]}" stroke-width="8" stroke-linecap="round"/>')
    out.append(text(720, 300, t["check"], 13, C["accent"], weight=600))
    return svg(w, h, "".join(out))


def fig_scales(t):
    w, h = 900, 260
    out = []
    s = 2.55
    for k, n in enumerate((9, 27, 81)):
        x0 = 30 + k * 290
        out.append(f'<rect x="{x0}" y="20" width="260" height="190" rx="10" fill="#ffffff" stroke="{C["frame"]}"/>')
        out.append(f'<g opacity="0.28">{excavator(x0 + 13, 45, s)}</g>')
        out.append(f'<g opacity="0.85">{pixelated(x0 + 13, 45, s, n)}</g>')
        out.append(text(x0 + 130, 200, t["scales"][k], 14, weight=600))
    out.append(text(450, 240, t["scale_note"], 13, C["muted"]))
    return svg(w, h, "".join(out))


def fig_chain(t):
    w, h = 900, 250
    out = []
    boxes = [(30, 40), (250, 40), (470, 40), (690, 150)]
    for i, (x, y) in enumerate(boxes):
        name, ext = t["chain"][i]
        fill = "#eaf1fb" if i == 3 else "#ffffff"
        out.append(f'<rect x="{x}" y="{y}" width="180" height="70" rx="10" fill="{fill}" stroke="{C["accent"] if i == 3 else C["frame"]}" stroke-width="1.6"/>')
        out.append(text(x + 90, y + 30, ext, 17, weight=700, mono=True))
        out.append(text(x + 90, y + 54, name, 13, C["muted"]))
    out.append(arrow(212, 75, 246, 75)); out.append(text(229, 64, t["chain_ops"][0], 12, C["accent"], weight=600))
    out.append(arrow(432, 75, 466, 75)); out.append(text(449, 64, t["chain_ops"][1], 12, C["accent"], weight=600))
    # .o and .a both go into the link step
    out.append(f'<path d="M340 112 L340 185 L684 185" fill="none" stroke="{C["muted"]}" stroke-width="1.8" marker-end="url(#ah)"/>')
    out.append(f'<path d="M560 112 L560 185" fill="none" stroke="{C["muted"]}" stroke-width="1.8"/>')
    out.append(text(612, 176, t["chain_ops"][2], 12, C["accent"], weight=600))
    return svg(w, h, "".join(out))


def booklet_page(x, y, w, h, fill="#ffffff"):
    return (f'<rect x="{x+4}" y="{y+4}" width="{w}" height="{h}" rx="4" fill="{C["frame"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{C["grey_d"]}" stroke-width="1.3"/>')


def dim(x1, x2, y, label):
    """Horizontal dimension line with end ticks and a label above."""
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{C["accent"]}" stroke-width="1.4"/>'
            f'<line x1="{x1}" y1="{y-6}" x2="{x1}" y2="{y+6}" stroke="{C["accent"]}" stroke-width="1.4"/>'
            f'<line x1="{x2}" y1="{y-6}" x2="{x2}" y2="{y+6}" stroke="{C["accent"]}" stroke-width="1.4"/>'
            + text((x1 + x2) / 2, y - 7, label, 11, C["accent"], weight=600))


def fig_brief(t):
    w, h = 900, 330
    out = []
    # the brief on a clipboard
    out.append(f'<rect x="30" y="40" width="250" height="230" rx="10" fill="#c99b62" stroke="#94703f" stroke-width="1.5"/>')
    out.append(f'<rect x="44" y="58" width="222" height="200" rx="4" fill="#ffffff" stroke="{C["frame"]}"/>')
    out.append(f'<rect x="125" y="32" width="60" height="18" rx="5" fill="{C["grey_d"]}"/>')
    out.append(text(155, 84, t["brief_title"], 13, weight=700))
    for i, line in enumerate(t["brief"]):
        y = 114 + i * 28
        out.append(f'<rect x="58" y="{y-11}" width="12" height="12" rx="2" fill="none" stroke="{C["provide"]}" stroke-width="1.6"/>'
                   f'<path d="M60 {y-5} l3 4 l6 -8" fill="none" stroke="{C["provide"]}" stroke-width="2"/>')
        out.append(text(78, y, line, 12, anchor="start"))
    # the designer: pencil + arrow
    out.append(arrow(296, 155, 404, 155))
    out.append(f'<g transform="rotate(-35 350 125)"><rect x="320" y="119" width="56" height="12" rx="2" fill="#f2c14e" stroke="#b58a1d"/>'
               f'<polygon points="376,119 390,125 376,131" fill="#e8d2a6" stroke="#b58a1d"/><rect x="314" y="119" width="7" height="12" fill="#e58a9a"/></g>')
    out.append(text(350, 185, t["designer"], 12, C["accent"], weight=600, mono=False))
    # the booklet: open book with a dashed excavator and dimensions
    out.append(booklet_page(420, 40, 220, 230, "#eaf1fb") + booklet_page(640, 40, 220, 230, "#eaf1fb"))
    out.append(f'<line x1="640" y1="40" x2="640" y2="270" stroke="{C["grey_d"]}" stroke-width="2"/>')
    out.append(excavator(440, 110, 1.9).replace('fill="', 'fill-opacity="0.15" fill="'))
    out.append(dim(440, 440 + 90 * 1.9, 92, t["dims"][3]))
    out.append(beam(668, 90, 15, u=12))
    out.append(text(758, 74, t["dims"][0], 11, C["muted"]))
    out.append(pin(690, 140, 3, 1, C["blue"], C["blue_d"], u=34))
    out.append(dim(690, 690 + 3 * 34, 120, t["dims"][1]))
    # 9x9x9 patch as a small cube
    cx, cy, a = 700, 190, 54
    out.append(f'<polygon points="{cx},{cy} {cx+a},{cy} {cx+a},{cy+a} {cx},{cy+a}" fill="#ffffff" stroke="{C["accent"]}"/>'
               f'<polygon points="{cx},{cy} {cx+18},{cy-14} {cx+a+18},{cy-14} {cx+a},{cy}" fill="#dbe7f7" stroke="{C["accent"]}"/>'
               f'<polygon points="{cx+a},{cy} {cx+a+18},{cy-14} {cx+a+18},{cy+a-14} {cx+a},{cy+a}" fill="#c4d6f0" stroke="{C["accent"]}"/>')
    for k in range(1, 9):
        out.append(f'<line x1="{cx+k*a/9:.1f}" y1="{cy}" x2="{cx+k*a/9:.1f}" y2="{cy+a}" stroke="#bcd0ec" stroke-width="0.8"/>'
                   f'<line x1="{cx}" y1="{cy+k*a/9:.1f}" x2="{cx+a}" y2="{cy+k*a/9:.1f}" stroke="#bcd0ec" stroke-width="0.8"/>')
    out.append(text(cx + a + 52, cy + 32, t["dims"][2], 12, C["accent"], weight=700, mono=True))
    out.append(text(640, 292, t["booklet"], 13, weight=600))
    out.append(text(450, 318, t["fixed"] + "  ·  " + t["brief_note"], 12, C["muted"]))
    return svg(w, h, "".join(out))


def card_icon(i, x, y):
    """Small drawing for card i, inside a 190 x 100 box with top-left (x, y)."""
    cx, cy = x + 95, y + 50
    if i == 0:   # cover with scale bar
        return (booklet_page(cx - 45, y + 6, 90, 88, "#eaf1fb") + excavator(cx - 38, y + 22, 0.82)
                + dim(cx - 34, cx + 34, y + 84, "1:20"))
    if i == 1:   # chassis: crossed beams over a track
        return (f'<rect x="{cx-70}" y="{cy+16}" width="140" height="24" rx="12" fill="{C["track"]}"/>'
                + "".join(f'<circle cx="{cx-56+k*22.4:.1f}" cy="{cy+28}" r="7" fill="{C["grey_d"]}" stroke="#1f2226"/>' for k in range(6))
                + beam(cx - 75, cy - 4, 11, u=13.6) + beam(cx - 75, cy - 24, 11, u=13.6))
    if i == 2:   # gears + bucket
        bucket = [(0, 0), (34, 0), (40, 26), (18, 34), (2, 18)]
        pts = " ".join(f"{cx+20+px:.1f},{cy-20+py:.1f}" for px, py in bucket)
        return (gear(cx - 46, cy, 26, teeth=14) + gear(cx - 6, cy - 14, 15, teeth=10, color="#c9cdd0")
                + f'<polygon points="{pts}" fill="{C["track"]}" stroke="{C["track"]}" stroke-linejoin="round"/>')
    if i == 3:   # two modules with shared holes highlighted
        u, ax = 11, cx - 90
        bx = ax + 6 * u                      # B's first 3 holes sit under A's last 3
        out = beam(ax, cy - 14, 9, u=u) + beam(bx, cy + 14, 9, u=u, color="#9fb8de")
        for k in range(3):
            out += f'<circle cx="{ax+(6+k+0.5)*u:.1f}" cy="{cy-14}" r="3.3" fill="{C["need"]}"/>'
            out += f'<circle cx="{bx+(k+0.5)*u:.1f}" cy="{cy+14}" r="3.3" fill="{C["need"]}"/>'
        return out
    if i == 4:   # an instruction step: number, part, arrow
        return (booklet_page(cx - 60, y + 6, 120, 88) + text(cx - 44, y + 32, "12", 18, C["accent"], weight=700)
                + beam(cx - 20, y + 66, 5, u=12) + pin(cx - 10, y + 32, 2, 1, C["black"], "#000", u=16)
                + arrow(cx + 6, y + 44, cx + 6, y + 58) + text(cx + 44, y + 30, "×3", 12, C["muted"], weight=600))
    if i == 5:   # pages in order
        out = ""
        for k in range(3):
            px = cx - 78 + k * 56
            out += booklet_page(px, y + 18, 44, 60) + text(px + 22, y + 56, str(k + 1), 16, C["accent"], weight=700)
            if k < 2:
                out += arrow(px + 48, y + 48, px + 54, y + 48)
        return out
    if i == 6:   # page 1 with a start flag
        return (booklet_page(cx - 45, y + 6, 90, 88) + text(cx - 28, y + 30, "1", 18, C["accent"], weight=700)
                + f'<line x1="{cx+4}" y1="{y+22}" x2="{cx+4}" y2="{y+82}" stroke="{C["ink"]}" stroke-width="2"/>'
                + f'<path d="M{cx+5} {y+22} l28 8 l-28 8 z" fill="{C["provide"]}"/>')
    # i == 7: parts list on the back cover with numbered bags
    out = booklet_page(cx - 80, y + 6, 160, 88)
    for k in range(4):
        bx = cx - 70 + k * 36
        out += (f'<rect x="{bx}" y="{y+20}" width="28" height="32" rx="4" fill="{C["bag"]}" stroke="{C["bag_s"]}"/>'
                + text(bx + 14, y + 41, str(k + 1), 12, C["accent"], weight=700))
    out += pin(cx - 66, y + 74, 2, 1, C["black"], "#000", u=14) + pin(cx - 22, y + 74, 3, 1, C["blue"], C["blue_d"], u=14)
    out += text(cx + 52, y + 78, "×120", 11, C["muted"], mono=True)
    return out


def fig_booklet(t):
    w, h = 900, 500
    out = []
    for i, (name, label) in enumerate(t["cards"]):
        col, row = i % 4, i // 4
        x, y = 20 + col * 218, 20 + row * 238
        out.append(f'<rect x="{x}" y="{y}" width="208" height="224" rx="10" fill="#ffffff" stroke="{C["frame"]}"/>')
        out.append(card_icon(i, x + 9, y + 14))
        out.append(text(x + 104, y + 150, name, 12.5, weight=700, mono=True))
        # wrap the label onto at most two lines
        words = label.split(" ") if (" " in label and "\n" not in label) else None
        lines = []
        if words:
            cur = ""
            for wd in words:
                if len(cur) + len(wd) + 1 > 26 and cur:
                    lines.append(cur); cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            lines.append(cur)
        else:
            lines = label.split("\n")
        for k, line in enumerate(lines[:3]):
            out.append(text(x + 104, y + 176 + k * 18, line, 12, C["muted"]))
    return svg(w, h, "".join(out))


def fig_halo(t):
    w, h = 900, 280
    u = 40
    out = []
    ax, ay = 40, 90
    bx, by = ax + 9 * u - 3 * u, 190   # B starts 3 holes before A ends... shown below, offset by the halo
    bx = ax + 9 * u
    # module A: 9 own holes + 3 halo holes on the right
    out.append(f'<rect x="{ax}" y="{ay-u/2}" width="{12*u}" height="{u}" rx="{u/2}" fill="{C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.4"/>')
    for k in range(12):
        halo = k >= 9
        out.append(f'<circle cx="{ax+(k+0.5)*u}" cy="{ay}" r="{u*0.3}" fill="{C["need"] if halo else C["bg"]}" '
                   f'stroke="{C["grey_d"]}" fill-opacity="{0.85 if halo else 1}"/>')
    # module B: 3 halo holes on the left + 9 own holes, shifted so that columns line up
    bx0 = ax + 6 * u
    out.append(f'<rect x="{bx0}" y="{by-u/2}" width="{12*u}" height="{u}" rx="{u/2}" fill="#9fb8de" stroke="{C["blue_d"]}" stroke-width="1.4"/>')
    for k in range(12):
        halo = k < 3
        out.append(f'<circle cx="{bx0+(k+0.5)*u}" cy="{by}" r="{u*0.3}" fill="{C["need"] if halo else C["bg"]}" '
                   f'stroke="{C["blue_d"]}" fill-opacity="{0.85 if halo else 1}"/>')
    # copy arrows: B's first 3 own holes -> A's halo, A's last 3 own holes -> B's halo
    for k in range(3):
        xa = ax + (9 + k + 0.5) * u
        out.append(arrow(xa, by - u / 2 - 4, xa, ay + u / 2 + 4, color=C["blue_d"]))
        xb = bx0 + (k + 0.5) * u
        out.append(arrow(xb, ay + u / 2 + 4, xb, by - u / 2 - 4, color=C["grey_d"]))
    out.append(text(ax + 4.5 * u, ay - 32, t["halo_a"], 13, weight=600))
    out.append(text(ax + 10.5 * u, ay - 32, t["halo_copy"], 12, C["need"], weight=600))
    out.append(text(bx0 + 7.5 * u, by + 42, t["halo_b"], 13, C["blue_d"], weight=600))
    out.append(text(bx0 + 1.5 * u, by + 42, t["halo_copy_b"], 12, C["need"], weight=600))
    out.append(text(450, 268, t["halo_note"], 12, C["muted"]))
    return svg(w, h, "".join(out))


def fig_drive(t):
    w, h = 900, 300
    out = []
    y = 130
    # motor
    out.append(f'<rect x="40" y="{y-40}" width="96" height="80" rx="12" fill="{C["black"]}" stroke="#000"/>'
               f'<rect x="52" y="{y-28}" width="20" height="56" rx="4" fill="#45484c"/>'
               f'<circle cx="112" cy="{y}" r="10" fill="{C["grey_d"]}" stroke="#000"/>'
               f'<line x1="122" y1="{y}" x2="168" y2="{y}" stroke="{C["grey_d"]}" stroke-width="6"/>')
    # reduction: small gear drives big gear
    out.append(gear(180, y, 16, teeth=8) + gear(236, y, 42, teeth=20, color="#c9cdd0"))
    out.append(f'<line x1="278" y1="{y}" x2="340" y2="{y}" stroke="{C["grey_d"]}" stroke-width="6"/>')
    # clutch gear: gear with an inner ring and slip marks
    out.append(gear(380, y, 40, teeth=24, color="#f1f1ee", dark=C["grey_d"]))
    out.append(f'<circle cx="380" cy="{y}" r="20" fill="#dcdcd6" stroke="{C["grey_d"]}" stroke-width="1.5"/>')
    for k in range(6):
        a = math.pi * k / 3
        out.append(f'<line x1="{380+12*math.cos(a):.1f}" y1="{y+12*math.sin(a):.1f}" x2="{380+19*math.cos(a):.1f}" y2="{y+19*math.sin(a):.1f}" stroke="{C["grey_d"]}" stroke-width="2"/>')
    out.append(f'<path d="M352 {y-62} q 8 -8 16 0 t 16 0 t 16 0" fill="none" stroke="{C["need"]}" stroke-width="2.2"/>')
    out.append(f'<line x1="420" y1="{y}" x2="472" y2="{y}" stroke="{C["grey_d"]}" stroke-width="6"/>')
    # turntable: big ring gear seen from the side, with the upper body on top
    out.append(f'<rect x="480" y="{y-6}" width="150" height="34" rx="6" fill="{C["grey_d"]}" stroke="#4d5357"/>')
    for k in range(14):
        out.append(f'<rect x="{484+k*10.5:.1f}" y="{y+22}" width="6" height="8" fill="#4d5357"/>')
    out.append(f'<rect x="490" y="{y-48}" width="130" height="42" rx="6" fill="{C["body"]}" stroke="{C["body_s"]}" stroke-width="1.4"/>')
    out.append(f'<path d="M640 {y-30} a 50 22 0 0 1 0 44" fill="none" stroke="{C["accent"]}" stroke-width="2" marker-end="url(#ah)"/>')
    # bucket on the stick
    for (x1, y1, x2, y2) in ((600, y - 34, 680, y - 84), (680, y - 84, 760, y - 20)):
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["body_s"]}" stroke-width="14" stroke-linecap="round"/>'
                   f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["body"]}" stroke-width="10" stroke-linecap="round"/>')
    out.append(f'<polygon points="748,{y-26} 800,{y-26} 808,{y+12} 778,{y+26} 752,{y+6}" fill="{C["track"]}" stroke="{C["track"]}" stroke-linejoin="round"/>')
    for k in range(4):
        out.append(f'<polygon points="{780+k*7},{y+22} {786+k*7},{y+22} {783+k*7},{y+32}" fill="{C["track"]}"/>')
    xs = [88, 220, 380, 555, 775]
    for i, x in enumerate(xs):
        out.append(text(x, 222, t["drive"][i], 14, weight=600))
        out.append(text(x, 244, t["drive_sub"][i], 12, C["muted"]))
    out.append(text(450, 282, t["drive_note"], 13, C["muted"]))
    return svg(w, h, "".join(out))


def actuator(x, y, ext, scale=1.0):
    """Linear actuator side view; (x, y) = centre of the input end; ext = rod extension in px."""
    L, H = 150 * scale, 26 * scale
    out = [f'<rect x="{x}" y="{y-H/2}" width="{L}" height="{H}" rx="{H/2.6:.1f}" fill="{C["black"]}" stroke="#000"/>',
           f'<line x1="{x+10*scale}" y1="{y-H/2+5*scale}" x2="{x+L-10*scale}" y2="{y-H/2+5*scale}" stroke="#ffffff" stroke-opacity="0.25" stroke-width="2"/>',
           f'<rect x="{x+L}" y="{y-6*scale}" width="{40*scale+ext}" height="{12*scale}" rx="3" fill="#c9cdd0" stroke="{C["grey_d"]}"/>',
           f'<circle cx="{x+L+40*scale+ext}" cy="{y}" r="{11*scale}" fill="{C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.4"/>',
           f'<circle cx="{x+L+40*scale+ext}" cy="{y}" r="{4.5*scale}" fill="{C["bg"]}" stroke="{C["grey_d"]}"/>',
           f'<circle cx="{x}" cy="{y}" r="{12*scale}" fill="{C["grey"]}" stroke="{C["grey_d"]}" stroke-width="1.4"/>',
           f'<path d="M{x-4*scale} {y} h{8*scale} M{x} {y-4*scale} v{8*scale}" stroke="{C["ink"]}" stroke-width="2.4"/>']
    return "".join(out)


def fig_actuator(t):
    w, h = 900, 330
    out = []
    # left: retracted and extended
    out.append(actuator(70, 90, 0))
    out.append(text(300, 95, t["act"][0], 13, C["muted"], anchor="start"))
    out.append(actuator(70, 170, 90))
    out.append(arrow(268, 196, 352, 196, color=C["accent"]))
    out.append(text(390, 175, t["act"][1], 13, C["muted"], anchor="start"))
    out.append(f'<path d="M52 {214} a 20 20 0 1 1 30 0" fill="none" stroke="{C["need"]}" stroke-width="2" marker-end="url(#ah)"/>')
    out.append(text(96, 222, t["act_in"], 12, C["need"], anchor="start"))
    out.append(text(220, 272, t["act_part"], 14, weight=600))
    # right: on the machine, actuator between upper body and boom
    ox, oy = 520, 70
    out.append(f'<rect x="{ox}" y="{oy+120}" width="160" height="34" rx="14" fill="{C["track"]}"/>')
    out.append(f'<rect x="{ox+10}" y="{oy+80}" width="120" height="40" rx="6" fill="{C["body"]}" stroke="{C["body_s"]}"/>')
    for (x1, y1, x2, y2, wd) in ((ox+110, oy+90, ox+210, oy+10, 16), (ox+210, oy+10, ox+300, oy+110, 13)):
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["body_s"]}" stroke-width="{wd+4}" stroke-linecap="round"/>'
                   f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["body"]}" stroke-width="{wd}" stroke-linecap="round"/>')
    out.append(f'<polygon points="{ox+288},{oy+104} {ox+330},{oy+104} {ox+336},{oy+136} {ox+312},{oy+148} {ox+292},{oy+130}" fill="{C["track"]}"/>')
    # two actuators, drawn as rotated small actuators
    for (cx, cy, ang, ext) in ((ox+80, oy+96, -48, 10), (ox+170, oy+44, -8, 6)):
        out.append(f'<g transform="rotate({ang} {cx} {cy})">{actuator(cx, cy, ext, scale=0.5)}</g>')
    out.append(text(ox + 170, 272, t["act_use"], 13, weight=600))
    out.append(text(450, 310, t["act_note"], 13, C["muted"]))
    return svg(w, h, "".join(out))


FIGURES = {"overview": fig_overview, "parts": fig_parts, "mould": fig_mould, "bags": fig_bags,
           "app": fig_app, "dig": fig_dig, "scales": fig_scales, "chain": fig_chain,
           "brief": fig_brief, "booklet": fig_booklet, "halo": fig_halo,
           "drive": fig_drive, "actuator": fig_actuator}


def main():
    for lang, t in L.items():
        for name, fn in FIGURES.items():
            path = os.path.join(HERE, f"{name}.{lang}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fn(t))
            print("wrote", os.path.relpath(path, HERE))


if __name__ == "__main__":
    main()
