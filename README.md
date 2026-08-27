# ShortsFactory - Would You Rather (Red vs Blue) Generator

Sistema 100% automatizado para gerar vídeos virais de quiz estilo TikTok / YouTube Shorts com tela dividida Vermelho vs Azul.

Compatível com o teu sistema anterior de histórias (mesmo .venv, moviepy, ffmpeg).

## 🎬 Como é o vídeo?

- **Formato:** 1080x1920 (9:16 vertical)
- **Duração:** 40-55 segundos (4-5 rondas)
- **Layout:**
  - Topo: Vermelho #FF3B30 com Opção A
  - Fundo: Azul #007AFF com Opção B
  - Centro: Círculo VS que vira countdown 3,2,1 + SFX tick
  - Final da ronda: Revelação de percentagens (ex: 72% vs 28%) + SFX ding para gerar comentários

## 📁 Estrutura

```
shortsfactory/
├── make_quiz.py          # Script principal (1 vídeo)
├── batch.py              # Gera todos os JSONs da pasta quizzes/
├── generate_quizzes.py   # Gera JSONs automaticamente sem API
├── requirements.txt
├── quizzes/
│   ├── quiz01.json
│   └── quiz02.json
├── output/               # Vídeos MP4 gerados
└── temp_audio/           # Áudios TTS cacheados
```

## 🚀 Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

**Dependências:**
- moviepy 1.0.3 (usa FFmpeg por baixo)
- edge-tts (voz IA gratuita da Microsoft - melhor qualidade)
- gTTS (fallback)
- Pillow + numpy

Verifica se tens FFmpeg:
```bash
ffmpeg -version
```

## 📝 Formato do JSON

```json
[
  {
    "option_a": "Have unlimited money",
    "option_b": "Be able to teleport anywhere",
    "percent_a": "72%",
    "percent_b": "28%"
  }
]
```

## 🎙️ Gerar 1 vídeo

```bash
# Single file
python make_quiz.py --input quizzes/quiz01.json --output output/quiz01.mp4

# Com voz específica
python make_quiz.py --input quizzes/quiz01.json --output output/quiz01.mp4 --voice en-US-GuyNeural

# Pasta inteira (gera um mp4 por json)
python make_quiz.py --input quizzes/ --output output/
```

Vozes recomendadas (edge-tts):
- `en-US-AriaNeural` (feminina, viral no TikTok)
- `en-US-GuyNeural` (masculina grave)
- `en-GB-SoniaNeural` (britânica)
- `en-US-JennyNeural` (jovem, energética)

## 📦 Gerar em lote (batch)

```bash
python batch.py --quizzes quizzes --output output
# Gera com vozes aleatórias para variar
```

## 🤖 Gerar 50 quizzes automaticamente

Sem precisar do ChatGPT:

```bash
python generate_quizzes.py --count 50 --rounds 5
# Cria quiz003.json até quiz052.json
```

Depois:
```bash
python batch.py
```

Se quiseres usar ChatGPT, pede:
> "Gera 50 Would You Rather em JSON no formato [{\"option_a\":\"...\",\"option_b\":\"...\",\"percent_a\":\"68%\",\"percent_b\":\"32%\"}] com 4 itens por array, temas virais, controversos"

E salva em `quizzes/`.

## ⚡ Fluxo recomendado para viralizar

1. `python generate_quizzes.py --count 20 --rounds 4`
2. `python batch.py --output output`
3. Posta 2-3 por dia no TikTok com hashtags #wouldyourather #quiz #redvsblue
4. Título: "99% CHOOSE WRONG! 😱" / "Only 1% agree with this..."

**Dica de engajamento:** Percentagens 49% vs 51% ou 72% vs 28% geram mais comentários. O script já randomiza para evitar 50/50.

## 🔧 Customização

Edita em `make_quiz.py`:
- `RED`, `BLUE` para cores
- `COUNTDOWN_DURATION = 3`
- `W, H = 1080,1920` resolução
- Fontes em `find_font()`
- Intro/Outro texto em `create_intro_clip()`

## 🐛 Troubleshooting

- **Sem áudio TTS:** Verifica internet. Edge-TTS precisa de rede. Fallback gTTS também precisa. Se offline, ele gera áudio silencioso mas vídeo sai igual.
- **Erro MoviePy TextClip:** Este projeto NÃO usa TextClip com ImageMagick, usa Pillow direto, então não precisa configurar IMAGEMAGICK_BINARY.
- **Vídeo preto:** Atualiza ffmpeg. `sudo apt update && sudo apt install ffmpeg`
- **Lento:** Usa `--preset ultrafast` já está ativo. Para mais velocidade, reduz rounds para 4.

## 📈 Próximos upgrades

- Adicionar música de fundo trending (low volume)
- Adicionar emojis automáticos com base no texto
- Versão "This or That" com imagens
- Versão PT-BR com voz `pt-BR-FranciscaNeural`

Feito para rodar 100% no terminal. Bora viralizar!
