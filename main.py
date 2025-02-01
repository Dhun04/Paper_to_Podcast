import openai
import requests
import os
import fitz  # PyMuPDF for PDF text extraction
import streamlit as st
import io

# API Keys (Replace with your valid keys)
openai.api_key = "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"
ELEVENLABS_API_KEY = "sk_797f1937fdd142c982b3a58f630c138963073958b6053f50"
ELEVENLABS_VOICES = {
    "Alice": "9BWtsMINqrJLrRacOk9x",  
    "Bob": "pqHfZKP75CvOlQylNhV4"
}

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Streamlit UI
st.title("📜 Research Paper to Podcast 🎙️")
st.write("Upload a research paper (PDF) and get an AI-generated podcast.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        # Open the uploaded PDF file as a BytesIO object
        pdf_stream = io.BytesIO(pdf_file.read())
        
        # Use fitz.open() with the BytesIO stream
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        # Extract text from each page of the PDF
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        st.error(f"❌ Error extracting text: {e}")
    return text

def text_to_speech_elevenlabs(text, speaker="Alice"):
    """Converts text to speech using ElevenLabs API."""
    if not text.strip():
        st.error("❌ The extracted text is empty or invalid.")
        return None
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICES[speaker]}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "voice_settings": {"stability": 0.7, "similarity_boost": 0.8}}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"❌ Error from ElevenLabs API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Exception occurred while calling ElevenLabs API: {e}")
        return None

def split_text_into_chunks(text, max_chunk_size=1000):
    """Splits the text into chunks to avoid API limitations."""
    chunks = []
    for i in range(0, len(text), max_chunk_size):
        chunks.append(text[i:i + max_chunk_size])
    return chunks

if uploaded_file:
    st.success("✅ File uploaded successfully!")

    # Extract text from PDF
    st.write("🔍 Extracting text...")
    paper_text = extract_text_from_pdf(uploaded_file)

    if paper_text:
        st.success("✅ Text extracted successfully!")
        st.write("📝 Extracted Text Preview (first 500 characters):")
        st.text(paper_text[:500])  # Show a preview of the text to verify

        # Split the text into smaller chunks
        st.write("💬 Splitting text into chunks...")
        text_chunks = split_text_into_chunks(paper_text)
        
        # Initialize audio variable to hold the final audio
        final_audio = b""

        for idx, chunk in enumerate(text_chunks):
            st.write(f"🎙️ Generating podcast for chunk {idx+1}...")
            podcast_audio = text_to_speech_elevenlabs(chunk)

            if podcast_audio:
                final_audio += podcast_audio  # Combine the audio chunks

        if final_audio:
            audio_path = "output/research_paper_podcast.mp3"
            with open(audio_path, "wb") as f:
                f.write(final_audio)

            st.success("✅ Podcast generated successfully!")

            # Provide download link
            with open(audio_path, "rb") as f:
                st.download_button("⬇️ Download Podcast", f, file_name="Research_Paper_Podcast.mp3", mime="audio/mpeg")

        else:
            st.error("❌ Error generating audio!")
