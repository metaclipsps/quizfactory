#!/usr/bin/env python3
"""
generate_quizzes.py - Gera JSONs de Would You Rather automaticamente
Uso:
  python generate_quizzes.py --count 20
  python generate_quizzes.py --count 50 --output quizzes/
"""

import json
import random
import argparse
from pathlib import Path

# Banco de ideias para gerar perguntas sem precisar de API externa
TEMPLATES = [
    ("Have unlimited money", "Be able to teleport anywhere"),
    ("Always know when someone is lying", "Get away with any lie you tell"),
    ("Live in a luxury mansion alone", "Live in a cozy van with your soulmate"),
    ("Eat your favorite meal every day forever", "Never have to eat or sleep again"),
    ("Have super strength", "Have super speed"),
    ("Be able to talk to animals", "Be able to speak every human language"),
    ("Live without internet for a year", "Live without friends for a year"),
    ("Never use social media again", "Never watch another movie or show"),
    ("Be famous on the internet", "Be famous in real life"),
    ("Have 10 years of perfect health", "Have 100 million dollars right now"),
    ("Be able to time travel to the past", "Be able to time travel to the future"),
    ("Never feel pain again", "Never feel sadness again"),
    ("Have a personal chef", "Have a personal driver"),
    ("Live on Mars with internet", "Live on a private island without internet"),
    ("Be the smartest person alive", "Be the most attractive person alive"),
    ("Always have to say what you think", "Never be able to speak again"),
    ("Be able to fly", "Be invisible"),
    ("Live one 1000-year life", "Live ten 100-year lives with memory reset"),
    ("Have free first class flights forever", "Have free 5-star hotels forever"),
    ("Know the date of your death", "Know the cause of your death"),
    ("Be able to control fire", "Be able to control water"),
    ("Have unlimited battery on your phone", "Have unlimited fuel in your car"),
    ("Never have to work again but poor", "Work your dream job but have to work daily"),
    ("Be able to pause time", "Be able to rewind time 10 seconds"),
    ("Eat only pizza for a year", "Eat only burgers for a year"),
    ("Have a rewind button for life", "Have a pause button for life"),
    ("Be loved by everyone but poor", "Be hated by everyone but rich"),
    ("Live without music", "Live without movies"),
    ("Have a dragon as a pet", "Have a unicorn as a pet"),
    ("Always be 10 minutes early", "Always be 20 minutes late"),
    ("Be able to breathe underwater", "Be able to survive in space without suit"),
    ("Have $1M now", "Have $10k every month for life"),
    ("Never need to charge your phone", "Never need to do laundry"),
    ("Be able to read minds", "Be able to see the future for 10 seconds"),
    ("Live in Harry Potter world", "Live in Marvel universe"),
    ("Have 100% honest friends", "Have 100% loyal partner"),
    ("Be able to instantly learn any skill", "Be able to instantly master any instrument"),
    ("Live in a city with no crime", "Live in a forest with magical creatures"),
    ("Have the ability to heal anyone", "Have the ability to bring one person back"),
    ("Never feel cold", "Never feel hot"),
]

def gen_percentages():
    a = random.randint(25, 75)
    # Evitar 50/50 exato para gerar debate
    if a == 50:
        a = 51
    b = 100 - a
    return f"{a}%", f"{b}%"

def generate_one_quiz(num_rounds=4):
    selected = random.sample(TEMPLATES, num_rounds)
    quiz = []
    for opt_a, opt_b in selected:
        # 50% chance de inverter ordem para variedade
        if random.random() > 0.5:
            opt_a, opt_b = opt_b, opt_a
        pa, pb = gen_percentages()
        quiz.append({
            "option_a": opt_a,
            "option_b": opt_b,
            "percent_a": pa,
            "percent_b": pb
        })
    return quiz

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10, help="Quantos arquivos JSON gerar")
    parser.add_argument("--rounds", type=int, default=4, help="Perguntas por vídeo (4-5 recomendado)")
    parser.add_argument("--output", default="quizzes", help="Pasta de saída")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Descobrir próximo índice para não sobrescrever
    existing = len(list(out_dir.glob("*.json")))
    start_idx = existing + 1

    for i in range(args.count):
        idx = start_idx + i
        quiz = generate_one_quiz(num_rounds=args.rounds)
        out_file = out_dir / f"quiz{idx:03d}.json"
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(quiz, f, indent=2, ensure_ascii=False)
        print(f"[gen] {out_file} criado com {args.rounds} rounds")

    print(f"\n[done] {args.count} quizzes gerados em {out_dir}/")

if __name__ == "__main__":
    main()
