from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "zeus_ai_secret_key_change_in_production"

# ==============================================================================
# DATABASE INITIALIZATION (SQLite for Users & Credits)
# ==============================================================================
def init_db():
    conn = sqlite3.connect('zeus_studio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            credits INTEGER DEFAULT 30,
            is_subscribed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==============================================================================
# COMMERCIAL PLATFORM HTML TEMPLATE
# ==============================================================================
PLATFORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZEUS AI ENTERTAINMENT MIX LIMITED — SaaS Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .header-bar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 20px; }
        .badge { background: #0284c7; color: #fff; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #cbd5e1; }
        select, textarea { width: 100%; padding: 12px; margin-bottom: 20px; background: #0f172a; border: 1px solid #475569; border-radius: 6px; color: #fff; font-size: 14px; box-sizing: border-box; }
        textarea { height: 120px; resize: vertical; }
        button { background: #0284c7; color: white; border: none; padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .pay-box { background: #334155; padding: 20px; border-radius: 8px; text-align: center; margin-top: 20px; }
        .pay-btn { background: #10b981; width: auto; display: inline-block; padding: 10px 25px; text-decoration: none; color: #fff; border-radius: 6px; margin-top: 10px; font-weight: bold; }
        #output { margin-top: 25px; background: #0f172a; padding: 15px; border-radius: 6px; border: 1px solid #334155; white-space: pre-wrap; font-family: monospace; color: #38bdf8; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-bar">
            <div>
                <h1>ZEUS AI ENTERTAINMENT MIX LIMITED</h1>
                <p class="subtitle">Commercial Micro-Drama Studio Engine</p>
            </div>
            <div>
                <span class="badge">Credits Remaining: {{ credits }}</span>
            </div>
        </div>

        {% if not is_subscribed %}
        <div class="pay-box">
            <h3>Activate Creator Tier ($30/Month)</h3>
            <p>Unlock unlimited monthly micro-drama pipelines, batch prompt generation, and 30-episode automation.</p>
            <a href="/subscribe" class="pay-btn">Upgrade Now ($30/mo)</a>
        </div>
        <hr style="border: 0; border-top: 1px solid #334155; margin: 25px 0;">
        {% endif %}

        <form id="productionForm">
            <label for="projectType">Select Series Project:</label>
            <select id="projectType" name="projectType">
                <option value="Vault_Blackout">Vault Blackout (Sci-Fi Cyberpunk / 9:16 Vertical)</option>
                <option value="Cain_And_Abel" selected>Cain and Abel (3D Western Animation)</option>
                <option value="Warriors_Way">Warriors Way of Life (Graphic Novel Action)</option>
            </select>
            
            <label for="episodeNumber">Episode Number:</label>
            <select id="episodeNumber" name="episodeNumber">
                <script>
                    for(let i=1; i<=30; i++) {
                        document.write(`<option value="${i}">Episode ${i}</option>`);
                    }
                </script>
            </select>

            <label for="customPrompt">Core Scene / Storyline Idea:</label>
            <textarea id="customPrompt" name="customPrompt" placeholder="Enter what happens in this 66-second episode..."></textarea>

            <button type="submit">Generate Episode Pipeline (1 Credit)</button>
        </form>

        <div id="output"></div>
    </div>

    <script>
        document.getElementById('productionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const outputDiv = document.getElementById('output');
            outputDiv.style.display = 'block';
            outputDiv.innerHTML = "-> [Engine] Processing script breakdown and validating subscription credits...";

            const formData = {
                projectType: document.getElementById('projectType').value,
                episodeNumber: document.getElementById('episodeNumber').value,
                customPrompt: document.getElementById('customPrompt').value
            };

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if(data.success) {
                outputDiv.innerHTML = `✅ PIPELINE GENERATED SUCCESSFULLY!\n\n` +
                    `Project: ${data.project}\n` +
                    `Episode: ${data.episode}\n` +
                    `Credits Left: ${data.remaining_credits}\n\n` +
                    `LOCKED SHOT PROMPTS:\n` +
                    data.shots.map((s, idx) => `Shot ${idx+1}: ${s}`).join('\n');
            } else {
                outputDiv.innerHTML = `❌ Error: ${data.message}`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        session['user_id'] = 1
        session['email'] = 'creator@zeusaientertainment.com'
        session['credits'] = 30
        session['is_subscribed'] = False

    return render_template_string(
        PLATFORM_HTML, 
        credits=session['credits'], 
        is_subscribed=session['is_subscribed']
    )

@app.route('/subscribe')
def subscribe():
    # Placeholder for Paystack (Nigeria) & Stripe (International) redirect hooks
    session['is_subscribed'] = True
    session['credits'] = 100
    return redirect(url_for('dashboard'))

@app.route('/generate', methods=['POST'])
def generate():
    if session.get('credits', 0) <= 0 and not session.get('is_subscribed'):
        return jsonify({"success": False, "message": "Insufficient credits. Please upgrade your plan."})

    session['credits'] -= 1

    data = request.json
    project = data.get('projectType', 'Cain_And_Abel')
    episode = data.get('episodeNumber', '1')
    user_prompt = data.get('customPrompt', 'Hero faces a sudden turning point.')

    shots = [
        f"Hook Shot: Wide establishing view, {user_prompt[:30]}..., high tension, 4k cinematic framing",
        f"Action Shot: Close-up reaction, fast dialogue handoff, strict character style consistency",
        f"Conflict Shot: Escalation of the main plot twist, dynamic camera movement",
        f"Cliffhanger Shot: Sudden freeze-frame on critical reveal, leading directly into Episode {int(episode)+1}"
    ]

    return jsonify({
        "success": True,
        "project": project,
        "episode": episode,
        "remaining_credits": session['credits'],
        "shots": shots
    })

if __name__ == '__main__':
    print("\n================================================================")
    print(" ZEUS AI ENTERTAINMENT MIX LIMITED — COMMERCIAL PLATFORM LIVE")
    print(" Access your business dashboard at: http://127.0.0.1:5000")
    print("================================================================\n")
    app.run(debug=True, port=5000)
