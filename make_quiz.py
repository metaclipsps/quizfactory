#!/usr/bin/env python3
"""
make_quiz.py - Gerador de vídeos Would You Rather (Vermelho vs Azul) 9:16
Uso:
  python make_quiz.py --input quizzes/quiz01.json --output output/quiz01.mp4
  python make_quiz.py --input quizzes/ --output output/ --voice en-US-AriaNeural

Compatível com o sistema shortsfactory (.venv, moviepy, ffmpeg)
"""

import os
import json
import argparse
import asyncio
import textwrap
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# FIX Pillow 10+ compat - MoviePy 1.0.3 usa ANTIALIAS que foi removido no Pillow 10
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
# FIX para versões ainda mais novas
if not hasattr(Image, 'BICUBIC'):
    Image.BICUBIC = Image.Resampling.BICUBIC if hasattr(Image, 'Resampling') else 3

# MoviePy 1.0.3
from moviepy.editor import (
    ImageClip, AudioFileClip, AudioClip, CompositeAudioClip,
    CompositeVideoClip, concatenate_videoclips, ColorClip
)

# Configurações visuais
W, H = 1080, 1920
HALF_H = H // 2
RED = (255, 59, 48)      # #FF3B30
BLUE = (0, 122, 255)     # #007AFF
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_RED = (180, 30, 30)
DARK_BLUE = (0, 70, 180)

COUNTDOWN_DURATION = 3
REVEAL_DURATION = 2.5

# Força MAIÚSCULAS estilo viral TikTok + FONTE GIGANTE para ler no telemóvel
FORCE_UPPERCASE = True
STROKE_WIDTH = 14  # contorno bem grosso estilo TikTok
FONT_SIZE_BASE = 120  # GIGANTE - antes era 88, agora 120
FONT_SIZE_SHORT = 135  # texto curto <30 chars
FONT_SIZE_MEDIUM = 110 # texto médio 30-60 chars
FONT_SIZE_LONG = 85    # texto longo 60+ chars

# -------------------- Fontes (ROBUSTO - com assets/ incluso) --------------------
def find_font(bold=True):
    import glob
    # PRIORIDADE 1: pasta assets/ que já vem com o projeto (resolve teu problema de letras minúsculas)
    candidates = [
        "assets/DejaVuSans-Bold.ttf" if bold else "assets/DejaVuSans.ttf",
        "./assets/DejaVuSans-Bold.ttf" if bold else "./assets/DejaVuSans.ttf",
        "quizfactory/assets/DejaVuSans-Bold.ttf" if bold else "quizfactory/assets/DejaVuSans.ttf",
        "/home/david/shortsfactory/quizfactory/assets/DejaVuSans-Bold.ttf" if bold else "/home/david/shortsfactory/quizfactory/assets/DejaVuSans.ttf",
        # Sistema
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    # Glob search para achar qualquer DejaVu
    for pattern in ["/usr/share/fonts/**/DejaVuSans-Bold.ttf", "/usr/share/fonts/**/DejaVuSans.ttf", "**/DejaVuSans-Bold.ttf", "assets/*.ttf"]:
        candidates.extend(glob.glob(pattern, recursive=True))
    
    for p in candidates:
        if p and os.path.exists(p):
            try:
                ImageFont.truetype(p, 20)
                return p
            except:
                continue
    
    # Tenta pelo nome (Pillow procura no font path)
    for name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "LiberationSans-Bold.ttf"]:
        try:
            ImageFont.truetype(name, 20)
            return name
        except:
            pass

    print("[font] AVISO: Nenhuma fonte TTF encontrada! O texto vai ficar minúsculo.")
    print("[font] Solução: sudo apt install fonts-dejavu-core")
    print("[font] Ou verifica se a pasta assets/ tem DejaVuSans-Bold.ttf")
    return None

FONT_BOLD_PATH = find_font(bold=True)
FONT_REG_PATH = find_font(bold=False) or FONT_BOLD_PATH

