# Setup isolado - QuizFactory vs ShortsFactory

## ESTRUTURA RECOMENDADA NA TUA MÁQUINA:

```
~/projects/
├── shortsfactory/      <- TEU PROJETO ATUAL DE HISTÓRIAS (não mexer)
│   ├── .venv/          (venv das histórias: whisper, etc)
│   ├── make_short.py
│   ├── batch.py
│   ├── assets/
│   └── ...
│
└── quizfactory/        <- NOVO PROJETO SÓ DE QUIZ (este que criei)
    ├── .venv/          (venv separado só para quiz)
    ├── make_quiz.py
    ├── batch.py
    ├── generate_quizzes.py
    ├── preview.py
    ├── quizzes/
    ├── output/
    └── requirements.txt
```

## PORQUÊ SEPARAR?

1.  **Dependências diferentes:**
    - shortsfactory: whisper, openai, edge-tts, moviepy
    - quizfactory: só edge-tts, moviepy, Pillow (mais leve)

2.  **Não partes o que já funciona** - se o quiz der erro, as histórias continuam a gerar

3.  **Podes ter versões de moviepy diferentes** se precisares (1.0.3 para quiz, 2.x para histórias)

4.  **Mais fácil para fazer backup / enviar para VPS**
