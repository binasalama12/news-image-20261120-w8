#!/usr/bin/env python3
"""Warm Postcard — one day of world news, Friday 20 November 2026.

A single-page newspaper drawn from scratch with PIL: masthead, UTC timeline,
region strip, three hero panels, thirteen pictured panels, a dot-matrix world
map with numbered pins, thirty-two briefs, a date-check box and a footer.
Warm palette: cream paper, terracotta, ochre, brown.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1600
M = 44
CW = W - 2 * M

PAPER = (247, 240, 226)
CREAM = (252, 247, 236)
INK = (43, 32, 24)
TERRA = (186, 74, 42)
TERRA_D = (150, 52, 32)
OCHRE = (206, 150, 60)
BROWN = (96, 62, 38)
BROWN_D = (66, 42, 26)
SAGE = (122, 132, 84)
TEAL = (46, 110, 105)
NAVY = (38, 62, 84)
SKY = (186, 205, 214)
SKY_D = (120, 150, 175)
NIGHT = (24, 34, 54)
GOLD = (232, 178, 80)
WHITE = (250, 246, 238)

DJ = "/usr/share/fonts/truetype/dejavu/"
LB = "/usr/share/fonts/truetype/liberation/"


def sans(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(DJ + name, size)
    except OSError:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            return ImageFont.load_default()


def serif(size, bold=False, italic=False):
    if italic:
        name = "LiberationSerif-Italic.ttf"
    elif bold:
        name = "LiberationSerif-Bold.ttf"
    else:
        name = "LiberationSerif-Regular.ttf"
    try:
        return ImageFont.truetype(LB + name, size)
    except OSError:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            return ImageFont.load_default()


def wrap(d, text, font, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def ellipsize(d, text, font, width):
    if d.textlength(text, font=font) <= width:
        return text
    while text and d.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text + "…"


def text_block(d, x, y, text, font, width, leading, fill, max_lines=None):
    lines = wrap(d, text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = ellipsize(d, lines[-1], font, width)
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def paper_texture(d, seed=11):
    rnd = random.Random(seed)
    for _ in range(5200):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(0, H - 1)
        n = rnd.randint(-9, 9)
        base = PAPER
        d.point((x, y), fill=(base[0] + n, base[1] + n, base[2] + n))


def sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=col)


def sun(d, cx, cy, r, col=GOLD):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x1 = cx + int(math.cos(a) * (r + 3))
        y1 = cy + int(math.sin(a) * (r + 3))
        x2 = cx + int(math.cos(a) * (r + 11))
        y2 = cy + int(math.sin(a) * (r + 11))
        d.line([(x1, y1), (x2, y2)], fill=col, width=3)


def skyline(d, x, y, w, h, col, seed=3, lit=False):
    rnd = random.Random(seed)
    bx = x
    while bx < x + w - 14:
        bw = rnd.randint(15, 40)
        bh = rnd.randint(int(h * 0.35), int(h * 0.95))
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=col)
        if lit:
            for _ in range(4):
                wx = rnd.randint(bx + 3, bx + bw - 4)
                wy = rnd.randint(y + h - bh + 4, y + h - 6)
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=GOLD)
        bx += bw + 3


def waves(d, x, y, w, h, col, seed=5):
    rnd = random.Random(seed)
    for row in range(3):
        yy = y + int(h * (0.25 + row * 0.3))
        for xx in range(x, x + w, 26):
            d.arc([xx, yy, xx + 26, yy + 12], 180, 360, fill=col, width=3)


def flag(d, x, y, w, h, kind):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    if kind == "us":
        d.rectangle([x, y, x + w, y + h], fill=(178, 52, 52))
        for i in range(4):
            d.rectangle([x, y + i * h // 4 + h // 8, x + w, y + i * h // 4 + h // 4], fill=WHITE)
        d.rectangle([x, y, x + w // 2, y + h // 2], fill=NAVY)
    elif kind == "cn":
        d.rectangle([x, y, x + w, y + h], fill=(196, 40, 40))
        d.ellipse([x + 3, y + 3, x + 11, y + 11], fill=GOLD)
    elif kind == "ru":
        d.rectangle([x, y, x + w, y + h // 3], fill=WHITE)
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(52, 90, 160))
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(178, 52, 52))
    elif kind == "in":
        d.rectangle([x, y, x + w, y + h // 3], fill=(232, 150, 50))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=WHITE)
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(60, 140, 90))
    else:
        d.rectangle([x, y, x + w, y + h], fill=OCHRE)


def tag20(d, x, y, w):
    tw = 62
    d.rectangle([x + w - tw, y, x + w, y + 24], fill=TERRA)
    d.text((x + w - tw + 7, y + 4), "20 NOV", font=sans(14, True), fill=WHITE)


def scene(d, x, y, w, h, idx):
    d.rectangle([x, y, x + w, y + h], outline=BROWN, width=1)
    if idx == 1:
        sky(d, x, y, w, h, (52, 96, 110), (24, 44, 66))
        for i in range(5):
            d.arc([x + w // 2 - 46 + i * 9, y + 18 + i * 9,
                   x + w // 2 + 46 - i * 9, y + 110 - i * 9],
                  200, 500, fill=(210, 225, 230), width=4)
        for k in range(26):
            rx = x + random.Random(idx * 7 + k).randint(0, w)
            ry = y + random.Random(idx * 3 + k).randint(0, h)
            d.line([(rx, ry), (rx - 5, ry + 12)], fill=(200, 215, 225), width=2)
        waves(d, x, y + h - 26, w, 26, (210, 225, 230))
    elif idx == 2:
        sky(d, x, y, w, h, NIGHT, (58, 48, 70))
        skyline(d, x, y + 20, w, h - 20, (16, 20, 34), seed=9, lit=True)
        d.line([(x + 20, y + h - 30), (x + w // 2, y + 12)], fill=(232, 140, 60), width=4)
        d.line([(x + w // 2, y + 12), (x + w - 30, y + h - 40)], fill=(232, 140, 60), width=4)
        sun(d, x + w // 2, y + 16, 12, (232, 140, 60))
    elif idx == 3:
        sky(d, x, y, w, h, (232, 178, 110), (150, 90, 70))
        sun(d, x + w - 60, y + 34, 20)
        skyline(d, x, y + 30, w, h - 30, (70, 52, 44), seed=4)
        flag(d, x + 26, y + 18, 46, 28, "us")
        flag(d, x + 92, y + 18, 46, 28, "cn")
        flag(d, x + 158, y + 18, 46, 28, "ru")
    elif idx == 4:
        sky(d, x, y, w, h, SKY, (200, 210, 200))
        d.arc([x + 10, y + h - 26, x + w - 10, y + h + 60], 180, 360, fill=BROWN_D, width=5)
        d.line([(x + 10, y + h - 14), (x + w - 10, y + h - 14)], fill=BROWN_D, width=4)
        sun(d, x + w - 40, y + 22, 12)
        d.ellipse([x + w // 2 - 8, y + h - 46, x + w // 2 + 8, y + h - 30], fill=(232, 140, 60))
    elif idx == 5:
        sky(d, x, y, w, h, (210, 190, 150), (150, 110, 80))
        skyline(d, x, y + 16, w, h - 16, (90, 66, 48), seed=6)
        flag(d, x + 20, y + 8, 34, 20, "cn")
        flag(d, x + 66, y + 8, 34, 20, "us")
    elif idx == 6:
        sky(d, x, y, w, h, (240, 210, 140), (220, 160, 90))
        sun(d, x + w // 2, y + 26, 16)
        d.ellipse([x + 20, y + h - 30, x + w - 20, y + h - 8], fill=SAGE)
        d.polygon([(x + w // 2, y + 18), (x + w // 2 - 16, y + 44),
                   (x + w // 2 + 16, y + 44)], fill=(90, 140, 70))
        d.line([(x + w // 2, y + 20), (x + w // 2, y + 44)], fill=(60, 110, 50), width=2)
    elif idx == 7:
        sky(d, x, y, w, h, (200, 190, 170), (150, 130, 110))
        d.line([(x + w // 2, y + 10), (x + w // 2, y + h - 14)], fill=BROWN_D, width=4)
        d.line([(x + 30, y + 22), (x + w - 30, y + 22)], fill=BROWN_D, width=4)
        d.polygon([(x + 40, y + 22), (x + 24, y + 46), (x + 56, y + 46)], outline=BROWN_D, width=3)
        d.polygon([(x + w - 40, y + 22), (x + w - 56, y + 22), (x + w - 24, y + 46)], outline=BROWN_D, width=3)
    elif idx == 8:
        sky(d, x, y, w, h, CREAM, (232, 220, 200))
        pts = [(x + 10, y + 16), (x + w // 4, y + 30), (x + w // 2, y + 24),
               (x + 3 * w // 4, y + 44), (x + w - 10, y + h - 12)]
        d.line(pts, fill=TERRA, width=4)
        for px, py in pts:
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=TERRA)
        d.text((x + 10, y + h - 24), "-2.25%", font=sans(13, True), fill=TERRA)
    elif idx == 9:
        sky(d, x, y, w, h, (250, 190, 120), (120, 60, 110))
        sun(d, x + w - 44, y + 26, 18, (250, 220, 130))
        skyline(d, x, y + 22, w, h - 22, (60, 40, 70), seed=8)
        d.rectangle([x + 16, y + h - 34, x + 62, y + h - 10], fill=(30, 30, 40))
        d.rectangle([x + 24, y + h - 28, x + 54, y + h - 16], fill=(120, 220, 130))
    elif idx == 10:
        sky(d, x, y, w, h, NIGHT, (10, 12, 28))
        rnd = random.Random(10)
        for _ in range(30):
            sx = x + rnd.randint(0, w)
            sy = y + rnd.randint(0, h)
            d.point((sx, sy), fill=WHITE)
        d.ellipse([x + w // 2 - 6, y + h // 2 - 6, x + w // 2 + 6, y + h // 2 + 6], fill=GOLD)
        d.line([(x + 12, y + h - 12), (x + w // 2, y + h // 2)], fill=GOLD, width=2)
    elif idx == 11:
        sky(d, x, y, w, h, (220, 200, 170), (170, 140, 110))
        d.rectangle([x + 20, y + h - 22, x + w - 20, y + h - 12], fill=BROWN)
        d.rectangle([x + w // 2 - 5, y + 14, x + w // 2 + 5, y + h - 22], fill=BROWN_D, width=2)
        d.ellipse([x + w // 2 - 22, y + 10, x + w // 2 + 22, y + 30], fill=BROWN_D)
    elif idx == 12:
        sky(d, x, y, w, h, (245, 205, 130), (220, 150, 80))
        sun(d, x + w // 2, y + 24, 15)
        d.ellipse([x + 14, y + h - 26, x + w - 14, y + h - 8], fill=(200, 160, 100))
        for xx in range(x + 16, x + w - 16, 30):
            d.line([(xx, y + h - 12), (xx + 7, y + h - 20)], fill=BROWN_D, width=2)
            d.line([(xx + 7, y + h - 20), (xx + 14, y + h - 14)], fill=BROWN_D, width=2)
    elif idx == 13:
        sky(d, x, y, w, h, (30, 40, 70), (70, 60, 90))
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=GOLD)
        for k in range(3):
            d.ellipse([cx - 34, cy - 13, cx + 34, cy + 13], outline=(200, 210, 230), width=2)
    elif idx == 14:
        sky(d, x, y, w, h, (200, 220, 200), (140, 170, 140))
        flag(d, x + 24, y + 14, 44, 26, "us")
        flag(d, x + w - 68, y + 14, 44, 26, "in")
        d.line([(x + 30, y + h - 16), (x + w - 30, y + h - 16)], fill=BROWN_D, width=4)
    elif idx == 15:
        sky(d, x, y, w, h, (190, 200, 205), (120, 140, 150))
        d.rectangle([x + w // 2 - 46, y + 18, x + w // 2 + 46, y + 40], fill=BROWN_D)
        d.rectangle([x + w // 2 - 30, y + 8, x + w // 2 + 30, y + 18], fill=TERRA)
        waves(d, x, y + h - 24, w, 24, (90, 120, 140))
    else:
        sky(d, x, y, w, h, (150, 190, 120), (90, 140, 90))
        d.rectangle([x + 30, y + 14, x + 44, y + h - 14], fill=(210, 190, 140))
        d.ellipse([x + w - 52, y + 16, x + w - 36, y + 32], fill=(200, 50, 50))
        d.ellipse([x + 20, y + h - 30, x + w - 20, y + h - 12], fill=(90, 140, 90))
    tag20(d, x, y, w)


HEROES = [
    ("1 · ODISHA · STORM", "Akvan comes ashore on the Odisha coast",
     "Cyclone Akvan crossed the coast near Gopalpur at noon, winds 90-100 km/h "
     "gusting to 110. Three hundred thousand people are out of harm's way, "
     "423 rescue teams deployed, red alerts in 11 districts.",
     "IMD · THE HINDU", 1),
    ("2 · RIYADH · ATTACK", "Houthi missile hits Riyadh's KAFD financial district",
     "A Houthi missile damaged a wealth-fund tower in the financial district, "
     "one of Riyadh's tallest. No casualties are reported, as air defences "
     "answered the strike.",
     "ARAB NEWS · REUTERS", 2),
    ("3 · SHENZHEN · DIPLOMACY", "Trump, Xi and Putin issue a joint declaration",
     "No big peace deal from the trilateral's second day. Trump says the Iran "
     "war call waits until 2027, rates the summit '12 out of 10', and Putin "
     "may attend December's G20 in Miami.",
     "REUTERS · AP", 3),
]

PICTURED = [
    ("4 · KERCH STRAIT · WAR", "Crimean Bridge hit a third time this week; rail halted",
     "A Ukrainian naval drone strike disrupted rail traffic on the bridge. "
     "Rail partly resumes; Putin vows retaliation, and Kyiv was hit by drones.",
     "CLAIM · KYIV", 4),
    ("5 · SHENZHEN · SUMMIT", "APEC leaders meet in Shenzhen",
     "Leaders gather in China for the APEC summit. Xi urges APEC economies "
     "to back open trade and new technology.", "AP", 5),
    ("6 · ANTALYA · CLIMATE", "COP31's final day: fossil fuels cut from the text",
     "A revised draft strips out every fossil-fuel phase-out pledge. "
     "Delegates push back as the final plenary meets today.", "UNFCCC · AFP", 6),
    ("7 · THE HAGUE · LAW", "The world answers the genocide verdict",
     "Britain expels Myanmar's defence attache and seeks an urgent Security "
     "Council meeting. The Gambia hails a 'historic' verdict.", "AP · BBC", 7),
    ("8 · NEW YORK · MARKETS", "Anthropic's debut can't stop the slide",
     "The Dow fell 1,084 points, the S&P 2.02% and the Nasdaq 2.25%, as the "
     "AI selloff bit a day after Anthropic's record debut.", "BLOOMBERG", 8),
    ("9 · VICE CITY · GAMES", "GTA VI passes The Odyssey's $1.84bn",
     "Launch-day sales top The Odyssey's $1.80bn global run, Sensor Tower "
     "estimates. Reviews land; Rockstar calls it the highest-rated game ever.",
     "SENSOR TOWER", 9),
    ("10 · SPACE · SCIENCE", "NASA confirms Voyager 1's light-day milestone",
     "The probe is now a full light-day from Earth — 16 billion miles out, "
     "the farthest any human-made object has ever travelled.", "NASA · JPL", 10),
    ("11 · SEOUL · LAW", "South Korea clears ex-PM Han",
     "The Supreme Court overturns former prime minister Han Duck-soo's "
     "conviction, in the case tied to the 2024 martial-law declaration.",
     "KOREA TIMES", 11),
    ("12 · SUVA · CLIMATE", "Fiji declares a national disaster over drought",
     "Fiji declares a national disaster over drought and water shortages. "
     "El Nino leaves water short across the islands.", "AFP", 12),
    ("13 · VIENNA · SECURITY", "North Korea expands uranium enrichment at Yongbyon",
     "The UN watchdog reports growth at the nuclear site, in its latest "
     "assessment of the Yongbyon complex.", "IAEA", 13),
    ("14 · CARACAS · DIPLOMACY", "US and Venezuela restore military cooperation",
     "The two countries sign an agreement to work together again, restoring "
     "a military channel closed for years.", "REUTERS", 14),
    ("15 · HORMUZ · CONFLICT", "ADNOC vessel attacked in the Strait of Hormuz",
     "One crew member is missing after the strike on the ADNOC vessel in "
     "the strait.", "REUTERS", 15),
    ("16 · WELLINGTON · CRICKET", "Day two at the Basin: Nicholls' 113 anchors New Zealand",
     "New Zealand build on Henry Nicholls' unbeaten 113 as India hunt early "
     "wickets, in the first Test at the Basin Reserve.", "AP", 16),
]

BRIEFS = [
    (17, "BRUSSELS", "EU-UK summit opens"),
    (18, "NEW DELHI", "Modi meets William and Kate"),
    (19, "DHAKA", "Fire at the Yunus home; arson feared"),
    (20, "MUMBAI", "Sensex +1.21%, Nifty +1.14% on the day"),
    (21, "TOKYO", "Hayabusa2 gives up landing; mission rewritten"),
    (22, "BERLIN", "Coalition of the Willing meets in Berlin"),
    (23, "BERLIN", "Merz hosts Qatar's emir in Berlin"),
    (24, "NEW DELHI", "Pakistan minister leads delegation to Delhi for SCO"),
    (25, "MANILA", "Philippines-Chile trade deal signed"),
    (26, "MANILA", "Musk plans Philippines projects"),
    (27, "HONG KONG", "India beats Malaysia, Asian Hockey Trophy opens"),
    (28, "IPOH", "Harimau Shakti exercise opens in Ipoh"),
    (29, "NEW DELHI", "India's electronics exports jump 44%"),
    (30, "NEW DELHI", "ICMR completes 100 tech transfers"),
    (31, "NEW DELHI", "India unveils its first bird-flu vaccine"),
    (32, "GENEVA", "World Children's Day marked worldwide"),
    (33, "EUROPE", "Youth anti-war protests across Europe"),
    (34, "BRUSSELS", "EU delays its methane rules by 24 months"),
    (35, "COLOGNE", "Bayern Munich beat Koln 3-0"),
    (36, "U17 CUP", "Argentina 0-2 Australia at the U17 Cup"),
    (37, "WASHINGTON", "Jobless claims come in at 203,000"),
    (38, "STRASBOURG", "NATO's assembly opens its 72nd session"),
    (39, "HANOI", "Azerbaijan's Aliyev visits Vietnam"),
    (40, "MARKETS", "Crude futures fall over 3%"),
    (41, "KHARTOUM", "Sudan army: two-year El Obeid siege broken"),
    (42, "MOGADISHU", "Somalia gives UAE ambassador 72 hours to leave"),
    (43, "SAN SALVADOR", "Migrant boat capsizes off El Salvador; dozens missing"),
    (44, "PORT-AU-PRINCE", "Haiti approves Salvadoran troop deal vs gangs"),
    (45, "ARABIAN SEA", "Amur falcons cross the Arabian Sea"),
    (46, "NEW YORK", "Al-Saadi appears in a New York court over a UK plot"),
    (47, "KYIV", "Witkoff and Kushner brief Zelenskyy"),
    (48, "BEIJING", "Xi urges APEC to back open trade, new tech"),
]

MAP_ROWS = [
    "   #########       ####      ##########################   ",
    "  ###########     #####   ##############################  ",
    "  ############     ###    #############################   ",
    "   ##########      ##  ######  ####################      ",
    "    ########        #########  #######  ##########        ",
    "     #####         ##########   ####   #######            ",
    "      ###          #########    ##    #####               ",
    "      ###           #######          ######               ",
    "       ##            #####           ########             ",
    "       ##             ###             ######    ##         ",
    "        #              #               ####      #          ",
]

PINS = {
    4: (37, 45), 5: (114, 22), 6: (30, 36), 7: (4, 52),
    8: (-74, 40), 9: (-80, 25), 10: (150, -25), 11: (127, 37),
    12: (178, -18), 13: (16, 48), 14: (-67, 10), 15: (56, 26),
    16: (175, -41),
}

REGIONS = [
    ("EUROPE", 11, (58, 90, 130)),
    ("THE AMERICAS", 7, TEAL),
    ("ASIA-PACIFIC", 19, TERRA),
    ("MIDEAST", 3, OCHRE),
    ("AFRICA", 2, SAGE),
    ("OCEANIA", 2, (120, 140, 170)),
    ("WORLD", 4, (110, 100, 90)),
]

TIMELINE = ("THE DAY IN UTC — OVERNIGHT Crimean Bridge hit a third time · "
            "06:00 APEC leaders meet in Shenzhen · 10:00 Trilateral declaration "
            "issued · 12:00 Akvan makes landfall in Odisha · 14:00 Houthi missile "
            "hits Riyadh KAFD · LATE Wall Street slides; Dow -1,084")


def hero_panel(d, x, y, w, kicker, head, dek, source, idx):
    d.rounded_rectangle([x, y, x + w, y + 330], radius=14,
                        fill=CREAM, outline=BROWN, width=2)
    scene(d, x + 8, y + 8, w - 16, 148, idx)
    ky = y + 166
    d.text((x + 14, ky), kicker, font=sans(15, True), fill=TERRA)
    sw = d.textlength(source, font=sans(13, True))
    d.text((x + w - 14 - sw, ky + 1), source, font=sans(13, True), fill=BROWN)
    hy = ky + 26
    hy = text_block(d, x + 14, hy, head, serif(31, True), w - 28, 35, INK, max_lines=2)
    text_block(d, x + 14, hy + 4, dek, sans(16), w - 28, 20, (70, 60, 48), max_lines=3)


def pictured_panel(d, x, y, w, kicker, head, dek, source, idx):
    d.rounded_rectangle([x, y, x + w, y + 182], radius=10,
                        fill=CREAM, outline=BROWN, width=1)
    scene(d, x + 6, y + 6, w - 12, 70, idx)
    ky = y + 84
    d.text((x + 10, ky), kicker, font=sans(12, True), fill=TERRA)
    hy = ky + 19
    hy = text_block(d, x + 10, hy, head, serif(19, True), w - 20, 22, INK, max_lines=2)
    text_block(d, x + 10, hy + 2, dek, sans(12), w - 20, 15, (70, 60, 48), max_lines=2)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    cols = len(MAP_ROWS[0])
    rows = len(MAP_ROWS)
    dx = w / cols
    dy = h / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = x + c * dx + dx / 2
                cy = y + r * dy + dy / 2
                d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(170, 185, 200))
    for num, (lon, lat) in sorted(PINS.items()):
        px = x + (lon + 170) / 360.0 * w
        py = y + (75 - lat) / 130.0 * h
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=TERRA, outline=WHITE, width=2)
        label = str(num)
        tw = d.textlength(label, font=sans(12, True))
        d.text((px - tw / 2, py - 7), label, font=sans(12, True), fill=WHITE)


def main():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    paper_texture(d)

    # --- top line + postage stamp ---
    d.text((M, 24), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=sans(19, True), fill=TERRA)
    sx, sy, sw, sh = W - M - 268, 16, 268, 34
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=4,
                        fill=CREAM, outline=TERRA, width=2)
    for px in range(sx + 6, sx + sw - 4, 10):
        d.point((px, sy + 2), fill=TERRA)
        d.point((px, sy + sh - 3), fill=TERRA)
    stamp = "48 STORIES · FRIDAY 20 NOV 2026"
    tw = d.textlength(stamp, font=sans(13, True))
    d.text((sx + (sw - tw) / 2, sy + 9), stamp, font=sans(13, True), fill=TERRA)
    d.line([(M, 58), (W - M, 58)], fill=BROWN, width=2)

    # --- masthead ---
    title = "Friday 20 November 2026"
    tf = serif(102, True)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 70), title, font=tf, fill=INK)
    sub = ("Akvan comes ashore · A missile over Riyadh · Trump puts the Iran "
           "decision off to 2027 · The world answers the genocide verdict")
    sf = serif(25, italic=True)
    tw = d.textlength(sub, font=sf)
    d.text(((W - tw) / 2, 196), sub, font=sf, fill=TERRA)

    # --- timeline strip ---
    ty = 232
    d.rectangle([M, ty, W - M, ty + 56], fill=BROWN_D)
    text_block(d, M + 16, ty + 6, TIMELINE, sans(17), CW - 32, 22,
               (245, 238, 225), max_lines=2)

    # --- region strip ---
    ry = 296
    total = sum(n for _, n, _ in REGIONS)
    rx = M
    for name, n, col in REGIONS:
        seg = int(CW * n / total)
        d.rectangle([rx, ry, rx + seg - 2, ry + 32], fill=col)
        label = f"{name} {n}"
        tw = d.textlength(label, font=sans(12, True))
        d.text((rx + (seg - tw) / 2, ry + 9), label, font=sans(12, True), fill=WHITE)
        rx += seg

    # --- heroes ---
    hy = 342
    hw = (CW - 24) // 3
    for i, (kicker, head, dek, source, idx) in enumerate(HEROES):
        hero_panel(d, M + i * (hw + 12), hy, hw, kicker, head, dek, source, idx)

    # --- pictured rows 5 / 4 / 4 ---
    rows = [PICTURED[0:5], PICTURED[5:9], PICTURED[9:13]]
    py = 676
    for row in rows:
        gap = 10
        pw = (CW - gap * (len(row) - 1)) // len(row)
        for i, (kicker, head, dek, source, idx) in enumerate(row):
            pictured_panel(d, M + i * (pw + gap), py, pw, kicker, head, dek, source, idx)
        py += 188

    # --- bottom: map + briefs ---
    by = py + 6
    d.text((M, by), "WHERE IT HAPPENED", font=sans(20, True), fill=TERRA)
    bx = M + 600
    d.text((bx, by), "ALSO ON FRIDAY 20 NOVEMBER — 32 MORE STORIES",
           font=sans(20, True), fill=TERRA)
    my = by + 30
    draw_map(d, M, my, 560, 186)
    bf = sans(13)
    col_w = 440
    for col_i in range(2):
        cx = bx + col_i * (col_w + 16)
        for j in range(16):
            num, place, text = BRIEFS[col_i * 16 + j]
            line = f"● {num} {place} — {text}"
            line = ellipsize(d, line, bf, col_w)
            d.text((cx, my + j * 12), line, font=bf, fill=INK)

    # --- date check ---
    dy = my + 196
    d.rectangle([M, dy, W - M, dy + 66], fill=CREAM, outline=TERRA, width=2)
    d.rectangle([M, dy, M + 158, dy + 66], fill=TERRA)
    d.text((M + 14, dy + 20), "DATE CHECK", font=sans(19, True), fill=WHITE)
    dc = ("Left out — they broke before Friday: the ICJ genocide ruling on Myanmar "
          "itself (Thursday 19 Nov) — Friday's news is the world's answer to it — "
          "Denmark's Greenland-US pact (19 Nov) — Anthropic's $81.34bn IPO (19 Nov); "
          "its first trading day was Thursday — Germany's electricity-tax cut "
          "(18 Nov) — the Crimean Bridge span collapse (17-18 Nov). Not yet: the "
          "trilateral's first meeting was 19 Nov; the joint declaration is Friday's.")
    text_block(d, M + 172, dy + 7, dc, sans(15), CW - 186, 19, INK, max_lines=3)

    # --- footer ---
    fy = dy + 78
    d.text((M, fy), "Every story here happened, or was first reported, on Friday 20 "
                    "November 2026, in some time zone. Disputed claims are attributed, "
                    "not stated as fact.",
           font=serif(15, italic=True), fill=(90, 78, 64))
    d.text((M, fy + 20), "Sources: Reuters · AP · AFP · BBC · Bloomberg · IMD · NASA · "
                         "IAEA · The Hindu · Arab News · Sensor Tower. Original drawings, "
                         "drawn for this page.",
           font=serif(15, italic=True), fill=(90, 78, 64))

    out = im.resize((1024, 1024), Image.LANCZOS)
    candidates = []
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if output_dir:
        candidates.append(output_dir)
    candidates.append(".")
    candidates.append(os.path.dirname(os.path.abspath(__file__)))
    last_error = None
    saved_path = None
    for candidate in candidates:
        try:
            saved_path = os.path.join(candidate, "entry.png")
            out.save(saved_path)
            break
        except OSError as exc:
            last_error = exc
            saved_path = None
    if saved_path is None:
        raise last_error
    print(f"saved {saved_path} 1024x1024")


if __name__ == "__main__":
    main()