print(f"[font] bold: {FONT_BOLD_PATH}")
print(f"[font] regular: {FONT_REG_PATH}")
if not FONT_BOLD_PATH:
    print("[font] ERRO CRÍTICO: Fonte bold não encontrada! Vai ficar minúsculo!")
    print("[font] Corre: ls assets/  e  sudo apt install fonts-dejavu-core")
else:
    print(f"[font] ✅ Fonte OK ({FONT_BOLD_PATH}) - tamanho 135 vai ficar GIGANTE")

def load_font(size, bold=True):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    if path and os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception as e:
            print(f"[font] Falha {path}: {e}")
    # Tenta assets direto
    for p in ["assets/DejaVuSans-Bold.ttf", "assets/DejaVuSans.ttf", "./assets/DejaVuSans-Bold.ttf", "quizfactory/assets/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    # Nome sistema
    for name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "LiberationSans-Bold.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            pass
    
    print(f"[font] FALLBACK minúsculo! Não achou fonte para {size}")
    return ImageFont.load_default()

# -------------------- Texto com PIL --------------------
def create_wrapped_text_image(text, max_width_px=900, font_size=80, color=WHITE, stroke_width=6, stroke_color=BLACK, bold=True, align="center", line_spacing=15):
    """
    Cria uma imagem PIL transparente com texto quebrado automaticamente
    Retorna PIL Image
    """
    # FORÇA MAIÚSCULAS se ativado
    if FORCE_UPPERCASE:
        text = text.upper()
    
    # Se stroke não foi passado, usa o global mais grosso
    if stroke_width == 6:
        stroke_width = STROKE_WIDTH
    if font_size == 80:
        font_size = FONT_SIZE_BASE
        
    font = load_font(font_size, bold=bold)
    # Para medir, criar draw temporário
    dummy_img = Image.new("RGB", (max_width_px, 100))
    draw = ImageDraw.Draw(dummy_img)

    # Quebra de linha inteligente
    # Estimar chars por linha baseado em font_size
    # Melhor: quebrar por palavras e medir
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        # medir
        try:
            # Pillow >=10 usa textbbox
            bbox = draw.textbbox((0,0), test_line, font=font, stroke_width=stroke_width)
            w = bbox[2] - bbox[0]
        except:
            w, _ = draw.textsize(test_line, font=font)
        if w <= max_width_px - 20:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calcular altura total
    line_heights = []
    max_line_width = 0
    for line in lines:
        try:
            bbox = draw.textbbox((0,0), line, font=font, stroke_width=stroke_width)
            lw = bbox[2]-bbox[0]
            lh = bbox[3]-bbox[1]
        except:
            lw, lh = draw.textsize(line, font=font)
        line_heights.append(lh)
        max_line_width = max(max_line_width, lw)

    total_h = sum(line_heights) + line_spacing * (len(lines)-1) + 20
    total_w = max(max_width_px, max_line_width + 40)

    # Criar imagem final transparente
    img = Image.new("RGBA", (total_w, total_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    y = 10
    for i, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0,0), line, font=font, stroke_width=stroke_width)
            lw = bbox[2]-bbox[0]
            lh = bbox[3]-bbox[1]
        except:
            lw, lh = draw.textsize(line, font=font)

        if align == "center":
            x = (total_w - lw) // 2
        elif align == "left":
            x = 10
        else:
            x = total_w - lw - 10

        draw.text((x, y), line, font=font, fill=color, stroke_width=stroke_width, stroke_fill=stroke_color, align=align)
        y += lh + line_spacing

    return img

def pil_to_imageclip(pil_img, duration):
    """Converte PIL para ImageClip"""
    np_img = np.array(pil_img)
    clip = ImageClip(np_img, transparent=True).set_duration(duration)
    return clip

def create_background():
    """Cria background 1080x1920 metade vermelho metade azul"""
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    # Topo vermelho
    draw.rectangle([0, 0, W, HALF_H], fill=RED)
    # Fundo azul
    draw.rectangle([0, HALF_H, W, H], fill=BLUE)
    # Linha divisória branca grossa
    draw.rectangle([0, HALF_H-6, W, HALF_H+6], fill=WHITE)
    # Adicionar leve vinheta / borda escura
    # Cantos arredondados internos? manter simples
    return img

def create_vs_circle_image(text="VS", size=220, bg_color=WHITE, text_color=BLACK, number=False):
    """Cria círculo central com VS ou número"""
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Sombra
    draw.ellipse([8, 8, size-2, size-2], fill=(0,0,0,120))
    # Círculo branco
    draw.ellipse([0, 0, size-12, size-12], fill=bg_color, outline=BLACK, width=8)
    # Texto
    font_size = 90 if not number else 110
    font = load_font(font_size, bold=True)
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        tw = bbox[2]-bbox[0]
        th = bbox[3]-bbox[1]
    except:
        tw, th = draw.textsize(text, font=font)
    tx = (size-12 - tw)//2
    ty = (size-12 - th)//2 - 5
    draw.text((tx, ty), text, font=font, fill=text_color, stroke_width=3, stroke_fill=WHITE if text_color==BLACK else BLACK)
    return img

def create_percent_image(percent_text, size_w=420, size_h=160, bg_color=WHITE, text_color=BLACK):
    """Cria badge de percentagem estilo votação"""
    img = Image.new("RGBA", (size_w, size_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Fundo arredondado
    # Desenhar retângulo com cantos arredondados (pill)
    radius = size_h//2
    draw.rounded_rectangle([0,0,size_w-1,size_h-1], radius=radius, fill=bg_color, outline=BLACK, width=6)
    font = load_font(85, bold=True)
    try:
        bbox = draw.textbbox((0,0), percent_text, font=font)
        tw = bbox[2]-bbox[0]
        th = bbox[3]-bbox[1]
    except:
        tw, th = draw.textsize(percent_text, font=font)
    tx = (size_w - tw)//2
    ty = (size_h - th)//2 - 4
    draw.text((tx, ty), percent_text, font=font, fill=text_color)
    return img

def create_round_label_image(round_idx, total, width=500, height=90):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    text = f"ROUND {round_idx}/{total}"
    font = load_font(42, bold=True)
    # Fundo preto semi transparente
    draw.rounded_rectangle([0,0,width-1,height-1], radius=25, fill=(0,0,0,160))
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        tw = bbox[2]-bbox[0]
        th = bbox[3]-bbox[1]
    except:
        tw, th = draw.textsize(text, font=font)
    tx = (width - tw)//2
    ty = (height - th)//2 - 2
    draw.text((tx, ty), text, font=font, fill=WHITE)
    return img

# -------------------- Áudio SFX --------------------
def make_beep_clip(freq=800, duration=0.18, volume=0.6, sample_rate=44100):
    def make_frame(t):
        # t pode ser array
        # beep com envelope
        envelope = np.exp(-3*t) if np.isscalar(t) else np.exp(-3*t)
        # seno
        if isinstance(t, np.ndarray):
            wave = np.sin(2*np.pi*freq*t) * envelope
            # estereo
            return np.column_stack([wave, wave]) * volume
        else:
            return np.array([np.sin(2*np.pi*freq*t)*envelope*volume, np.sin(2*np.pi*freq*t)*envelope*volume])
    return AudioClip(make_frame, duration=duration, fps=sample_rate)

def make_ding_clip(duration=0.6, volume=0.7):
    def make_frame(t):
        # dois tons
        f1, f2 = 1200, 1800
        if isinstance(t, np.ndarray):
            env = np.exp(-2.5*t)
            w1 = np.sin(2*np.pi*f1*t) * env
            w2 = np.sin(2*np.pi*f2*t) * env * 0.6
            wave = w1 + w2
            return np.column_stack([wave, wave]) * volume
        else:
            env = np.exp(-2.5*t)
            wave = np.sin(2*np.pi*f1*t)*env + np.sin(2*np.pi*f2*t)*env*0.6
            return np.array([wave*volume, wave*volume])
    return AudioClip(make_frame, duration=duration, fps=44100)

# -------------------- TTS --------------------
async def tts_edge(text, output_path, voice="en-US-AriaNeural"):
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"[tts edge] falhou: {e}")
        return False

def tts_gtts(text, output_path, lang="en"):
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"[tts gtts] falhou: {e}")
        return False

def generate_tts_sync(text, output_path, voice="en-US-AriaNeural"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Tenta edge-tts
    try:
        asyncio.run(tts_edge(text, str(output_path), voice=voice))
        if output_path.exists() and output_path.stat().st_size > 1000:
            print(f"[tts] OK edge-tts: {output_path}")
            return True
    except Exception as e:
        print(f"[tts] edge erro: {e}")

    # Fallback gTTS
    if tts_gtts(text, str(output_path)):
        print(f"[tts] OK gTTS fallback: {output_path}")
        return True

    print("[tts] FALHOU TUDO")
    return False

# -------------------- Criação de uma ronda --------------------
def create_round_clip(option_a, option_b, percent_a, percent_b, audio_path, round_idx, total_rounds, temp_dir):
    print(f"\n--- Round {round_idx}/{total_rounds} ---")
    print(f"A: {option_a} ({percent_a})")
    print(f"B: {option_b} ({percent_b})")

    audio_clip = AudioFileClip(str(audio_path))
    audio_duration = audio_clip.duration
    print(f"[audio] duração: {audio_duration:.2f}s")

    total_duration = audio_duration + COUNTDOWN_DURATION + REVEAL_DURATION

    # Background base
    bg_pil = create_background()
    bg_clip = ImageClip(np.array(bg_pil)).set_duration(total_duration)

    # Textos das opções - com tamanho GIGANTE para TikTok
    len_a = len(option_a)
    len_b = len(option_b)
    font_size_a = FONT_SIZE_SHORT if len_a < 30 else FONT_SIZE_MEDIUM if len_a < 60 else FONT_SIZE_LONG
    font_size_b = FONT_SIZE_SHORT if len_b < 30 else FONT_SIZE_MEDIUM if len_b < 60 else FONT_SIZE_LONG

    # Agora o .upper() é feito dentro da função, mas mantemos aqui também por segurança
    text_a_pil = create_wrapped_text_image(option_a, max_width_px=980, font_size=font_size_a, color=WHITE, stroke_width=STROKE_WIDTH, stroke_color=BLACK, bold=True, line_spacing=12)
    text_b_pil = create_wrapped_text_image(option_b, max_width_px=980, font_size=font_size_b, color=WHITE, stroke_width=STROKE_WIDTH, stroke_color=BLACK, bold=True, line_spacing=12)

    text_a_clip = pil_to_imageclip(text_a_pil, total_duration).set_position(("center", 220))
    # Para garantir que fica no topo: y = HALF_H/2 - h/2
    # Vamos ajustar posição para centro do topo
    # Calcular centro
    h_a = text_a_pil.height
    y_a = (HALF_H - h_a)//2 - 40
    text_a_clip = text_a_clip.set_position(("center", y_a))

    h_b = text_b_pil.height
    y_b = HALF_H + (HALF_H - h_b)//2 + 20
    text_b_clip = pil_to_imageclip(text_b_pil, total_duration).set_position(("center", y_b))

    # Round label
    label_pil = create_round_label_image(round_idx, total_rounds)
    label_clip = pil_to_imageclip(label_pil, total_duration).set_position(("center", 80))

    # VS circle - aparece durante áudio
    vs_pil = create_vs_circle_image("VS", size=210)
    vs_clip = pil_to_imageclip(vs_pil, audio_duration).set_position(("center", HALF_H-105)).set_start(0)

    # Countdown numbers 3,2,1
    countdown_clips = []
    tick_audio_clips = []
    for i in range(COUNTDOWN_DURATION):
        num = COUNTDOWN_DURATION - i
        color_bg = WHITE
        # Alternar cor? 3 vermelho? manter branco
        num_pil = create_vs_circle_image(str(num), size=230, bg_color=WHITE, text_color=RED if num%2==1 else BLUE, number=True)
        clip = pil_to_imageclip(num_pil, 1).set_position(("center", HALF_H-115)).set_start(audio_duration + i)
        # Efeito pop: scale
        clip = clip.resize(lambda t: 0.7 + 0.3*(1-np.exp(-8*t)) if t<0.5 else 1.0 + 0.05*np.sin(10*t))
        countdown_clips.append(clip)

        # Tick SFX
        tick = make_beep_clip(freq=900 + num*80, duration=0.22, volume=0.5).set_start(audio_duration + i)

        tick_audio_clips.append(tick)

    # Percentagens - aparecem no reveal
    percent_a_pil = create_percent_image(percent_a, bg_color=WHITE, text_color=RED)
    percent_b_pil = create_percent_image(percent_b, bg_color=WHITE, text_color=BLUE)

    # Posição: abaixo do texto A e acima do texto B, mas mais perto do centro
    # Top percent embaixo do topo
    y_percent_a = HALF_H - 220
    y_percent_b = HALF_H + 70

    percent_a_clip = pil_to_imageclip(percent_a_pil, REVEAL_DURATION).set_position(("center", y_percent_a)).set_start(audio_duration+COUNTDOWN_DURATION)
    percent_b_clip = pil_to_imageclip(percent_b_pil, REVEAL_DURATION).set_position(("center", y_percent_b)).set_start(audio_duration+COUNTDOWN_DURATION)

    # Animação pop para percentagens
    def pop_resize(t):
        # t desde 0
        # cresce rapido de 0 a 1.2 depois 1
        if t < 0.3:
            return 0.2 + 3.0*t
        elif t < 0.5:
            return 1.2 - 0.4*(t-0.3)/0.2
        else:
            return 1.0

    percent_a_clip = percent_a_clip.resize(pop_resize)
    percent_b_clip = percent_b_clip.resize(pop_resize)

    # Ding SFX no reveal
    ding_clip = make_ding_clip(duration=0.7, volume=0.8).set_start(audio_duration+COUNTDOWN_DURATION)

    # Composição de vídeo
    video_layers = [bg_clip, text_a_clip, text_b_clip, label_clip, vs_clip] + countdown_clips + [percent_a_clip, percent_b_clip]

    # Para efeito extra: adicionar emojis / ícones? Vamos adicionar barra de VS pulsando?
    final_video = CompositeVideoClip(video_layers, size=(W, H)).set_duration(total_duration)

    # Áudio final: voz + ticks + ding
    final_audio = CompositeAudioClip([audio_clip] + tick_audio_clips + [ding_clip]).set_duration(total_duration)
    final_video = final_video.set_audio(final_audio)

    return final_video

def create_intro_clip(duration=2.2, title="WOULD YOU RATHER?"):
    bg_pil = create_background()
    bg_clip = ImageClip(np.array(bg_pil)).set_duration(duration)

    title_pil = create_wrapped_text_image(title, max_width_px=900, font_size=110, color=WHITE, stroke_width=10, stroke_color=BLACK, bold=True)
    title_clip = pil_to_imageclip(title_pil, duration).set_position("center")

    subtitle_pil = create_wrapped_text_image("DIFFICULT CHOICES!", max_width_px=800, font_size=52, color=WHITE, stroke_width=5, stroke_color=BLACK, bold=True)
    subtitle_clip = pil_to_imageclip(subtitle_pil, duration).set_position(("center", HALF_H + 250))

    # beep intro
    beep1 = make_beep_clip(600, 0.2, 0.5).set_start(0.1)
    beep2 = make_beep_clip(900, 0.3, 0.6).set_start(0.5)
    audio = CompositeAudioClip([beep1, beep2]).set_duration(duration)

    comp = CompositeVideoClip([bg_clip, title_clip, subtitle_clip], size=(W,H)).set_duration(duration).set_audio(audio)
    return comp

def create_outro_clip(duration=2.5, text="COMMENT YOUR CHOICE!"):
    bg_pil = create_background()
    bg_clip = ImageClip(np.array(bg_pil)).set_duration(duration)

    text_pil = create_wrapped_text_image(text, max_width_px=900, font_size=78, color=WHITE, stroke_width=8, stroke_color=BLACK, bold=True)
    text_clip = pil_to_imageclip(text_pil, duration).set_position("center")
    # Pop
    text_clip = text_clip.resize(lambda t: 0.8 + 0.2*np.sin(6*t) + 0.2*(1-np.exp(-5*t)))

    ding = make_ding_clip(0.6, 0.7).set_start(0.2)
    audio = CompositeAudioClip([ding]).set_duration(duration)

    comp = CompositeVideoClip([bg_clip, text_clip], size=(W,H)).set_duration(duration).set_audio(audio)
    return comp

# -------------------- Gerador principal --------------------
def gerar_video_quiz(json_path, output_path, voice="en-US-AriaNeural", temp_dir="temp_audio"):
    json_path = Path(json_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Path(temp_dir).mkdir(parents=True, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        perguntas = json.load(f)

    print(f"[quiz] {len(perguntas)} perguntas carregadas de {json_path}")

    clips = []
    # Intro
    intro = create_intro_clip(2.2, "WOULD YOU RATHER?")
    clips.append(intro)

    for idx, item in enumerate(perguntas, start=1):
        option_a = item.get("option_a", "").strip()
        option_b = item.get("option_b", "").strip()
        percent_a = item.get("percent_a", f"{random.randint(30,70)}%")
        percent_b = item.get("percent_b", f"{100 - int(percent_a.strip('%'))}%")

        if not option_a or not option_b:
            print(f"[skip] round {idx} sem opções")
            continue

        texto_audio = f"Would you rather... {option_a}, or... {option_b}?"
        audio_file = Path(temp_dir) / f"round_{idx}_{json_path.stem}.mp3"

        if not audio_file.exists():
            ok = generate_tts_sync(texto_audio, audio_file, voice=voice)
            if not ok:
                # criar audio silencioso de 3s como fallback
                print("[fallback] criando audio silencioso")
                silent = AudioClip(lambda t: np.array([0,0]), duration=3.5, fps=44100)
                silent.write_audiofile(str(audio_file), fps=44100, logger=None)
        else:
            print(f"[cache] usando audio existente {audio_file}")

        round_clip = create_round_clip(option_a, option_b, percent_a, percent_b, audio_file, idx, len(perguntas), temp_dir)
        clips.append(round_clip)

    # Outro
    outro = create_outro_clip(2.5, "COMMENT YOUR CHOICE!")
    clips.append(outro)

    print(f"[concat] juntando {len(clips)} clips...")
    final = concatenate_videoclips(clips, method="compose")

    print(f"[export] exportando para {output_path} ...")
    # Codec: libx264, aac
    final.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    print(f"[done] Vídeo salvo em {output_path}")
    return str(output_path)

# -------------------- CLI --------------------
def main():
    parser = argparse.ArgumentParser(description="Gerador de vídeos Would You Rather - Red vs Blue")
    parser.add_argument("--input", "-i", required=True, help="Arquivo JSON ou pasta com JSONs")
    parser.add_argument("--output", "-o", required=True, help="Arquivo MP4 de saída ou pasta")
    parser.add_argument("--voice", default="en-US-AriaNeural", help="Voz edge-tts (ex: en-US-GuyNeural, en-US-AriaNeural, en-GB-SoniaNeural)")
    parser.add_argument("--temp", default="temp_audio", help="Pasta temporária para áudios")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        # Batch: todos JSONs na pasta
        json_files = list(input_path.glob("*.json"))
        if not json_files:
            print(f"Nenhum JSON encontrado em {input_path}")
            return
        output_path.mkdir(parents=True, exist_ok=True)
        for jf in json_files:
            out_file = output_path / (jf.stem + ".mp4")
            gerar_video_quiz(jf, out_file, voice=args.voice, temp_dir=args.temp)
    else:
        # Single
        if output_path.is_dir() or not output_path.suffix:
            output_path.mkdir(parents=True, exist_ok=True)
            out_file = output_path / (input_path.stem + ".mp4")
        else:
            out_file = output_path
        gerar_video_quiz(input_path, out_file, voice=args.voice, temp_dir=args.temp)

if __name__ == "__main__":
    main()
