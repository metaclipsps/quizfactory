#!/bin/bash
echo "=== FIX para erro PIL.Image.ANTIALIAS ==="
echo "Este erro acontece porque instalaste Pillow 10+ que removeu ANTIALIAS"
echo ""

# Ativar venv
source .venv/bin/activate

echo "[1/3] Desinstalando Pillow atual..."
pip uninstall -y Pillow

echo "[2/3] Instalando Pillow 9.5.0 compatível..."
pip install Pillow==9.5.0
pip install decorator==4.4.2

echo "[3/3] Verificando..."
python -c "from PIL import Image; print('Pillow', Image.__version__, 'ANTIALIAS:', hasattr(Image, 'ANTIALIAS'))"
python -c "import moviepy; print('moviepy', moviepy.__version__)"

echo ""
echo "=== FIX aplicado! Tenta de novo: ==="
echo "python make_quiz.py --input quizzes/demo_1round.json --output output/demo_1round.mp4"
