import gradio as gr
from openai import OpenAI
import os

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

        print("Received audio:", audio_file)

        # ======================
        # CHECK AUDIO
        # ======================

        if audio_file is None:
            return "No audio recorded.", None

        if not os.path.exists(audio_file):
            return "Audio file not found.", None

        # ======================
        # TRANSCRIBE AUDIO
        # ======================

        with open(audio_file, "rb") as f:

            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        user_text = transcription.text.strip()

        print("User said:", user_text)

        if not user_text:
            return "Could not detect speech.", None

        # ======================
        # SAVE USER MESSAGE
        # ======================

        conversation_history.append({
            "role": "user",
            "content": user_text
        })

        # ======================
        # LIMIT MEMORY
        # ======================

        if len(conversation_history) > 8:
            conversation_history = (
                [conversation_history[0]] +
                conversation_history[-7:]
            )

        # ======================
        # CHAT RESPONSE
        # ======================

        chat_response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=conversation_history,
            max_tokens=150,
            timeout=40
        )

        ai_text = chat_response.choices[0].message.content.strip()

        print("AI Response:", ai_text)

        # ======================
        # SAVE AI RESPONSE
        # ======================

        conversation_history.append({
            "role": "assistant",
            "content": ai_text
        })

        # ======================
        # TEXT TO SPEECH
        # ======================

        output_path = "response.mp3"

        speech_response = client.audio.speech.create(
            model="gemini-2.5-flash-tts",
            voice="alloy",
            input=ai_text
        )

        with open(output_path, "wb") as f:
            f.write(speech_response.content)

        # ======================
        # RETURN OUTPUTS
        # ======================

        return ai_text, output_path

    except Exception as e:

        print("ERROR:", str(e))

        error_msg = str(e)

        if "429" in error_msg:
            return (
                "Rate limit exceeded. Please wait and try again.",
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
        format="wav",
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

demo.queue().launch(
    share=True,
    ssr_mode=False
)
