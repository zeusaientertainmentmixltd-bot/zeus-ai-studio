import os
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from moviepy.editor import ColorClip, TextClip, AudioFileClip, CompositeVideoClip

app = Flask(__name__)


# Initialize the OpenAI client securely using environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Ensure storage directories exist
os.makedirs("static/audio", exist_ok=True)
os.makedirs("static/renders", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_movie_pipeline():
    data = request.json or {}
    series_title = data.get("title", "Cain and Abel: Lagos Nights")
    genre = data.get("genre", "Cyberpunk Thriller")
    duration_str = data.get("duration", "66 Seconds")
    prompt = data.get("prompt", "Two rival fixers meet under neon lights in Adeje.")

    # Extract target duration in seconds (default to 10s for rapid test rendering if needed)
    target_duration = 10 
    if "66" in duration_str:
        target_duration = 15  # Scaled for timeline rendering demo

    system_prompt = (
        f"You are the elite AI cinematic director for ZEUS AI ENTERTAINMENT MIX LIMITED. "
        f"Generate a structured JSON response for a micro-drama titled '{series_title}' "
        f"in the genre '{genre}'. Return strictly a JSON object with two keys: "
        f"'visual_caption' (a short punchy text overlay for the video screen) and "
        f"'voiceover_text' (the clean dialogue or narration script to be spoken)."
    )

    try:
        # Step 1: Intelligent Script Generation via GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        content = json.loads(response.choices[0].message.content)
        visual_caption = content.get("visual_caption", series_title)
        vo_text = content.get("voiceover_text", prompt)

        # Step 2: Automated Text-to-Speech (TTS) Voiceover Synthesis
        audio_filename = "movie_voiceover.mp3"
        audio_filepath = os.path.join("static/audio", audio_filename)
        
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=vo_text
        )
        speech_response.stream_to_file(audio_filepath)

        # Step 3: InVideo-Style Timeline Compilation & Video Rendering (MoviePy Engine)
        output_video_filename = "final_production.mp4"
        output_video_path = os.path.join("static/renders", output_video_filename)

        # Create a styled background canvas (Cinematic Dark Theme)
        bg_clip = ColorClip(size=(1280, 720), color=[15, 15, 25], duration=target_duration)

        # Generate dynamic text overlay for the video scene
        txt_clip = TextClip(
            visual_caption, 
            fontsize=48, 
            color='white', 
            font='Arial-Bold',
            size=(1100, None),
            method='caption'
        ).set_position('center').set_duration(target_duration)

        # Attach and synchronize the synthesized voiceover audio track
        audio_clip = AudioFileClip(audio_filepath)
        
        # Composite visual layers together
        video_composite = CompositeVideoClip([bg_clip, txt_clip])
        final_video = video_composite.set_audio(audio_clip)

        # Render the final MP4 file out to disk
        final_video.write_videofile(
            output_video_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            logger=None
        )

        return jsonify({
            "status": "success",
            "studio": "ZEUS AI ENTERTAINMENT MIX LIMITED",
            "project": series_title,
            "message": "Full InVideo-standard timeline rendered successfully!",
            "video_url": f"/static/renders/{output_video_filename}",
            "audio_track": f"/static/audio/{audio_filename}",
            "visual_script": visual_caption
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/static/renders/<path:filename>")
def serve_renders(filename):
    return send_from_directory("static/renders", filename)

@app.route("/static/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static/audio", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
