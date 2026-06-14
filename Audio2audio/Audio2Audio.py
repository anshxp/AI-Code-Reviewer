import gradio as gr
from openai import OpenAI
import os
import time

# =========================
# CONFIG
# =========================

API_KEY = os.getenv("API_KEY")

client = OpenAI(
    api_key="sk-EF5sUlx6Li_oUp0N5E6R5Q",
    base_url="https://apidev.navigatelabsai.com"
)

# =========================
# MEMORY
# =========================

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI voice assistant. "
            "Keep responses short, natural, and conversational."
        )
    }
]

# =========================
# MAIN FUNCTION
# =========================

def audio_chat(audio_file):

    global conversation_history

    try:

        if audio_file is None:
            return "No audio uploaded.", None

        # ======================
        # TRANSCRIBE AUDIO
        # ======================

        with open(audio_file, "rb") as f:

            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        user_text = transcription.text.strip()

        if not user_text:
            return "Could not detect speech.", None

        # Save user message
        conversation_history.append({
            "role": "user",
            "content": user_text
        })

        # ======================
        # LIMIT MEMORY
        # ======================

        # Keep only recent messages
        if len(conversation_history) > 8:
            conversation_history = (
                [conversation_history[0]] +
                conversation_history[-7:]
            )

        # ======================
        # CHAT RESPONSE
        # ======================

        recent_history = conversation_history

        chat_response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=recent_history,
            timeout=40,
            max_tokens=150
        )

        ai_text = chat_response.choices[0].message.content.strip()

        # Save assistant response
        conversation_history.append({
            "role": "assistant",
            "content": ai_text
        })

        # ======================
        # TEXT TO SPEECH
        # ======================

        tts_response = client.audio.speech.create(
            model="gemini-2.5-flash-tts",
            voice="alloy",
            input=ai_text
        )

        output_path = "response.mp3"

        with open(output_path, "wb") as f:
            f.write(tts_response.content)

        return ai_text, output_path

    except Exception as e:

        error_msg = str(e)

        # Rate limit handling
        if "429" in error_msg or "Rate Limit" in error_msg:
            return (
                "Rate limit exceeded. Please wait a few seconds and try again.",
                None
            )

        return f"Error: {error_msg}", None

# =========================
# UI
# =========================

with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # AI Voice Assistant

    Speak with AI using voice.

    Features:
    - Speech to Text
    - AI Chat
    - Text to Speech
    """)

    audio_input = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Speak Here"
    )

    text_output = gr.Textbox(
        label="AI Response",
        lines=4
    )

    audio_output = gr.Audio(
        label="AI Voice Response",
        type="filepath",
        autoplay=True
    )

    submit_btn = gr.Button("Generate Response")

    submit_btn.click(
        fn=audio_chat,
        inputs=audio_input,
        outputs=[text_output, audio_output]
    )

# =========================
# LAUNCH
# =========================

demo.queue().launch()
