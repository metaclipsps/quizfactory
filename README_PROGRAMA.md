# Como transformar o sistema num PROGRAMA / BOT

Sim, dá para transformar em 3 formatos. Já criei os 3 protótipos para ti na pasta `quizfactory/`:

## 1. 🖥️ Programa com Janela (Desktop App)
**Ficheiro:** `app_desktop.py`

- Janela com 4 linhas de inputs (Opção A, Opção B, %)
- Botão GERAR VÍDEO
- Escolhe onde salvar o MP4

```bash
pip install customtkinter
python app_desktop.py
```

Para criar .exe instalável:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "quizzes:quizzes" app_desktop.py
# Gera dist/app_desktop.exe
```

**Vantagem:** Usas offline, sem terminal, podes vender.

---

## 2. 🌐 Site / Web App (Interface no Browser)
**Ficheiro:** `app_gradio.py`

- Abre no browser em http://localhost:7860
- Tem aba de Preview rápido (imagem) e Vídeo completo
- Podes hospedar no HuggingFace Spaces de graça

```bash
pip install gradio
python app_gradio.py
```

Para deploy online:
- Cria conta em huggingface.co
- Cria Space -> Gradio -> faz upload dos ficheiros
- Fica online 24/7 com link para partilhar

**Vantagem:** Qualquer pessoa usa sem instalar nada, podes pôr paywall.

---

## 3. 🤖 Bot do Telegram (Canal)
**Ficheiro:** `telegram_bot.py`

- Pessoas mandam /quiz no Telegram e recebem o vídeo pronto
- Podes criar um canal onde o bot posta 3x por dia automaticamente

Passos:
1. Vai no Telegram, fala com @BotFather
2. /newbot -> nome: QuizFactoryBot -> pega o TOKEN tipo `123456:ABC...`
3. No teu servidor/VPS:
```bash
pip install python-telegram-bot
export TELEGRAM_TOKEN="teu_token_aqui"
python telegram_bot.py
```

Comandos que já programei:
- `/start` - boas vindas
- `/quiz` - gera quiz aleatório e envia MP4
- `/custom Ter dinheiro | Poder voar | 70% | 30%` - custom

Para canal automático (postar sozinho):
```python
# Adiciona no bot um job que corre a cada 8h
from telegram.ext import JobQueue
# ... posta vídeo no canal @teucanal
```

**Vantagem:** Viraliza sozinho, podes cobrar subscrição no canal privado.

---

## Qual escolher?

| Formato | Dificuldade | Custo | Monetização |
|---------|-------------|-------|-------------|
| Desktop .exe | Fácil | 0€ | Vender licença 20€ |
| Site Gradio | Média | 0€ (HF) | Anúncios / Paywall |
| Bot Telegram | Média | 5€/mês VPS | Canal VIP 5€/mês |

**Recomendação:** Começa com o **Gradio** (5 min para ficar online) + **Telegram** para distribuição.

Queres que eu:
1. Hospede o Gradio para ti?
2. Configure o bot com o teu token?
3. Gere o .exe?

Diz-me qual preferes e eu monto.
