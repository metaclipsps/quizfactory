#!/bin/bash
# run.sh - Comandos rápidos para gerar vídeos Would You Rather

echo "=== ShortsFactory Quiz - Red vs Blue ==="

# 1. Ativar venv se existir
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# 2. Instalar deps
pip install -q -r requirements.txt

# 3. Gerar preview rápido (sem vídeo)
echo "[1/4] Gerando preview.png..."
python preview.py

# 4. Gerar 10 quizzes novos se quiseres
echo "[2/4] Gerando 10 quizzes novos..."
python generate_quizzes.py --count 10 --rounds 4

# 5. Gerar 1 vídeo demo (1 ronda = rápido)
echo "[3/4] Gerando vídeo demo de 1 ronda..."
python make_quiz.py --input quizzes/demo_1round.json --output output/demo_1round.mp4 --voice en-US-AriaNeural

# 6. Gerar vídeo completo (4 rondas = 40-55s)
echo "[4/4] Gerando vídeo completo quiz01..."
python make_quiz.py --input quizzes/quiz01.json --output output/quiz01.mp4 --voice en-US-AriaNeural

echo "=== DONE ==="
echo "Vídeos em output/"
ls -lh output/
