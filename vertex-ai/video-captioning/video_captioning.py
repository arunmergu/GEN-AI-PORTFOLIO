
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import language_v1
from google.cloud import texttospeech

# TODO(developer): Update and un-comment below lines
project_id = "genai-project-429612"

vertexai.init(project=project_id, location="us-central1")

model = GenerativeModel("gemini-1.5-flash-001")

prompt = """
what the video and tell me what is happening 
"""

video_file_uri = "gs://cloud-videos/16726088-uhd_2160_3840_60fps.mp4"

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

    # print("Text: {}".format(result["input"]))
    # print("Translation: {}".format(result["translatedText"]))
    # print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result["translatedText"]


def generate_response(video_file_uri,prompt,target_language):
    
    video_file = Part.from_uri(video_file_uri, mime_type="video/mp4")

    contents = [video_file, prompt]

    response = model.generate_content(contents)

    print(response.text)

    translated_repsonse=translate_text(target_language,response.text)

    return translated_repsonse

# import cv2

# # ... existing code for generate_response function

# def overlay_caption(video_file_uri, caption):
#     # Read video capture object
#     cap = cv2.VideoCapture(video_file_uri)

#     # Define text properties (font, color, position)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = 1
#     color = (255, 255, 255)  # White text
#     text_pos = (50, 50)  # Adjust position as needed

#     # Define video writer for output
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Adjust codec if needed
#     out = cv2.VideoWriter("output.avi", fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Add caption text to the frame
#         cv2.putText(frame, caption, text_pos, font, font_scale, color, thickness=2, lineType=cv2.LINE_AA)

#         # Write processed frame to output video
#         out.write(frame)

#     # Release resources
#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()

# # Call functions
caption = generate_response(video_file_uri, prompt,'zh-CN')

print(caption)

from google.cloud import texttospeech

# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text=caption)

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
language_code="zh-CN",
    ssml_gender=texttospeech.SsmlVoiceGender.MALE)



# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# The response's audio_content is binary.
with open("output.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')
# overlay_caption(video_file_uri, caption)

# print("Output video with caption created!")




