from flask import Flask, render_template_string, request, jsonify
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "zeus_ai_secret_key_change_in_production"

# ==========================================
# DATABASE INITIALIZATION (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect('zeus_studio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            status TEXT DEFAULT 'Draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# STUDIO HTML / CSS UI (InVideo Style)
# ==========================================
STUDIO_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZEUS AI ENTERTAINMENT MIX LIMITED - Studio Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; color: #f3f4f6; }
        .glass-panel { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glow-accent { box-shadow: 0 0 25px rgba(59, 130, 246, 0.15); }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Top Navigation Bar -->
    <header class="glass-panel border-b border-gray-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-xl text-white shadow-lg shadow-blue-500/30">Z</div>
            <div>
                <h1 class="font-bold text-base tracking-wide text-white">ZEUS AI STUDIO</h1>
                <p class="text-xs text-blue-400 font-medium">Enterprise Creator Tier</p>
            </div>
        </div>
        <div class="flex items-center space-x-4">
            <span class="px-3 py-1 text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full animate-pulse">● System Online</span>
            <div class="w-9 h-9 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-sm font-bold text-gray-300">Z</div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column: Workflow Control Center (7 cols) -->
        <section class="lg:col-span-7 space-y-6">
            <div class="glass-panel rounded-2xl p-6 glow-accent">
                <h2 class="text-lg font-bold text-white mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                    AI Micro-Drama Director Engine
                </h2>

                <form id="renderForm" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Project Series Title</label>
                        <input type="text" id="projectTitle" value="Cain and Abel: Lagos Nights" class="w-full bg-gray-900/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition">
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Genre / Style Preset</label>
                            <select id="genre" class="w-full bg-gray-900/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition">
                                <option>Cyberpunk Thriller (Cinematic)</option>
                                <option>Nollywood Epic & Drama</option>
                                <option>Gritty Crime Noir</option>
                                <option>Sci-Fi Space Opera</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Episode Duration</label>
                            <select id="duration" class="w-full bg-gray-900/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition">
                                <option>66 Seconds (Short Reel)</option>
                                <option>3 Minutes (Standard Episode)</option>
                                <option>10 Minutes (Full Cinematic)</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Core Scene / Storyline Prompt</label>
                        <textarea id="prompt" rows="4" placeholder="Describe the scene blocking, action, and dialogue..." class="w-full bg-gray-900/80 border border-gray-700 rounded-xl p-4 text-sm text-white focus:outline-none focus:border-blue-500 transition">Two rival fixers meet under neon lights in Adeje, exchanging encrypted drives while an Afrobeats bassline thumps in the distance.</textarea>
                    </div>

                    <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3.5 rounded-xl transition shadow-lg shadow-blue-600/25 flex items-center justify-center space-x-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <span>Generate AI Production Pipeline</span>
                    </button>
                </form>
            </div>
        </section>

        <!-- Right Column: Live Timeline & Output Logs (5 cols) -->
        <section class="lg:col-span-5 space-y-6">
            <div class="glass-panel rounded-2xl p-6 h-full flex flex-col">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-bold uppercase tracking-wider text-gray-300">Live Production Telemetry</h3>
                    <span id="statusBadge" class="px-2.5 py-0.5 text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 rounded-full">Standby</span>
                </div>

                <div id="logOutput" class="flex-1 bg-gray-950/80 border border-gray-800 rounded-xl p-4 font-mono text-xs text-gray-400 overflow-y-auto max-h-[350px] space-y-2">
                    <p class="text-blue-400">> ZEUS_CORE v4.2 initialized successfully.</p>
                    <p>> Waiting for user generation trigger...</p>
                </div>

                <div class="mt-4 pt-4 border-t border-gray-800">
                    <div class="flex justify-between text-xs text-gray-400 mb-2">
                        <span>API Model: OpenAI GPT-4o</span>
                        <span>Token Rate: Optimal</span>
                    </div>
                    <div class="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                        <div id="progressBar" class="bg-blue-600 h-2 w-0 transition-all duration-500"></div>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Script to Handle Dynamic Interactivity -->
    <script>
        document.getElementById('renderForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const logBox = document.getElementById('logOutput');
            const badge = document.getElementById('statusBadge');
            const bar = document.getElementById('progressBar');
            
            badge.className = "px-2.5 py-0.5 text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full animate-pulse";
            badge.innerText = "Processing Pipeline";
            bar.style.width = "30%";

            logBox.innerHTML += `<p class="text-yellow-400">> Initializing AI Director pipeline...</p>`;
            
            setTimeout(() => {
                bar.style.width = "70%";
                logBox.innerHTML += `<p class="text-blue-300">> Parsing scene blocking & audio frequency tags...</p>`;
            }, 1000);

            setTimeout(() => {
                bar.style.width = "100%";
                badge.className = "px-2.5 py-0.5 text-xs bg-green-500/10 text-green-400 border border-green-500/20 rounded-full";
                badge.innerText = "Production Ready";
                logBox.innerHTML += `<p class="text-green-400 font-bold">> Success! Micro-drama script compiled & assets generated.</p>`;
                logBox.scrollTop = logBox.scrollHeight;
            }, 2200);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(STUDIO_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    return jsonify({"status": "success", "message": "Pipeline processed successfully for " + data.get('title', 'Untitled')})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
