#!/bin/bash
# setup_new_venv.sh - Cria .venv isolado SÓ para quizzes
# Corre este ficheiro DENTRO da pasta quizfactory

echo "=== QuizFactory - Setup .venv isolado ==="
echo "Pasta atual: $(pwd)"

# 1. Criar venv
if [ ! -d ".venv" ]; then
  echo "[1/3] Criando .venv..."
  python3 -m venv .venv
else
  echo "[1/3] .venv já existe, a usar o existente"
fi

# 2. Ativar e instalar
echo "[2/3] Instalando dependências..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo "[3/3] Testando..."
python -c "import moviepy; print('moviepy', moviepy.__version__)"
python -c "import edge_tts; print('edge-tts OK')"
python preview.py --output preview_test.png && echo "Preview OK: preview_test.png"

echo ""
echo "=== PRONTO! ==="
echo "Para usar no futuro:"
echo "  cd ~/projects/quizfactory"
echo "  source .venv/bin/activate"
echo "  python make_quiz.py --input quizzes/quiz01.json --output output/quiz01.mp4"
echo ""
echo "Para desativar venv: deactivate"
