#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golemancer - Gerador procedural de arte para Thea 2: The Shattering.
Estilo Dark Fantasy.
"""

import math
import random
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_ROOT = os.path.join(ROOT, "Images", "Interface")

FONT_SERIF = r"C:\Windows\Fonts\georgia.ttf"
FONT_SERIF_B = r"C:\Windows\Fonts\georgiab.ttf"
FONT_ROMAN_B = r"C:\Windows\Fonts\constanb.ttf"

C_BG_DARK   = (18, 16, 20)
C_STONE     = (110, 105, 100)
C_IRON      = (140, 145, 150)
C_AMBER     = (210, 160, 60)
C_BONE      = (220, 215, 205)
C_DARK_BLUE = (35, 30, 45)
C_RED_DARK  = (100, 20, 25)
C_GREEN_D   = (40, 60, 40)
C_PURPLE_D  = (60, 30, 70)
C_GOLD      = (190, 160, 80)

def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v

def lerp(a, b, t):
    return a + (b - a) * t

def smooth(t):
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)

def hexc(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def mix(c1, c2, t):
    t = clamp(t)
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(3))

def rgba(c, a=255):
    if len(c) == 4:
        return c
    return (c[0], c[1], c[2], int(a))

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def vignette(size, power=2.2, strength=0.85, inset=0.15):
    w, h = size
    cx, cy = w * 0.5, h * 0.5
    rx, ry = w * (0.5 + inset), h * (0.5 + inset)
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    for y in range(h):
        dy = (y - cy) / ry
        for x in range(w):
            dx = (x - cx) / rx
            d = math.sqrt(dx * dx + dy * dy)
            v = clamp((d - 0.35) / 0.85)
            px[x, y] = int(255 * (v ** power) * strength)
    return mask.convert("RGBA")

def dust(size, seed, count=180, color=(220, 215, 200), rmax=2.2, alpha=120):
    rnd = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, w)
        y = rnd.uniform(0, h)
        r = rnd.uniform(0.4, rmax)
        a = int(rnd.uniform(0.25, 1.0) * alpha)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(color, a))
    return layer.filter(ImageFilter.GaussianBlur(0.6))

def scratches(size, seed, count=45, color=(240, 236, 226), alpha=55):
    rnd = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, w)
        y = rnd.uniform(0, h)
        ang = rnd.uniform(-0.6, 0.6)
        ln = rnd.uniform(4, 26)
        d.line(
            [x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln],
            fill=rgba(color, int(rnd.uniform(0.15, 1.0) * alpha)),
            width=1,
        )
    return layer.filter(ImageFilter.GaussianBlur(0.35))

def crack_pattern(size, seed, lines=12, color=(30, 28, 26), alpha=110, width=2):
    w, h = size
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(lines):
        x = rnd.uniform(0, w)
        y = rnd.uniform(0, h)
        pts = [(x, y)]
        ang = rnd.uniform(0, math.pi * 2)
        for _ in range(rnd.randint(4, 12)):
            ang += rnd.uniform(-0.8, 0.8)
            step = rnd.uniform(6, 34)
            x += math.cos(ang) * step
            y += math.sin(ang) * step
            pts.append((x, y))
        d.line(pts, fill=rgba(color, alpha), width=width)
    return layer.filter(ImageFilter.GaussianBlur(0.8))

def grain(size, seed, amount=14):
    w, h = size
    rnd = random.Random(seed)
    noise = Image.new("L", (w, h))
    noise.putdata([rnd.randint(0, 255) for _ in range(w * h)])
    dark = Image.new("RGBA", (w, h), (10, 9, 8, 255))
    light = Image.new("RGBA", (w, h), (250, 248, 242, 255))
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    over = Image.composite(light, base, noise.point(lambda v: 255 if v > 170 else 0))
    under = Image.composite(dark, base, noise.point(lambda v: int(amount * 1.6) if v < 85 else 0))
    return Image.alpha_composite(under, over)

def radial_glow(size, center, radius, color, strength=1.0):
    w, h = size
    cx, cy = center
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    r = max(1.0, radius)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * clamp(strength)))
    mask = mask.filter(ImageFilter.GaussianBlur(r * 0.55))
    layer = Image.new("RGBA", (w, h), rgba(color, 0))
    layer.putalpha(mask)
    return layer

def save_img(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    print("  OK " + os.path.basename(path) + " " + str(im.size) + " " + im.mode)

def make_card(name, subtitle, tier, color_accent, seed):
    """Card de personagem/golem 1024x1536"""
    w, h = 1024, 1536
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), C_BG_DARK)
    d = ImageDraw.Draw(im)

    # Fundo texturizado com gradiente escuro
    for y in range(h):
        t = y / h
        c = mix(C_BG_DARK, C_DARK_BLUE, t * 0.3)
        for x in range(w):
            d.point((x, y), fill=c)

    # Vinheta
    im = Image.alpha_composite(im, vignette((w, h), power=2.5, strength=0.9))

    # Borda decorativa (frame de pedra/ferro)
    border_w = 14
    d.rectangle([0, 0, w-1, border_w], fill=C_STONE)
    d.rectangle([0, h-border_w, w-1, h-1], fill=C_STONE)
    d.rectangle([0, 0, border_w, h-1], fill=C_STONE)
    d.rectangle([w-border_w, 0, w-1, h-1], fill=C_STONE)

    # Cantos decorativos
    corner_size = 60
    for cx, cy in [(corner_size, corner_size), (w-corner_size, corner_size),
                   (corner_size, h-corner_size), (w-corner_size, h-corner_size)]:
        d.ellipse([cx-corner_size//2, cy-corner_size//2, cx+corner_size//2, cy+corner_size//2],
                  outline=color_accent, width=4)

    # Silhueta do busto (centro inferior)
    bust_w = int(w * 0.45)
    bust_h = int(h * 0.55)
    bust_x = (w - bust_w) // 2
    bust_y = int(h * 0.35)

    # Base do busto (forma de ombro/peito)
    d.ellipse([bust_x, bust_y, bust_x + bust_w, bust_y + bust_h], fill=C_STONE)

    # Cabeça (círculo acima do busto)
    head_r = int(bust_w * 0.32)
    head_x = bust_x + bust_w // 2
    head_y = bust_y - int(bust_h * 0.15)
    d.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=C_BONE)

    # Cabelo/barba (sombra sobre a cabeça)
    hair_r = int(head_r * 1.1)
    d.ellipse([head_x - hair_r, head_y - int(head_r * 0.3), head_x + hair_r, head_y + head_r], fill=(40, 35, 30))

    # Olhos (pontos âmbar)
    eye_r = max(2, head_r // 12)
    d.ellipse([head_x - head_r//3 - eye_r, head_y - eye_r, head_x - head_r//3 + eye_r, head_y + eye_r], fill=color_accent)
    d.ellipse([head_x + head_r//3 - eye_r, head_y - eye_r, head_x + head_r//3 + eye_r, head_y + eye_r], fill=color_accent)

    # Luz dramática vindo do lado esquerdo
    glow = radial_glow((w, h), (head_x, head_y), head_r * 2, color_accent, 0.4)
    im = Image.alpha_composite(im, glow)

    # Texto: Nome
    fnt_name = font(FONT_SERIF_B, 64)
    fnt_sub = font(FONT_SERIF, 36)
    fnt_tier = font(FONT_SERIF, 28)

    # Nome na parte inferior
    name_w = d.textlength(str(name), font=fnt_name)
    d.text((w - name_w - 40, h - 140), name, font=fnt_name, fill=C_BONE)

    # Subtitulo
    sub_w = d.textlength(str(subtitle), font=fnt_sub)
    d.text((w - sub_w - 40, h - 90), subtitle, font=fnt_sub, fill=color_accent)

    # Tier
    tier_w = d.textlength(str(tier), font=fnt_tier)
    d.text((w - tier_w - 40, h - 50), str(tier), font=fnt_tier, fill=C_GOLD)

    # Poeira e granulacao
    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=200, alpha=100))
    im = Image.alpha_composite(im, grain((w, h), seed + 2000, amount=12))
    im = Image.alpha_composite(im, scratches((w, h), seed + 3000, count=30, alpha=40))

    return im.convert("RGB")


def make_roster(name, tier, color_accent, seed):
    """Roster 256x256 RGBA com fundo transparente, foco no rosto"""
    w, h = 256, 256
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = w // 2, int(h * 0.38)
    head_r = int(w * 0.22)

    # Sombra suave apenas atras da cabeca
    shadow = radial_glow((w, h), (cx, cy - 5), head_r * 0.9, (0, 0, 0), 0.25)
    im = Image.alpha_composite(im, shadow)

    # Cabeca (osso/pedra) - so a cabeca, ocupa parte superior
    d.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=C_BONE)

    # Cabelo/capuz (parte superior da cabeca)
    d.pieslice([cx - int(head_r*1.0), cy - int(head_r*1.0), cx + int(head_r*1.0), cy + int(head_r*0.1)],
               start=180, end=360, fill=(35, 30, 28, 255))

    # Olhos (acento)
    eye_r = max(2, head_r // 14)
    d.ellipse([cx - head_r//3 - eye_r, cy - head_r//6 - eye_r, cx - head_r//3 + eye_r, cy - head_r//6 + eye_r], fill=color_accent)
    d.ellipse([cx + head_r//3 - eye_r, cy - head_r//6 - eye_r, cx + head_r//3 + eye_r, cy - head_r//6 + eye_r], fill=color_accent)

    # Nariz
    d.polygon([(cx, cy + eye_r), (cx - eye_r//2, cy + eye_r*2), (cx + eye_r//2, cy + eye_r*2)], fill=C_STONE)

    # Busto pequeno (ombros) abaixo da cabeca
    bust_w = int(w * 0.35)
    bust_h = int(h * 0.18)
    d.ellipse([cx - bust_w//2, cy + int(head_r*0.45), cx + bust_w//2, cy + int(head_r*0.45) + bust_h], fill=C_STONE)

    # Colar/gargantilha
    d.arc([cx - head_r//2, cy + int(head_r*0.4), cx + head_r//2, cy + int(head_r*0.7)],
          start=180, end=360, fill=color_accent, width=3)

    # Luz direcional no rosto
    face_glow = radial_glow((w, h), (cx - int(head_r*0.15), cy - int(head_r*0.15)), head_r * 0.45, color_accent, 0.35)
    im = Image.alpha_composite(im, face_glow)

    # Poeira leve apenas onde tem conteudo
    dust_layer = dust((w, h), seed + 1000, count=30, alpha=50)
    content_mask = Image.new("L", (w, h), 0)
    cm = ImageDraw.Draw(content_mask)
    cm.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=255)
    cm.ellipse([cx - bust_w//2, cy + int(head_r*0.45), cx + bust_w//2, cy + int(head_r*0.45) + bust_h], fill=255)
    dust_layer.putalpha(content_mask)
    im = Image.alpha_composite(im, dust_layer)

    return im


def make_class_icon(name, color_accent, seed):
    """Icone de classe 256x256"""
    w, h = 256, 256
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = w // 2, h // 2
    r = int(w * 0.38)

    # Fundo circular de pedra
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=C_STONE)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], fill=(60, 55, 50))

    # Simbolo de martelo + bigorna (forja)
    # Martelo (diagonal)
    d.line([cx - int(r*0.35), cy + int(r*0.35), cx + int(r*0.35), cy - int(r*0.35)],
           fill=color_accent, width=8)
    # Cabeca do martelo
    d.rectangle([cx + int(r*0.25), cy - int(r*0.42), cx + int(r*0.42), cy - int(r*0.28)], fill=C_IRON)
    # Bigorna (base)
    d.rectangle([cx - int(r*0.3), cy + int(r*0.2), cx + int(r*0.3), cy + int(r*0.4)], fill=C_IRON)

    # Borda externa
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color_accent, width=6)

    # Poeira
    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=50, alpha=70))

    return im

def make_skill_icon(name, color_accent, seed):
    """Icone de habilidade 256x256"""
    w, h = 256, 256
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = w // 2, h // 2
    r = int(w * 0.4)

    # Fundo escuro circular
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 26, 24, 255))

    # Simbolo generico de magia/forja (runas)
    # Circulo interno
    d.ellipse([cx - int(r*0.5), cy - int(r*0.5), cx + int(r*0.5), cy + int(r*0.5)],
              outline=color_accent, width=4)

    # Simbolo central (triangulo + linha)
    d.polygon([(cx, cy - int(r*0.3)), (cx - int(r*0.25), cy + int(r*0.3)),
               (cx + int(r*0.25), cy + int(r*0.3))], fill=color_accent)
    d.line([cx, cy - int(r*0.3), cx, cy + int(r*0.3)], fill=C_BONE, width=3)

    # Borda externa
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C_IRON, width=3)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=50, alpha=70))

    return im

def make_item_icon(name, color_accent, seed):
    """Icone de item 256x256"""
    w, h = 256, 256
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = w // 2, h // 2

    # Fundo de item (quadrado com cantos arredondados simulado)
    item_r = int(w * 0.35)
    d.rounded_rectangle([cx - item_r, cy - item_r, cx + item_r, cy + item_r], radius=20,
                        fill=C_STONE, outline=color_accent, width=4)

    # Simbolo interno baseado no nome (simplificado)
    if "LAMINA" in name or "MARTELO" in name:
        # Arma
        d.rectangle([cx - 8, cy - int(item_r*0.5), cx + 8, cy], fill=C_IRON)
        d.rectangle([cx - 14, cy - 4, cx + 14, cy + 4], fill=C_BONE)
    elif "MALHA" in name or "ESCUDO" in name:
        # Armadura/Escudo
        d.rectangle([cx - int(item_r*0.4), cy - int(item_r*0.4), cx + int(item_r*0.4), cy + int(item_r*0.4)],
                    fill=C_IRON, outline=C_BONE, width=2)
    elif "PINGENTE" in name or "ALVO" in name:
        # Joia
        d.ellipse([cx - int(item_r*0.35), cy - int(item_r*0.35), cx + int(item_r*0.35), cy + int(item_r*0.35)],
                  fill=color_accent, outline=C_GOLD, width=3)
        d.line([cx - int(item_r*0.2), cy, cx + int(item_r*0.2), cy], fill=C_GOLD, width=2)
        d.line([cx, cy - int(item_r*0.2), cx, cy + int(item_r*0.2)], fill=C_GOLD, width=2)
    elif "PAO" in name or "ERVA" in name:
        # Comida/Erva
        d.ellipse([cx - int(item_r*0.4), cy - int(item_r*0.4), cx + int(item_r*0.4), cy + int(item_r*0.4)],
                  fill=C_GREEN_D, outline=color_accent, width=3)
        d.ellipse([cx - int(item_r*0.15), cy - int(item_r*0.4), cx + int(item_r*0.15), cy - int(item_r*0.25)],
                  fill=(20, 40, 20))
    else:
        # Generico
        d.ellipse([cx - int(item_r*0.4), cy - int(item_r*0.4), cx + int(item_r*0.4), cy + int(item_r*0.4)],
                  fill=C_BONE, outline=color_accent, width=3)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=50, alpha=70))

    return im


def make_event_vertical(title, subtitle, color_accent, seed):
    """Evento vertical 700x1000"""
    w, h = 700, 1000
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), C_BG_DARK)
    d = ImageDraw.Draw(im)

    # Gradiente de fundo
    for y in range(h):
        t = y / h
        c = mix(C_BG_DARK, C_PURPLE_D, t * 0.4)
        for x in range(w):
            d.point((x, y), fill=c)

    # Vinheta forte
    im = Image.alpha_composite(im, vignette((w, h), power=2.0, strength=0.9, inset=0.2))

    # Cena abstrata: forja com brasas
    cx, cy = w // 2, h // 2

    # Bigorna (base)
    anvil_w = int(w * 0.35)
    anvil_h = int(h * 0.15)
    d.rectangle([cx - anvil_w//2, cy - anvil_h//2, cx + anvil_w//2, cy + anvil_h//2], fill=C_IRON)
    d.rectangle([cx - anvil_w//2 + 10, cy - anvil_h//2 + 10, cx + anvil_w//2 - 10, cy + anvil_h//2 - 10], fill=(70, 65, 60))

    # Martelo (diagonal sobre a bigorna)
    d.line([cx - int(w*0.2), cy + int(h*0.15), cx + int(w*0.2), cy - int(h*0.15)],
           fill=color_accent, width=10)

    # Faíscas/brasas ao redor
    for _ in range(30):
        sx = rnd.uniform(0, w)
        sy = rnd.uniform(0, h)
        sr = rnd.uniform(2, 8)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=C_AMBER)

    # Luz de forge
    forge_glow = radial_glow((w, h), (cx, cy - int(h*0.1)), int(w*0.4), C_AMBER, 0.5)
    im = Image.alpha_composite(im, forge_glow)

    # Texto
    fnt_title = font(FONT_SERIF_B, 42)
    fnt_sub = font(FONT_SERIF, 24)

    # Título em banner
    banner_h = 80
    banner_y = h - banner_h - 40
    d.rectangle([30, banner_y, w - 30, banner_y + banner_h], fill=(30, 26, 24, 230))
    d.rectangle([30, banner_y, w - 30, banner_y + banner_h], outline=color_accent, width=2)

    title_w = d.textlength(title, font=fnt_title)
    d.text(((w - title_w) // 2, banner_y + banner_h // 2), title, font=fnt_title, fill=C_BONE, anchor="mm")

    sub_w = d.textlength(str(subtitle), font=fnt_sub)
    d.text((w - sub_w - 30, h - 30), subtitle, font=fnt_sub, fill=color_accent)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=100, alpha=90))
    im = Image.alpha_composite(im, grain((w, h), seed + 2000, amount=10))

    return im.convert("RGB")

def make_event_wide(title, subtitle, color_accent, seed):
    """Evento horizontal 1280x720"""
    w, h = 1280, 720
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), C_BG_DARK)
    d = ImageDraw.Draw(im)

    # Gradiente horizontal escuro
    for x in range(w):
        t = x / w
        c = mix(C_BG_DARK, C_DARK_BLUE, t * 0.3)
        for y in range(h):
            d.point((x, y), fill=c)

    im = Image.alpha_composite(im, vignette((w, h), power=1.5, strength=0.7, inset=0.15))

    # Cena: grupo de golens em torno de uma forja
    cx, cy = w // 2, h // 2

    # Fogueira central
    fire_r = int(h * 0.15)
    d.ellipse([cx - fire_r, cy - fire_r, cx + fire_r, cy + fire_r], fill=C_RED_DARK)
    d.ellipse([cx - fire_r//2, cy - fire_r//2, cx + fire_r//2, cy + fire_r//2], fill=C_AMBER)

    # Silhuetas de golens ao redor (formas simples)
    positions = [
        (cx - int(w*0.3), cy), (cx + int(w*0.3), cy),
        (cx - int(w*0.15), cy - int(h*0.2)), (cx + int(w*0.15), cy - int(h*0.2)),
        (cx - int(w*0.15), cy + int(h*0.2)), (cx + int(w*0.15), cy + int(h*0.2)),
    ]
    for px, py in positions:
        gr = int(w * 0.08)
        d.ellipse([px - gr, py - gr, px + gr, py + gr], fill=C_STONE)
        d.ellipse([px - int(gr*0.6), py - int(gr*0.8), px + int(gr*0.6), py - int(gr*0.2)], fill=C_BONE)

    # Luz da fogueira
    fire_glow = radial_glow((w, h), (cx, cy), int(w*0.5), C_AMBER, 0.4)
    im = Image.alpha_composite(im, fire_glow)

    # Texto em banner inferior
    fnt_title = font(FONT_SERIF_B, 48)
    fnt_sub = font(FONT_SERIF, 26)

    banner_h = 100
    banner_y = h - banner_h - 30
    d.rectangle([40, banner_y, w - 40, banner_y + banner_h], fill=(30, 26, 24, 220))
    d.rectangle([40, banner_y, w - 40, banner_y + banner_h], outline=color_accent, width=2)

    title_w = d.textlength(title, font=fnt_title)
    d.text(((w - title_w) // 2, banner_y + banner_h // 2), title, font=fnt_title, fill=C_BONE, anchor="mm")

    sub_w = d.textlength(str(subtitle), font=fnt_sub)
    d.text((w - sub_w - 40, h - 25), subtitle, font=fnt_sub, fill=color_accent)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=80, alpha=80))
    im = Image.alpha_composite(im, grain((w, h), seed + 2000, amount=10))

    return im.convert("RGB")

def make_scene(title, subtitle, color_accent, seed):
    """Cena de interacao 1536x1024"""
    w, h = 1536, 1024
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), C_BG_DARK)
    d = ImageDraw.Draw(im)

    # Gradiente de cena (ceu escuro + chao)
    horizon = int(h * 0.6)
    for y in range(h):
        if y < horizon:
            t = y / horizon
            c = mix(C_DARK_BLUE, C_BG_DARK, t * 0.5)
        else:
            t = (y - horizon) / (h - horizon)
            c = mix(C_BG_DARK, (10, 8, 10), t * 0.5)
        for x in range(w):
            d.point((x, y), fill=c)

    im = Image.alpha_composite(im, vignette((w, h), power=1.8, strength=0.75))

    # Cena: Yuri ensinando aprendizes na forja
    cx, cy = w // 2, int(h * 0.55)

    # Forja (estrutura de pedra e metal)
    forge_w = int(w * 0.4)
    forge_h = int(h * 0.3)
    d.rectangle([cx - forge_w//2, cy - forge_h//2, cx + forge_w//2, cy + forge_h//2], fill=C_STONE)
    d.rectangle([cx - forge_w//2 + 15, cy - forge_h//2 + 15, cx + forge_w//2 - 15, cy + forge_h//2 - 15], fill=(50, 45, 40))

    # Fogo na forja
    fire_r = int(w * 0.06)
    d.ellipse([cx - fire_r, cy - fire_r, cx + fire_r, cy + fire_r], fill=C_RED_DARK)
    d.ellipse([cx - fire_r//2, cy - fire_r//2, cx + fire_r//2, cy + fire_r//2], fill=C_AMBER)

    # Silhuetas de personagens (Yuri + 3 aprendizes)
    char_positions = [
        (cx - int(w*0.18), cy + int(h*0.05)),  # Yuri (centro-esquerda)
        (cx + int(w*0.18), cy + int(h*0.05)),  # Aprendiz 1
        (cx - int(w*0.05), cy - int(h*0.08)),  # Aprendiz 2
    ]
    for px, py in char_positions:
        hr = int(w * 0.045)
        d.ellipse([px - hr, py - hr, px + hr, py + hr], fill=C_BONE)
        d.ellipse([px - int(hr*0.7), py - int(hr*0.9), px + int(hr*0.7), py - int(hr*0.3)], fill=(35, 30, 28))
        # Corpo
        d.rectangle([px - int(hr*0.5), py + hr, px + int(hr*0.5), py + int(hr*1.8)], fill=C_STONE)

    # Luz da forja nos personagens
    forge_glow = radial_glow((w, h), (cx, cy), int(w*0.4), C_AMBER, 0.35)
    im = Image.alpha_composite(im, forge_glow)

    # Texto em banner inferior
    fnt_title = font(FONT_SERIF_B, 52)
    fnt_sub = font(FONT_SERIF, 30)

    banner_h = 120
    banner_y = h - banner_h - 30
    d.rectangle([50, banner_y, w - 50, banner_y + banner_h], fill=(30, 26, 24, 210))
    d.rectangle([50, banner_y, w - 50, banner_y + banner_h], outline=color_accent, width=2)

    title_w = d.textlength(title, font=fnt_title)
    d.text(((w - title_w) // 2, banner_y + banner_h // 2), title, font=fnt_title, fill=C_BONE, anchor="mm")

    sub_w = d.textlength(str(subtitle), font=fnt_sub)
    d.text((w - sub_w - 50, h - 30), subtitle, font=fnt_sub, fill=color_accent)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=120, alpha=90))
    im = Image.alpha_composite(im, grain((w, h), seed + 2000, amount=10))

    return im.convert("RGB")


def make_hud(name, color_accent, seed):
    """Elemento HUD 9-slice RGBA transparente"""
    w, h = 256, 256
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    corner = 32
    # Painel principal (borda de pedra com canto transparente no meio)
    d.rectangle([0, 0, w, corner], fill=C_STONE)  # topo
    d.rectangle([0, h-corner, w, h], fill=C_STONE)  # baixo
    d.rectangle([0, 0, corner, h], fill=C_STONE)  # esquerda
    d.rectangle([w-corner, 0, w, h], fill=C_STONE)  # direita

    # Cantos decorativos
    d.line([0, corner, corner, 0], fill=color_accent, width=6)
    d.line([w-1, corner, w-1-corner, 0], fill=color_accent, width=6)
    d.line([0, h-1-corner, corner, h-1], fill=color_accent, width=6)
    d.line([w-1, h-1-corner, w-1-corner, h-1], fill=color_accent, width=6)

    # Poeira leve
    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=30, alpha=60))

    return im

def make_hud_bar(name, color_accent, seed):
    """Barra de status HUD 128x16"""
    w, h = 128, 16
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Fundo da barra
    d.rectangle([0, 0, w, h], fill=(40, 35, 30, 200))
    d.rectangle([0, 0, w, h], outline=C_IRON, width=2)

    # Preenchimento (acento)
    fill_w = int(w * 0.7)
    d.rectangle([2, 2, fill_w, h-2], fill=color_accent)

    # Borda de brilho
    d.line([2, 2, fill_w, 2], fill=C_GOLD, width=1)

    return im

def make_hud_slot(name, color_accent, seed):
    """Slot de item HUD 64x64"""
    w, h = 64, 64
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Slot vazio
    d.rectangle([0, 0, w, h], fill=(30, 26, 24, 180))
    d.rectangle([0, 0, w, h], outline=C_STONE, width=2)

    # Brilho nas bordas
    d.line([0, 0, w-1, 0], fill=C_IRON, width=1)
    d.line([0, 0, 0, h-1], fill=C_IRON, width=1)
    d.line([0, h-1, w-1, h-1], fill=(60, 55, 50), width=1)
    d.line([w-1, 0, w-1, h-1], fill=(60, 55, 50), width=1)

    return im

def make_hud_portrait_frame(name, color_accent, seed):
    """Moldura de retrato octogonal 160x160 com furo central"""
    w, h = 160, 160
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx, cy = w // 2, h // 2
    r_outer = int(w * 0.45)
    r_inner = int(w * 0.38)

    # Moldura octogonal aproximada (elipse grossa)
    d.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=C_STONE, outline=color_accent, width=6)
    d.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(0, 0, 0, 0))  # furo central transparente

    # Cantos decorativos (octogonal)
    for ang in range(0, 360, 45):
        import math as m
        x1 = cx + int(m.cos(m.radians(ang)) * r_outer)
        y1 = cy + int(m.sin(m.radians(ang)) * r_outer)
        x2 = cx + int(m.cos(m.radians(ang)) * (r_outer - 10))
        y2 = cy + int(m.sin(m.radians(ang)) * (r_outer - 10))
        d.line([x1, y1, x2, y2], fill=color_accent, width=4)

    im = Image.alpha_composite(im, dust((w, h), seed + 1000, count=30, alpha=60))

    return im


# Definicoes de todas as imagens a gerar
# (nome_arquivo, tipo, params)

CARD_DEFS = [
    # (nome, subtitulo, tier, cor_acento, seed)
    ("YURI_Yuri_Card", "Yuri Mizuki", "Golemancer - Criador de Golens", C_AMBER, 1001),
    ("GOLEM_CHOQUE_Card", "Choque", "Golem Inferior - Pedra e Argila", C_STONE, 1002),
    ("GOLEM_CASCALHO_Card", "Cascalho", "Golem Inferior - Pedra e Osso", C_IRON, 1003),
    ("GOLEM_GALHO_Card", "Galho", "Golem Inferior - Madeira", C_GREEN_D, 1004),
    ("GOLEM_LAMPEJO_Card", "Lamp-Ambar", "Golem Inferior - Ambar e Quartzo", C_AMBER, 1005),
    ("GOLEM_MASSA_Card", "Massa-Mae", "Golem Inferior - Graos e Nozes", C_GOLD, 1006),
    ("GOLEM_SEIXO_Card", "Seixo", "Golem Inferior - Pedra Pura", C_STONE, 1007),
    ("GOLEM_FERRO_VIDO_Card", "Ferro-Vivo", "Golem Feitor - Ferro e Pedra", C_IRON, 1008),
    ("GOLEM_RAIZ_Card", "Raiz", "Golem Feitor - Madeira de Driade", C_GREEN_D, 1009),
    ("GOLEM_OSSADA_Card", "Ossada", "Golem Feitor - Ossos e Argila", C_BONE, 1010),
    ("GOLEM_CRISTAL_Card", "Cristal", "Golem Feitor - Quartzo e Ambar", C_PURPLE_D, 1011),
    ("GOLEM_PAO_DO_CAMPO_Card", "Pao-do-Campo", "Golem Feitor - Comida Cozida", C_GOLD, 1012),
    ("GOLEM_MURALHA_Card", "Muralha", "Golem Superior - Granito e Pedra Armada", C_STONE, 1013),
    ("GOLEM_VIUVA_Card", "Viuva-de-Cedro", "Golem Superior - Madeira Sagrada", C_PURPLE_D, 1014),
    ("GOLEM_VEJO_Card", "Vejo", "Golem Superior - Gema e Diamante", C_AMBER, 1015),
    ("GOLEM_AGULHA_Card", "Agulha", "Golem Superior - Ervas e Cogumelos", C_GREEN_D, 1016),
    ("GOLEM_FERREIRO_Card", "Ferreiro", "Golem Superior - Ferro e Acou", C_IRON, 1017),
    ("GOLEM_GUARDAO_DA_MINA_Card", "Guardiao da Mina", "Golem Unico - Pedra e Essencia", C_STONE, 1018),
    ("GOLEM_DRAGAO_OSSO_Card", "Dragao de Osso", "Golem Unico - Ossos de Dragao", C_BONE, 1019),
    ("GOLEM_CEVA_Card", "Ceva", "Golem Unico - Ervas e Essencia da Vida", C_GREEN_D, 1020),
    ("GOLEM_CINZEL_Card", "Cinzel", "Golem Unico - Aco e Mithril", C_IRON, 1021),
    ("YURI_HALF_ARGILA_Card", "Half-Argila", "Descendente - Int 5 Sab 4 Mis 2", C_GREEN_D, 1022),
    ("YURI_HALF_BRASA_Card", "Half-Brasa", "Descendente - Sab 4 Mis 2 Int 5", C_AMBER, 1023),
    ("GOLEM_OBSIDIANA_Card", "Obsidiana", "Golem de Obsidiana", C_RED_DARK, 1024),
    ("GOLEM_SANGUE_Card", "Sangue", "Golem de Sangue", C_RED_DARK, 1025),
    ("GOLEM_NEBULINA_Card", "Nebulina", "Golem de Nebulina", C_PURPLE_D, 1026),
    ("GOLEM_FUNGO_Card", "Fungo", "Golem de Fungo", C_GREEN_D, 1027),
    ("GOLEM_RELIQUIA_Card", "Relíquia", "Golem Relíquia", C_GOLD, 1028),

]

ROSTER_DEFS = [
    # (nome, tier, cor_acento, seed)
    ("YURI_Yuri_Roster", "Yuri Mizuki", C_AMBER, 2001),
    ("GOLEM_CHOQUE_Roster", "Choque", C_STONE, 2002),
    ("GOLEM_CASCALHO_Roster", "Cascalho", C_IRON, 2003),
    ("GOLEM_GALHO_Roster", "Galho", C_GREEN_D, 2004),
    ("GOLEM_LAMPEJO_Roster", "Lamp-Ambar", C_AMBER, 2005),
    ("GOLEM_MASSA_Roster", "Massa-Mae", C_GOLD, 2006),
    ("GOLEM_SEIXO_Roster", "Seixo", C_STONE, 2007),
    ("GOLEM_FERRO_VIDO_Roster", "Ferro-Vivo", C_IRON, 2008),
    ("GOLEM_RAIZ_Roster", "Raiz", C_GREEN_D, 2009),
    ("GOLEM_OSSADA_Roster", "Ossada", C_BONE, 2010),
    ("GOLEM_CRISTAL_Roster", "Cristal", C_PURPLE_D, 2011),
    ("GOLEM_PAO_DO_CAMPO_Roster", "Pao-do-Campo", C_GOLD, 2012),
    ("GOLEM_MURALHA_Roster", "Muralha", C_STONE, 2013),
    ("GOLEM_VIUVA_Roster", "Viuva-de-Cedro", C_PURPLE_D, 2014),
    ("GOLEM_VEJO_Roster", "Vejo", C_AMBER, 2015),
    ("GOLEM_AGULHA_Roster", "Agulha", C_GREEN_D, 2016),
    ("GOLEM_FERREIRO_Roster", "Ferreiro", C_IRON, 2017),
    ("GOLEM_GUARDAO_DA_MINA_Roster", "Guardiao da Mina", C_STONE, 2018),
    ("GOLEM_DRAGAO_OSSO_Roster", "Dragao de Osso", C_BONE, 2019),
    ("GOLEM_CEVA_Roster", "Ceva", C_GREEN_D, 2020),
    ("GOLEM_CINZEL_Roster", "Cinzel", C_IRON, 2021),
    ("YURI_HALF_ARGILA_Roster", "Half-Argila", C_GREEN_D, 2022),
    ("YURI_HALF_BRASA_Roster", "Half-Brasa", C_AMBER, 2023),
    ("GOLEM_OBSIDIANA_Roster", "Obsidiana", C_RED_DARK, 2024),
    ("GOLEM_SANGUE_Roster", "Sangue", C_RED_DARK, 2025),
    ("GOLEM_NEBULINA_Roster", "Nebulina", C_PURPLE_D, 2026),
    ("GOLEM_FUNGO_Roster", "Fungo", C_GREEN_D, 2027),
    ("GOLEM_RELIQUIA_Roster", "Relíquia", C_GOLD, 2028),
    ("HALF_OBSIDIANA_Roster", "Half-Obsidiana", C_RED_DARK, 2029),
    ("HALF_NEBULINA_Roster", "Half-Nebulina", C_PURPLE_D, 2030),

]

CLASS_DEFS = [
    ("YURI_Yuri_Classe", C_AMBER, 3001),
    ("HALF_ARGILA_Classe", C_GREEN_D, 3002),
    ("HALF_BRASA_Classe", C_AMBER, 3003),
    ("HALF_OBSIDIANA_Classe", C_RED_DARK, 3004),
    ("HALF_NEBULINA_Classe", C_PURPLE_D, 3005),

]

SKILL_DEFS = [
    ("SKILL_YURI_FORJA_VIVA", C_AMBER, 4001),
    ("SKILL_YURI_FORNAR", C_IRON, 4002),
    ("SKILL_YURI_BATISMO", C_PURPLE_D, 4003),
    ("SKILL_YURI_APRENDIZ", C_GOLD, 4004),
    ("SKILL_GOLEM_ESCUDO", C_STONE, 4005),
    ("SKILL_GOLEM_PUNHO", C_IRON, 4006),
    ("SKILL_GOLEM_ECO", C_PURPLE_D, 4007),
    ("SKILL_GOLEM_CURA", C_GREEN_D, 4008),
    ("SKILL_GOLEM_LUTO", C_PURPLE_D, 4009),
    ("SKILL_GOLEM_VAZIO", C_DARK_BLUE, 4010),
    ("SKILL_GOLEM_RAIZ", C_GREEN_D, 4011),
    ("SKILL_GOLEM_MURALHA", C_STONE, 4012),
    ("SKILL_GOLEM_FERREIRO", C_IRON, 4013),
    ("SKILL_GOLEM_ESTALO", C_RED_DARK, 4014),
    ("SKILL_GOLEM_ARGILA", C_GREEN_D, 4015),
    ("SKILL_GOLEM_BRASA", C_RED_DARK, 4016),
    ("SKILL_PERS_LEAL", C_GOLD, 4017),
    ("SKILL_PERS_AGRESSIVO", C_RED_DARK, 4018),
    ("SKILL_PERS_SERENO", C_GREEN_D, 4019),
    ("SKILL_PERS_VAIDOSO", C_AMBER, 4020),
    ("SKILL_YM_ITEM_ESPADA_RUNICA", C_RED_DARK, 4021),
    ("SKILL_YM_ITEM_AMULETO_FORJA", C_GOLD, 4022),
    ("SKILL_YM_ITEM_BOTAS_ARGILA", C_GREEN_D, 4023),
    ("SKILL_YM_SANIDADE_LOSS", C_PURPLE_D, 4024),
    ("SKILL_YM_SANIDADE_RECOVER", C_GREEN_D, 4025),

]

ITEM_DEFS = [
    ("ITEM_LAMINA_FORJA", C_IRON, 5001),
    ("ITEM_MARTELO_MESTRE", C_IRON, 5002),
    ("ITEM_MALHA_COTA", C_STONE, 5003),
    ("ITEM_ESCUDO_PEDRA", C_STONE, 5004),
    ("ITEM_ALVO_AMBER", C_AMBER, 5005),
    ("ITEM_PAO_VIVO", C_GOLD, 5006),
    ("ITEM_ERVA_FORJA", C_GREEN_D, 5007),
    ("ITEM_ARMADILHA_LAMBRI", C_STONE, 5008),
    ("ITEM_PINGENTE_NOME", C_GOLD, 5009),
    ("ITEM_ESPADA_RUNICA", C_RED_DARK, 5010),
    ("ITEM_AMULETO_FORJA", C_GOLD, 5011),
    ("ITEM_BOTAS_ARGILA", C_GREEN_D, 5012),

]

EVENT_VERTICAL_DEFS = [
    ("EV_A_OFICINA_NO_VALE", "A Oficina no Vale", "Yuri Mizuki o aguarda em sua forja no vale.", C_AMBER, 6001),
    ("EV_A_FORJA_VIVA", "A Forja Viva", "A oficina itinerante de Yuri esta acesa.", C_IRON, 6002),
    ("EV_SOPRO_DE_ARGILA", "O Sopro de Argila", "Dois golens unidos criam uma nova vida.", C_GREEN_D, 6003),
    ("EV_BATISMO", "Batismo de Golem", "Um golem recebe nome e alma pelo d100.", C_PURPLE_D, 6004),
    ("EV_FILHO_SEM_NOME", "O Filho que Nao Quer Nome", "Um golem foge do batismo e age por conta propria.", C_RED_DARK, 6005),
    ("EV_FERRAMENTA_ENGOLIU", "A Ferramenta que Engoliu o Ferreiro", "O golem Ferreiro troca de corpo com Yuri.", C_IRON, 6006),
    ("EV_PESO_DO_PAO", "O Peso do Pao", "O Pao-do-Campo faminto ameaca um aliado.", C_GOLD, 6007),
    ("EV_CEVA_CHORA", "A Ceva Chora", "Ceva chora um aliado morto na fogueira.", C_GREEN_D, 6008),
    ("EV_PEDIDO_DO_CINZEL", "O Pedido do Cinzel", "Cinzel exige um sacrifício de igual.", C_IRON, 6009),
]

EVENT_WIDE_DEFS = [
    ("EV_A_OFICINA_NO_VALE", "A Oficina no Vale", "Yuri Mizuki o aguarda em sua forja no vale.", C_AMBER, 7001),
    ("EV_A_FORJA_VIVA", "A Forja Viva", "A oficina itinerante de Yuri esta acesa.", C_IRON, 7002),
    ("EV_SOPRO_DE_ARGILA", "O Sopro de Argila", "Dois golens unidos criam uma nova vida.", C_GREEN_D, 7003),
    ("EV_BATISMO", "Batismo de Golem", "Um golem recebe nome e alma pelo d100.", C_PURPLE_D, 7004),
    ("EV_FILHO_SEM_NOME", "O Filho que Nao Quer Nome", "Um golem foge do batismo e age por conta propria.", C_RED_DARK, 7005),
    ("EV_FERRAMENTA_ENGOLIU", "A Ferramenta que Engoliu o Ferreiro", "O golem Ferreiro troca de corpo com Yuri.", C_IRON, 7006),
    ("EV_PESO_DO_PAO", "O Peso do Pao", "O Pao-do-Campo faminto ameaca um aliado.", C_GOLD, 7007),
    ("EV_CEVA_CHORA", "A Ceva Chora", "Ceva chora um aliado morto na fogueira.", C_GREEN_D, 7008),
    ("EV_PEDIDO_DO_CINZEL", "O Pedido do Cinzel", "Cinzel exige um sacrifício de igual.", C_IRON, 7009),
]

SCENE_DEFS = [
    ("SC_YURI_ENSINA", "Yuri Ensina", "O artífice transmite seus conhecimentos aos aprendizes da forja.", C_AMBER, 8001),
    ("SC_FORJA_GOLEM", "Forjando um Golem", "A criacao de um corpo de pedra ganha vida nas brasas.", C_IRON, 8002),
    ("SC_BATISMO_D100", "Momento do Batismo", "O d100 decide o destino de um golem T3.", C_PURPLE_D, 8003),
    ("SC_HALFS", "Os Halfs", "Descendentes de Yuri e seus golens caminham juntos.", C_GREEN_D, 8004),
]

HUD_DEFS = [
    ("HUD_PANEL_MAIN", C_STONE, 9001),
    ("HUD_SIGIL_PORTRAIT", C_AMBER, 9002),
    ("HUD_RIBBON_TITLE", C_GOLD, 9003),
]

HUD_BAR_DEFS = [
    ("YM_BAR_EMPTY", (60, 55, 50), 9101),
    ("YM_BAR_FILL", C_AMBER, 9102),
]

HUD_SLOT_DEFS = [
    ("YM_SLOT", C_STONE, 9201),
]

HUD_SEL_DEFS = [
    ("YM_SEL_BORDER", C_AMBER, 9301),
]


def main():
    print("=== GOLEMANCER - GERADOR DE ARTE PROCEDURAL ===")
    print("")

    # Cards 1024x1536
    print("\n[1/8] Gerando CARDS (1024x1536)...")
    for fname, nome, subtitulo, tier, seed in CARD_DEFS:
        im = make_card(nome, subtitulo, tier, C_AMBER if "YURI" in fname else (C_IRON if "FERREIRO" in fname or "CINZEL" in fname or "GUARDAO" in fname else C_STONE), seed)
        save_img(im, os.path.join(IMG_ROOT, "Cards", fname + ".png"))

    # Rosters 256x256 RGBA transparente
    print("\n[2/8] Gerando ROSTERS (256x256 RGBA)...")
    for fname, nome, color_accent, seed in ROSTER_DEFS:
        im = make_roster(nome, "", color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Roster", fname + ".png"))

    # Icones de classe 256x256
    print("\n[3/8] Gerando ICONES DE CLASSE (256x256)...")
    for fname, color_accent, seed in CLASS_DEFS:
        im = make_class_icon(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Classe", fname + ".png"))

    # Icones de habilidade 256x256
    print("\n[4/8] Gerando ICONES DE HABILIDADE (256x256)...")
    for fname, color_accent, seed in SKILL_DEFS:
        im = make_skill_icon(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Skills", fname + ".png"))

    # Icones de item 256x256
    print("\n[5/8] Gerando ICONES DE ITEM (256x256)...")
    for fname, color_accent, seed in ITEM_DEFS:
        im = make_item_icon(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Items", fname + ".png"))

    # Eventos verticais 700x1000
    print("\n[6/8] Gerando EVENTOS VERTICAIS (700x1000)...")
    for fname, title, subtitle, color_accent, seed in EVENT_VERTICAL_DEFS:
        im = make_event_vertical(title, subtitle, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Events", fname + "_Vertical.png"))

    # Eventos wide 1280x720
    print("\n[7/8] Gerando EVENTOS WIDE (1280x720)...")
    for fname, title, subtitle, color_accent, seed in EVENT_WIDE_DEFS:
        im = make_event_wide(title, subtitle, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Events", fname + "_Wide.png"))

    # Cenas 1536x1024
    print("\n[8/8] Gerando CENAS (1536x1024)...")
    for fname, title, subtitle, color_accent, seed in SCENE_DEFS:
        im = make_scene(title, subtitle, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "Scenes", fname + ".png"))

    # HUD
    print("\n[9/9] Gerando HUD...")
    for fname, color_accent, seed in HUD_DEFS:
        if fname == "HUD_PANEL_MAIN":
            im = make_hud(fname, color_accent, seed)
        elif fname == "HUD_SIGIL_PORTRAIT":
            im = make_hud_portrait_frame(fname, color_accent, seed)
        elif fname == "HUD_RIBBON_TITLE":
            im = make_hud_bar(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "HUD", fname + ".png"))

    for fname, color_accent, seed in HUD_BAR_DEFS:
        im = make_hud_bar(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "HUD", fname + ".png"))

    for fname, color_accent, seed in HUD_SLOT_DEFS:
        im = make_hud_slot(fname, color_accent, seed)
        save_img(im, os.path.join(IMG_ROOT, "HUD", fname + ".png"))

    for fname, color_accent, seed in HUD_SEL_DEFS:
        im = make_hud_slot(fname, color_accent, seed)  # reuse slot as border base
        save_img(im, os.path.join(IMG_ROOT, "HUD", fname + ".png"))

    print("\n=== ARTE GERADA COM SUCESSO ===")

if __name__ == "__main__":
    main()
