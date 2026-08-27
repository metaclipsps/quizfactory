#!/usr/bin/env python3
"""
batch.py - Gera vários vídeos em lote a partir da pasta quizzes/
Uso:
  python batch.py
  python batch.py --quizzes quizzes/ --output output/ --voice en-US-GuyNeural
"""

import argparse
from pathlib import Path
from make_quiz import gerar_video_quiz
import json
import random

# Lista de vozes populares para variar
VOICES = [
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-AU-NatashaNeural",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quizzes", default="quizzes", help="Pasta com JSONs")
    parser.add_argument("--output", default="output", help="Pasta de saída")
    parser.add_argument("--voice", default=None, help="Voz fixa (se não passar, randomiza)")
    parser.add_argument("--limit", type=int, default=0, help="Limite de vídeos (0 = todos)")
    args = parser.parse_args()

    q_dir = Path(args.quizzes)
    o_dir = Path(args.output)
    o_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(q_dir.glob("*.json"))
    if args.limit > 0:
        files = files[:args.limit]

    if not files:
        print(f"Nenhum JSON em {q_dir}")
        return

    print(f"[batch] Encontrados {len(files)} quizzes")
    for jf in files:
        voice = args.voice or random.choice(VOICES)
        out = o_dir / f"{jf.stem}.mp4"
        if out.exists():
            print(f"[skip] {out} já existe, pulando. Apague para regenerar.")
            continue
        try:
            print(f"\n{'='*60}\n Gerando {jf} -> {out} com voz {voice}\n{'='*60}")
            gerar_video_quiz(jf, out, voice=voice)
        except Exception as e:
            print(f"[ERRO] Falha em {jf}: {e}")
            import traceback
            traceback.print_exc()

    print("\n[batch] Finalizado!")

if __name__ == "__main__":
    main()
