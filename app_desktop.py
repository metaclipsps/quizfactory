#!/usr/bin/env python3
"""
app_desktop.py - Programa com janela (GUI) usando CustomTkinter
pip install customtkinter
python app_desktop.py
"""
import os
import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    print("Instala: pip install customtkinter")

from make_quiz import gerar_video_quiz

if HAS_CTK:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    class QuizFactoryApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("QuizFactory - Red vs Blue Generator")
            self.geometry("900x700")

            # Título
            self.label_title = ctk.CTkLabel(self, text="🎬 QuizFactory - Would You Rather", font=("Arial", 22, "bold"))
            self.label_title.pack(pady=15)

            # Frame inputs
            self.frame_inputs = ctk.CTkFrame(self)
            self.frame_inputs.pack(pady=10, padx=20, fill="x")

            # 4 rondas
            self.entries = []
            for i in range(4):
                row = ctk.CTkFrame(self.frame_inputs)
                row.pack(pady=5, fill="x", padx=10)

                lbl = ctk.CTkLabel(row, text=f"Ronda {i+1}", width=80)
                lbl.pack(side="left", padx=5)

                entry_a = ctk.CTkEntry(row, placeholder_text=f"Opção A (Vermelho) - ex: Have unlimited money", width=250)
                entry_a.pack(side="left", padx=5, expand=True, fill="x")

                entry_b = ctk.CTkEntry(row, placeholder_text=f"Opção B (Azul) - ex: Be able to teleport", width=250)
                entry_b.pack(side="left", padx=5, expand=True, fill="x")

                entry_pa = ctk.CTkEntry(row, placeholder_text="72%", width=70)
                entry_pa.pack(side="left", padx=5)
                entry_pb = ctk.CTkEntry(row, placeholder_text="28%", width=70)
                entry_pb.pack(side="left", padx=5)

                self.entries.append((entry_a, entry_b, entry_pa, entry_pb))

            # Preencher com exemplos
            exemplos = [
                ("Have unlimited money", "Be able to teleport anywhere", "72%", "28%"),
                ("Always know when someone is lying", "Get away with any lie", "54%", "46%"),
                ("Live in mansion alone", "Live in van with soulmate", "38%", "62%"),
                ("Eat favorite meal daily", "Never eat or sleep again", "49%", "51%"),
            ]
            for i, (a,b,pa,pb) in enumerate(exemplos):
                self.entries[i][0].insert(0, a)
                self.entries[i][1].insert(0, b)
                self.entries[i][2].insert(0, pa)
                self.entries[i][3].insert(0, pb)

            # Voz
            self.frame_voice = ctk.CTkFrame(self)
            self.frame_voice.pack(pady=10, fill="x", padx=20)
            self.lbl_voice = ctk.CTkLabel(self.frame_voice, text="Voz IA:")
            self.lbl_voice.pack(side="left", padx=10)
            self.voice_var = ctk.StringVar(value="en-US-AriaNeural")
            self.voice_menu = ctk.CTkOptionMenu(self.frame_voice, values=["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-US-JennyNeural"], variable=self.voice_var)
            self.voice_menu.pack(side="left", padx=10)

            # Botão gerar
            self.btn_generate = ctk.CTkButton(self, text="🎬 GERAR VÍDEO", command=self.gerar, height=50, font=("Arial", 18, "bold"))
            self.btn_generate.pack(pady=20, padx=20, fill="x")

            # Status
            self.status = ctk.CTkLabel(self, text="Pronto para gerar!", font=("Arial", 14))
            self.status.pack(pady=10)

            self.progress = ctk.CTkProgressBar(self, width=800)
            self.progress.pack(pady=5)
            self.progress.set(0)

        def gerar(self):
            # Corre em thread separada para não travar GUI
            threading.Thread(target=self._gerar_thread, daemon=True).start()

        def _gerar_thread(self):
            try:
                self.btn_generate.configure(state="disabled", text="⏳ A gerar... demora 2-6 min")
                self.status.configure(text="A gerar áudios TTS...")
                self.progress.set(0.2)

                quiz_data = []
                for entry_a, entry_b, entry_pa, entry_pb in self.entries:
                    a = entry_a.get().strip()
                    b = entry_b.get().strip()
                    pa = entry_pa.get().strip() or "50%"
                    pb = entry_pb.get().strip() or "50%"
                    if a and b:
                        quiz_data.append({"option_a": a, "option_b": b, "percent_a": pa, "percent_b": pb})

                if not quiz_data:
                    messagebox.showerror("Erro", "Preenche pelo menos 1 ronda!")
                    return

                # Salva json temp
                import tempfile
                tmp_json = tempfile.mktemp(suffix=".json")
                with open(tmp_json, 'w', encoding='utf-8') as f:
                    json.dump(quiz_data, f, indent=2)

                # Pede onde salvar
                output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")], initialfile="quiz.mp4")
                if not output_path:
                    return

                self.status.configure(text=f"A renderizar vídeo com {len(quiz_data)} rondas...")
                self.progress.set(0.5)

                gerar_video_quiz(tmp_json, output_path, voice=self.voice_var.get(), temp_dir="temp_audio")

                self.progress.set(1.0)
                self.status.configure(text=f"✅ Vídeo salvo em {output_path}")
                messagebox.showinfo("Sucesso", f"Vídeo gerado!\n{output_path}")

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.status.configure(text=f"❌ Erro: {e}")
                messagebox.showerror("Erro", str(e))
            finally:
                self.btn_generate.configure(state="normal", text="🎬 GERAR VÍDEO")

    if __name__ == "__main__":
        app = QuizFactoryApp()
        app.mainloop()
else:
    print("Instala customtkinter: pip install customtkinter")
