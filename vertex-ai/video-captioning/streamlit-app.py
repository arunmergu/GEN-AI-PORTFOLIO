import streamlit as st
import uuid
import vertexai
# Import vertexai libraries
from vertexai.generative_models import GenerativeModel, Part
# from vertexai.utils import wait_for_operation

# Import Google Cloud libraries
from google.cloud import language_v1
from google.cloud import texttospeech
from google.cloud import storage


# Project and model details (update with your own)
project_id = "genai-project-429612"
model_name = "gemini-1.5-flash-001"

# Initialize Vertex AI
vertexai.init(project=project_id, location="us-central1")

# Load the generative model
model = GenerativeModel(model_name)


def translate_text(target_language, text):
    """Translates text into the target language."""
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language=target_language)
    return result["translatedText"]


def generate_response(video_file_uri, prompt, target_language):
    """Generates response from video content and translates."""
    video_file = Part.from_uri(video_file_uri, mime_type="video/mp4")
    contents = [video_file, prompt]

    response = model.generate_content(contents)
    # wait_for_operation(response.operation)  # Wait for model completion

    english_text=response.text

    translated_text = translate_text(target_language, response.text)

    return translated_text,english_text


def synthesize_audio(text, language_code="en-US", ssml_gender="MALE"):
    """Synthesizes audio from text."""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender[ssml_gender]
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content


def upload_to_gcs(bucket_name, source_file, destination_blob_name):
  """Uploads a file to the specified bucket.

  Args:
    bucket_name: The name of the bucket to upload to.
    source_file: The uploaded file object from Streamlit.
    destination_blob_name: The name of the blob to create.
  """

  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)

  blob.upload_from_file(source_file)

  return f"gs://{bucket_name}/{destination_blob_name}"



def main():

    """Streamlit app to translate video content and generate audio."""
    st.title(':blue[Video Captioning, Translation & Audio Description]')
        # Center the title and apply custom CSS


    # Video file input
    uploaded_file = st.file_uploader("Upload a video")
    st.markdown("""
        <style>
        .stButton > button {
            background-color: #007bff;  /* Blue color */
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Language selection
    supported_languages = ["en-US", "es-ES", "fr-FR", "zh-CN","hi-IN",'te-IN']  # Update with supported languages
    target_language = st.selectbox("Select Caption Language", supported_languages)

    # Audio language selection
    audio_languages = ["en-US", "es-ES", "fr-FR", "zh-CN"]  # Update with supported languages
    audio_language = st.selectbox("Select Audio Language", audio_languages)

    # Generate button
    if st.button("Generate"):
        st.markdown("""
        <style>
        .stButton > button {
            background-color: #007bff;  /* Blue color */
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        flag=False
        if uploaded_file is None:
            st.error("Please upload a video file first.")
        elif not uploaded_file.name.endswith(".mp4"):
            st.error("Please upload an MP4 video file.")
        else:
        # if uploaded_file is not None:
            file_name=uploaded_file.name
            print(file_name)
            destination_blob_name = file_name  # Assuming MP4 format

            # Upload the video to Cloud Storage
            bucket_name = "cloud-videos"  # Replace with your bucket name
            video_file_uri = upload_to_gcs(bucket_name, uploaded_file, destination_blob_name)
            flag=True
            

        if flag:
            prompt = "What is happening in the video?"
            translated_text,english_text = generate_response(video_file_uri, prompt, target_language)

            st.write(f"English Caption (en-US):")
            st.write(english_text)

            st.write(f"Translated Caption ({target_language}):")
            st.write(translated_text)

            audio_content = synthesize_audio(translated_text, language_code=audio_language)
            st.audio(audio_content, format="audio/mpeg")


if __name__ == "__main__":
    main()
