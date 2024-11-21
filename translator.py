import os
import streamlit as st
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound

# Load environment variables from .env file
load_dotenv()

# Initialize global variables for Azure SDK configurations
speech_config = None
translation_config = None

# Initialize the Azure Speech SDK
def initialize_azure():
    global speech_config
    global translation_config

    ai_key = os.getenv('SPEECH_KEY')
    ai_region = os.getenv('SPEECH_REGION')

    # Configure translation
    translation_config = speech_sdk.translation.SpeechTranslationConfig(ai_key, ai_region)
    translation_config.speech_recognition_language = 'en-US'
    translation_config.add_target_language('fr')
    translation_config.add_target_language('es')
    translation_config.add_target_language('hi')

    # Configure speech synthesis
    speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
    print('Ready to translate from', translation_config.speech_recognition_language)

# Function to translate speech to text
def translate_speech(target_language):
    translation = ''
    try:
        # Configure audio input
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
        st.write("Speak now...")

        result = translator.recognize_once_async().get()
        st.write(f'Translating: "{result.text}"')

        translation = result.translations[target_language]
        st.write(f"Translated: {translation}")

        # Play audio of translated text
        voices = {
            "fr": "fr-FR-HenriNeural",
            "es": "es-ES-ElviraNeural",
            "hi": "hi-IN-MadhurNeural"
        }

        speech_config.speech_synthesis_voice_name = voices.get(target_language)
        speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
        speak = speech_synthesizer.speak_text_async(translation).get()

        if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
            st.write(speak.reason)

        return translation

    except Exception as ex:
        st.write(ex)
        return "Error during translation"

# Streamlit UI with a sidebar, file uploader, and buttons
def create_ui():
    # Sidebar for app navigation
    st.sidebar.title("Speech Translator")
    st.sidebar.write("Select a language to translate into:")
    
    # Language selection
    target_language = st.sidebar.radio("Select Target Language", ('fr', 'es', 'hi'))
    st.sidebar.markdown("---")

    # Upload audio file
    uploaded_audio = st.sidebar.file_uploader("Upload an Audio File (Optional)", type=["wav", "mp3"])

    # Display welcome message and instructions
    st.title("Speech Translator Application")
    st.subheader("Translate your speech in real time!")
    st.write("Click the button below to start translation from English to your chosen language.")

    # Button for translating speech
    if st.button('Start Translation'):
        if uploaded_audio is not None:
            st.write(f"Audio uploaded: {uploaded_audio.name}")
            # Logic to handle uploaded audio file for translation can be added here
            st.write("Audio translation feature coming soon...")
        else:
            # Call the Azure translation function if no audio is uploaded
            translation = translate_speech(target_language)
            st.write("Translation: ", translation)

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Developed by Yassine Aboulanouar</p>", unsafe_allow_html=True)

# Main function to run everything
def main():
    initialize_azure()
    create_ui()

if __name__ == "__main__":
    main()
