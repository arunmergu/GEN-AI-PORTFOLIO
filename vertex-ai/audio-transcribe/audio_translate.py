import vertexai
import os

from vertexai.generative_models import GenerativeModel, Part

# TODO(developer): Update and un-comment below line
project_id = "genai-project-429612"

vertexai.init(project=project_id, location="us-central1")

vision_model = GenerativeModel("gemini-1.5-flash-001")

# Generate text
response = vision_model.generate_content(
    [
        Part.from_uri(
            "gs://cloud-samples-data/video/animals.mp4", mime_type="video/mp4"
        ),
        "What is in the video?",
    ]
)
print(response.text)

def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result["translatedText"]

translate_text('te',response.text)