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
    try:
        data = request.json or {}
        prompt = data.get("prompt", "A dramatic cinematic intro about artificial intelligence.")
        
        # 1. Generate Script via OpenAI Chat Completion
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional film director and screenwriter for ZEUS AI ENTERTAINMENT MIX LIMITED."},
                {"role": "user", "content": f"Write a short, punchy 3-sentence narration script based on this concept: {prompt}"}
            ]
        )
        script_text = completion.choices[0].message.content

        # 2. Generate Audio via OpenAI TTS
        audio_path = "static/audio/narration.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=script_text
        )
        response.stream_to_file(audio_path)

        # 3. Generate Video via MoviePy
        output_video_path = "static/renders/output.mp4"
        
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # Create background clip
        bg_clip = ColorClip(size=(1280, 720), color=(10, 10, 30), duration=duration)
        
        # Create text clip with fallback handling
        try:
            txt_clip = TextClip(script_text, fontsize=32, color='white', size=(1100, None), method='caption')
            txt_clip = txt_clip.set_duration(duration).set_position('center')
            video = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
        except Exception:
            video = bg_clip.set_audio(audio_clip)

        video.write_videofile(output_video_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
        
        # Close clips to free resources
        audio_clip.close()
        video.close()

        return jsonify({
            "status": "success",
            "script": script_text,
            "video_url": "/static/renders/output.mp4"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
