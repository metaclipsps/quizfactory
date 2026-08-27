# 🤖 Bot Telegram - Guia Completo em 5 Minutos

## Passo 1 - Criar o Bot (1 min)
1. Abre o Telegram
2. Procura `@BotFather`
3. Manda `/newbot`
4. Escolhe nome: `QuizFactoryBot`
5. Escolhe username: `teunome_quiz_bot` (tem de terminar em bot)
6. Ele vai te dar um TOKEN tipo `123456789:ABCdefGHIjklMNOpqr...` -> **COPIA**

## Passo 2 - Instalar e Correr (2 min)
No teu PC, dentro da pasta `quizfactory/`:

```bash
# Ativa o venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instala dependência do Telegram
pip install python-telegram-bot

# Define o token (Linux/Mac)
export TELEGRAM_TOKEN="123456:ABC-DEF... o teu token"

# Windows (PowerShell)
# $env:TELEGRAM_TOKEN="123456:ABC..."

# Corre o bot
python telegram_bot.py
```

Se aparecer `✅ Bot online!`, está a funcionar!

## Passo 3 - Testar no Telegram
Vai no Telegram, procura o teu bot `@teunome_quiz_bot` e manda:

- `/start` -> mostra botões
- Clica em `🎲 Quiz Aleatório` -> demora 2 min e recebes vídeo MP4
- `/custom Ter dinheiro infinito | Poder voar | 70% | 30%`

## Passo 4 - Canal Automático (opcional, mas recomendado)
Queres que o bot poste sozinho no teu canal 3x por dia?

1. Cria um canal no Telegram: `Criar Canal` -> nome `Would You Rather Viral`
2. Adiciona o teu bot como **Administrador** no canal
3. Pega o ID do canal:
   - Se for público: `@nomedocanal`
   - Se for privado: vai no canal, encaminha uma mensagem para @userinfobot, ele dá o ID tipo `-1001234567890`

4. Corre com canal:
```bash
export TELEGRAM_TOKEN="teu_token"
export CANAL_ID="@nomedocanal"  # ou -100...
python telegram_bot.py
```

Agora ele vai postar automaticamente a cada 8 horas!

Comando manual para postar agora:
```
/postar_canal
```

## Passo 5 - Deixar Online 24/7 (para o canal não parar quando desligas o PC)

### Opção A - Grátis (Railway.app)
1. Cria conta em railway.app
2. New Project -> Deploy from GitHub (faz upload do quizfactory)
3. Variables -> Adiciona TELEGRAM_TOKEN e CANAL_ID
4. Deploy -> fica online grátis

### Opção B - VPS Barato (5€/mês)
- Hetzner / Contabo / Hostinger
- Instala Python, clona o projeto, corre com `tmux` ou `systemd`

Exemplo com tmux:
```bash
tmux new -s bot
export TELEGRAM_TOKEN="..."
export CANAL_ID="@..."
python telegram_bot.py
# Ctrl+B, D para sair e deixar a correr
```

### Opção C - No teu PC com Docker
```bash
docker run -d --restart always -e TELEGRAM_TOKEN="..." -e CANAL_ID="..." -v $(pwd):/app python:3.12 bash -c "cd /app && pip install -r requirements.txt && python telegram_bot.py"
```

## Troubleshooting

**`No module named 'telegram'`**
```bash
pip install python-telegram-bot
```

**Bot não responde**
- Vê se o token está certo (sem espaços)
- Vê se o bot está a correr no terminal (tem de ficar aberto)
- Manda /start de novo

**Vídeo não gera**
- Vê se tem `ffmpeg`: `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`
- Instala: `pip install imageio-ffmpeg`

**Quero mudar voz para PT-BR**
No ficheiro `telegram_bot.py`, muda:
```python
voice="pt-BR-FranciscaNeural"
```

## Monetização do Canal
- Canal público grátis com 1 vídeo/dia
- Canal VIP privado com 3 vídeos/dia + sem marca d'água: 4.99€/mês via @InviteMemberBot

Quer que eu configure o Railway para ti?
