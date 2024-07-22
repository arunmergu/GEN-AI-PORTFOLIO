import ffmpeg
import time

# Replace with your video file path
video_path = "path/to/your/video.mp4"

# Set interval duration (in seconds)
interval = 15

def extract_and_caption(video_path, start_time, end_time):
    # Capture video frame using ffmpeg
    process = (
        ffmpeg.input(video_path, ss=start_time)
        .output("frame.jpg", vframes=1)
        .run(capture_stdout=True)
    )

    # Integrate Vertex AI Video Intelligence for real-time captioning
    caption = analyze_video_frame(frame_path="frame.jpg")

    return caption

video_duration = ffmpeg.probe(video_path)["streams"][0]["duration"]
intervals = []
current_time = 0

while current_time < video_duration:
    end_time = min(current_time + interval, video_duration)
    caption = extract_and_caption(video_path, current_time, end_time)
    intervals.append((current_time, end_time, caption))
    current_time += interval

# Optional: Clear captured frames to avoid memory accumulation
# (replace with appropriate command if needed)
# os.remove("frame.jpg")
