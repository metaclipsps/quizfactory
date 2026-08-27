#!/usr/bin/env python3
"""
app_gradio.py - Interface web com layout para gerar quizzes sem terminal
Corre: python app_gradio.py
Abre no browser: http://localhost:7860
"""
import gradio as gr
import json
import tempfile
from pathlib import Path
from make_quiz import gerar_video_quiz, create_background, create_wrapped_text_image, create_vs_circle_image, create_percent_image, create_round_label_image, W, H, HALF_H
from PIL import Image
import os

# Preview rápido sem gerar vídeo
def gerar_preview(a, b, pa, pb):
    from preview import generate_preview
    out = tempfile.mktemp(suffix=".png")
    # usa função do preview.py mas com fonte gigante
    bg = create_background()
    text_a = create_wrapped_text_image(a, max_width_px=980, font_size=125, color=(255,255,255), stroke_width=14, stroke_color=(0,0,0), bold=True)
    text_b = create_wrapped_text_image(b, max_width_px=980, font_size=125, color=(255,255,255), stroke_width=14, stroke_color=(0,0,0), bold=True)
    bg_copy = bg.copy()
    y_a = (HALF_H - text_a.height)//2 - 40
    bg_copy.paste(text_a, ((W - text_a.width)//2, y_a), text_a)
    y_b = HALF_H + (HALF_H - text_b.height)//2 + 20
    bg_copy.paste(text_b, ((W - text_b.width)//2, y_b), text_b)
    vs = create_vs_circle_image("VS", size=210)
    bg_copy.paste(vs, ((W - vs.width)//2, HALF_H-105), vs)
    pa_img = create_percent_image(pa, bg_color=(255,255,255), text_color=(255,59,48))
    pb_img = create_percent_image(pb, bg_color=(255,255,255), text_color=(0,122,255))
    bg_copy.paste(pa_img, ((W - pa_img.width)//2, HALF_H-220), pa_img)
    bg_copy.paste(pb_img, ((W - pb_img.width)//2, HALF_H+70), pb_img)
    bg_copy.save(out)
    return out

def gerar_video_completo(json_text, voice):
    try:
        # Validar JSON
        data = json.loads(json_text)
        # Salvar temp json
        tmp_json = tempfile.mktemp(suffix=".json")
        with open(tmp_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        tmp_mp4 = tempfile.mktemp(suffix=".mp4")
        gerar_video_quiz(tmp_json, tmp_mp4, voice=voice, temp_dir="temp_audio")
        return tmp_mp4, "✅ Vídeo gerado com sucesso!"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ Erro: {e}"

# Exemplos prontos
exemplo_json = """[
  {
    "option_a": "Have unlimited money",
    "option_b": "Be able to teleport anywhere",
    "percent_a": "72%",
    "percent_b": "28%"
  },
  {
    "option_a": "Live in a luxury mansion alone",
    "option_b": "Live in a cozy van with your soulmate",
    "percent_a": "38%",
    "percent_b": "62%"
  }
]"""

with gr.Blocks(title="QuizFactory - Red vs Blue Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 QuizFactory - Gerador de Vídeos Would You Rather")
    gr.Markdown("Cria vídeos virais TikTok Red vs Blue sem usar terminal. Escreve as perguntas e gera!")

    with gr.Tab("Preview Rápido (Imagem)"):
        with gr.Row():
            with gr.Column():
                opt_a = gr.Textbox(label="Opção A (Vermelho - Topo)", value="Have unlimited money", lines=2)
                opt_b = gr.Textbox(label="Opção B (Azul - Fundo)", value="Be able to teleport anywhere", lines=2)
                perc_a = gr.Textbox(label="Percentagem A", value="72%")
                perc_b = gr.Textbox(label="Percentagem B", value="28%")
                btn_preview = gr.Button("👁️ Gerar Preview", variant="secondary")
            with gr.Column():
                img_preview = gr.Image(label="Preview 1080x1920", type="filepath")
        btn_preview.click(gerar_preview, inputs=[opt_a, opt_b, perc_a, perc_b], outputs=[img_preview])

    with gr.Tab("Vídeo Completo"):
        with gr.Row():
            with gr.Column():
                json_input = gr.Textbox(label="JSON das perguntas (4-5 rondas recomendado)", value=exemplo_json, lines=15)
                voice_dd = gr.Dropdown(
                    choices=["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-US-JennyNeural", "pt-BR-FranciscaNeural"],
                    value="en-US-AriaNeural",
                    label="Voz IA"
                )
                btn_video = gr.Button("🎬 Gerar Vídeo MP4 (demora 2-6 min)", variant="primary")
            with gr.Column():
                video_out = gr.Video(label="Vídeo Gerado 1080x1920")
                status = gr.Textbox(label="Status")
        btn_video.click(gerar_video_completo, inputs=[json_input, voice_dd], outputs=[video_out, status])

    gr.Markdown("### 💡 Dicas:\n- Usa percentagens tipo 49% vs 51% para gerar mais comentários\n- 4 rondas = ~45 segundos (ideal TikTok)\n- Voz AriaNeural é a mais viral")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
