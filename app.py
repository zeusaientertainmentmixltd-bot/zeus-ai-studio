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
        prompt = data.get("prompt", "A cinematic trailer for a high-tech media empire.")
        voice = data.get("voice", "alloy")
        aspect = data.get("aspect", "16:9")
        
        # Determine dimensions based on aspect ratio selection
        if aspect == "9:16":
            width, height = 720, 1280
        else:
            width, height = 1280, 720

        # 1. Generate Multi-Scene Script via OpenAI GPT-4o
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are the Executive Producer for ZEUS AI ENTERTAINMENT MIX LIMITED. Generate a dynamic 3-scene cinematic narration script structured neatly."},
                {"role": "user", "content": f"Create an engaging script based on this concept: {prompt}"}
            ]
        )
        script_text = completion.choices[0].message.content

        # 2. Generate Narration Audio via OpenAI TTS
        audio_path = "static/audio/narration.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script_text
        )
        response.stream_to_file(audio_path)

        # 3. Render Video via MoviePy
        output_video_path = "static/renders/output.mp4"
        
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # Background styling
        bg_clip = ColorClip(size=(width, height), color=(15, 20, 30), duration=duration)
        
        try:
            txt_clip = TextClip(script_text, fontsize=28, color='white', size=(width - 100, None), method='caption')
            txt_clip = txt_clip.set_duration(duration).set_position('center')
            video = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
        except Exception:
            video = bg_clip.set_audio(audio_clip)

        video.write_videofile(output_video_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
        
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
