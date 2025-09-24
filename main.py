import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound
import tempfile
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os

# ---------------- Init ----------------
recognizer = sr.Recognizer()
listening = False

# GoogleTranslator instance
translator_instance = GoogleTranslator(source='auto', target='en')
languages_dict = translator_instance.get_supported_languages(as_dict=True)
lang_names = list(languages_dict.keys())

# ---------- Functions ----------
def play_tts(text, lang_code):
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "temp_voice.mp3")
        tts = gTTS(text=text, lang=lang_code)
        tts.save(temp_path)
        playsound(temp_path)
        os.remove(temp_path)
    except Exception as e:
        print("TTS error:", e)

def start_listening():
    global listening
    listening = True
    status_label.config(text="🎙️ Listening...", bootstyle="info")
    threading.Thread(target=listen_and_translate, daemon=True).start()

def stop_listening():
    global listening
    listening = False
    status_label.config(text="🛑 Stopped", bootstyle="danger")

def listen_and_translate():
    global listening
    while listening:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                status_label.config(text="🕑 Listening...", bootstyle="secondary")
                audio = recognizer.listen(source, timeout=5)

                src_lang_code = languages_dict[source_combo.get().lower()]
                tgt_lang_code = languages_dict[target_combo.get().lower()]

                try:
                    original_text = recognizer.recognize_google(audio, language=src_lang_code)
                except sr.UnknownValueError:
                    original_text = ""
                except sr.RequestError:
                    original_text = "[Network error]"

                original_box.delete(0, "end")
                original_box.insert(0, original_text)

                if original_text.strip():
                    try:
                        translator = GoogleTranslator(source=src_lang_code, target=tgt_lang_code)
                        translated = translator.translate(original_text)
                        translated_box.delete(0, "end")
                        translated_box.insert(0, translated)

                        play_tts(translated, tgt_lang_code)
                    except Exception as e:
                        translated_box.delete(0, "end")
                        translated_box.insert(0, f"⚠️ Error: {e}")
                else:
                    translated_box.delete(0, "end")
                    translated_box.insert(0, "😅 Didn't catch anything.")

        except Exception as e:
            status_label.config(text=f"❌ Error: {e}", bootstyle="danger")

# ---------- Autocomplete Function with Dropdown ----------
def filter_combobox(event, combobox, all_values):
    typed = combobox.get().lower()
    if typed == "":
        combobox['values'] = all_values
    else:
        filtered = [val for val in all_values if val.lower().startswith(typed)]
        combobox['values'] = filtered
        if filtered:
            combobox.event_generate('<Down>')  # Open dropdown automatically

# ---------------- Tkinter UI ----------------
app = ttk.Window(themename="superhero")
app.title("🌍 Universal Voice Translator")
app.geometry("1000x700")
app.minsize(900, 600)

# Title فوق كل شيء
title_label = ttk.Label(
    app,
    text="🌍 Universal Voice Translator",
    font=("DejaVu Sans", 24, "bold"),  # حجم أصغر
    bootstyle="info"
)
title_label.pack(pady=(10, 15))  # قلل المسافة بعد العنوان

# Central frame (مركزي)
main_frame = ttk.Frame(app, padding=(40, 20))
main_frame.pack(expand=True)

# Languages frame
lang_frame = ttk.Frame(main_frame)
lang_frame.pack(pady=10)

ttk.Label(lang_frame, text="🗣 Speak in:", font=("Helvetica", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
source_combo = ttk.Combobox(lang_frame, values=lang_names, width=30, font=("Helvetica", 14))
source_combo.set("german")
source_combo.grid(row=0, column=1, padx=10, pady=10)
source_combo.bind("<KeyRelease>", lambda e: filter_combobox(e, source_combo, lang_names))

ttk.Label(lang_frame, text="🌍 Translate to:", font=("Helvetica", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
target_combo = ttk.Combobox(lang_frame, values=lang_names, width=30, font=("Helvetica", 14))
target_combo.set("french")
target_combo.grid(row=1, column=1, padx=10, pady=10)
target_combo.bind("<KeyRelease>", lambda e: filter_combobox(e, target_combo, lang_names))

# Text boxes frame
text_frame = ttk.Frame(main_frame)
text_frame.pack(pady=20)

ttk.Label(text_frame, text="🔊 Original:", font=("Helvetica", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
original_box = ttk.Entry(text_frame, width=55, font=("Helvetica", 14), bootstyle="info")
original_box.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(text_frame, text="✅ Translated:", font=("Helvetica", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
translated_box = ttk.Entry(text_frame, width=55, font=("Helvetica", 14), bootstyle="info")
translated_box.grid(row=1, column=1, padx=10, pady=10)

# Status
status_label = ttk.Label(main_frame, text="🔔 Ready", bootstyle="secondary", font=("Helvetica", 14))
status_label.pack(pady=15)

# Buttons
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(pady=15)

start_btn = ttk.Button(
    btn_frame,
    text="▶ Start Listening",
    bootstyle="success-outline",
    width=25,
    padding=(10, 10),
    command=start_listening
)
start_btn.grid(row=0, column=0, padx=20, pady=10)

stop_btn = ttk.Button(
    btn_frame,
    text="⏹ Stop",
    bootstyle="danger-outline",
    width=25,
    padding=(10, 10),
    command=stop_listening
)
stop_btn.grid(row=0, column=1, padx=20, pady=10)

app.mainloop()
