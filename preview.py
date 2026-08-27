#!/usr/bin/env python3
"""
preview.py - Gera uma imagem PNG de preview do layout Red vs Blue sem precisar renderizar vídeo
Útil para testar fontes e textos rapidamente
"""
from PIL import Image
import numpy as np
from make_quiz import create_background, create_wrapped_text_image, create_vs_circle_image, create_percent_image, create_round_label_image, W, H, HALF_H
import os

def generate_preview(option_a="Have unlimited money", option_b="Be able to teleport anywhere", percent_a="72%", percent_b="28%", output="preview.png"):
    bg = create_background()
    # Textos - GIGANTE para TikTok
    text_a_pil = create_wrapped_text_image(option_a.upper(), max_width_px=980, font_size=125, color=(255,255,255), stroke_width=14, stroke_color=(0,0,0), bold=True)
    text_b_pil = create_wrapped_text_image(option_b.upper(), max_width_px=980, font_size=125, color=(255,255,255), stroke_width=14, stroke_color=(0,0,0), bold=True)
    
    # Compor tudo em uma imagem PIL
    bg_copy = bg.copy()
    # Colar textos
    y_a = (HALF_H - text_a_pil.height)//2 - 40
    bg_copy.paste(text_a_pil, ((W - text_a_pil.width)//2, y_a), text_a_pil)
    
    y_b = HALF_H + (HALF_H - text_b_pil.height)//2 + 20
    bg_copy.paste(text_b_pil, ((W - text_b_pil.width)//2, y_b), text_b_pil)
    
    # VS circle
    vs_pil = create_vs_circle_image("VS", size=210)
    bg_copy.paste(vs_pil, ((W - vs_pil.width)//2, HALF_H - 105), vs_pil)
    
    # Label
    label_pil = create_round_label_image(1, 4)
    bg_copy.paste(label_pil, ((W - label_pil.width)//2, 80), label_pil)
    
    # Percentagens (preview)
    percent_a_pil = create_percent_image(percent_a, bg_color=(255,255,255), text_color=(255,59,48))
    percent_b_pil = create_percent_image(percent_b, bg_color=(255,255,255), text_color=(0,122,255))
    bg_copy.paste(percent_a_pil, ((W - percent_a_pil.width)//2, HALF_H - 220), percent_a_pil)
    bg_copy.paste(percent_b_pil, ((W - percent_b_pil.width)//2, HALF_H + 70), percent_b_pil)
    
    bg_copy.save(output)
    print(f"[preview] Imagem salva em {output} - {bg_copy.size}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", default="Have unlimited money", help="Opção A")
    parser.add_argument("--b", default="Be able to teleport anywhere", help="Opção B")
    parser.add_argument("--pa", default="72%")
    parser.add_argument("--pb", default="28%")
    parser.add_argument("--output", default="preview.png")
    args = parser.parse_args()
    generate_preview(args.a, args.b, args.pa, args.pb, args.output)
