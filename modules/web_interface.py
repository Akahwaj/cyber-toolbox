"""
Web interface module for mobile-accessible UI.
Requires: pip install flask
Run: python cyber_toolbox.py --enable-server
Access from mobile browser: http://<your-ip>:5000
"""
import os
import socket

def get_local_ip():
    """Get local IP address for mobile access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run():
    try:
        from flask import Flask, render_template_string, request, jsonify
    except ImportError:
        print("Flask not installed. Install: pip install flask")
        return

    from modules.password import analyze_password
    from modules.hashing import hash_text
    from modules.ai_agent import AIAgent

    app = Flask(__name__)
    agent = AIAgent()

    HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧰 Mythos Lab Cyber Toolbox</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0d1117; color: #c9d1d9; min-height: 100vh; }
  header { background: #161b22; border-bottom: 1px solid #30363d;
           padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 1.3rem; color: #58a6ff; }
  .container { max-width: 900px; margin: 0 auto; padding: 20px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
          padding: 20px; margin-bottom: 20px; }
  .card h2 { color: #58a6ff; margin-bottom: 12px; font-size: 1.1rem; }
  input, textarea, select { width: 100%; padding: 10px; margin: 6px 0 12px;
    background: #0d1117; border: 1px solid #30363d; border-radius: 6px;
    color: #c9d1d9; font-size: 0.95rem; }
  button { background: #238636; color: white; border: none; padding: 10px 20px;
           border-radius: 6px; cursor: pointer; font-size: 0.95rem; width: 100%; }
  button:hover { background: #2ea043; }
  .result { background: #0d1117; border: 1px solid #30363d; border-radius: 6px;
            padding: 12px; margin-top: 12px; white-space: pre-wrap; font-size: 0.9rem; display: none; }
  .tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
  .tab { padding: 8px 16px; background: #21262d; border: 1px solid #30363d;
         border-radius: 6px; cursor: pointer; font-size: 0.9rem; color: #8b949e; }
  .tab.active { background: #1f6feb; border-color: #1f6feb; color: white; }
  .panel { display: none; } .panel.active { display: block; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; }
  .badge-green { background: #1a7f37; color: #aff5b4; }
  .badge-yellow { background: #9a6700; color: #fae17d; }
  .badge-red { background: #b62324; color: #ffd7d5; }
</style>
</head>
<body>
<header>
  <span style="font-size:1.5rem">🧰</span>
  <h1>Mythos Lab Cyber Toolbox</h1>
  <span style="margin-left:auto;font-size:0.8rem;color:#8b949e">Mobile Interface</span>
</header>
<div class="container">
  <div class="tabs">
    <div class="tab active" onclick="showTab('password', event)">🔐 Password</div>
    <div class="tab" onclick="showTab('hash', event)">🔑 Hash</div>
    <div class="tab" onclick="showTab('ai', event)">🤖 AI Chat</div>
    <div class="tab" onclick="showTab('learn', event)">📚 Learn</div>
  </div>
  <div id="password" class="panel active">
    <div class="card">
      <h2>🔐 Password Strength Checker</h2>
      <input type="password" id="pw-input" placeholder="Enter password to check...">
      <button onclick="checkPassword()">Check Strength</button>
      <div class="result" id="pw-result"></div>
    </div>
  </div>
  <div id="hash" class="panel">
    <div class="card">
      <h2>#️⃣ Hash Generator</h2>
      <input type="text" id="hash-input" placeholder="Text to hash...">
      <select id="hash-algo">
        <option value="md5">MD5</option>
        <option value="sha1">SHA-1</option>
        <option value="sha256" selected>SHA-256</option>
        <option value="sha512">SHA-512</option>
      </select>
      <button onclick="generateHash()">Generate Hash</button>
      <div class="result" id="hash-result"></div>
    </div>
  </div>
  <div id="ai" class="panel">
    <div class="card">
      <h2>🤖 AI Cybersecurity Assistant</h2>
      <div id="chat-history" style="min-height:150px;max-height:350px;overflow-y:auto;
           background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px;
           margin-bottom:12px;font-size:0.9rem;"></div>
      <textarea id="chat-input" rows="2" placeholder="Ask anything about cybersecurity..."></textarea>
      <button onclick="sendChat()">Send</button>
    </div>
  </div>
  <div id="learn" class="panel">
    <div class="card">
      <h2>📚 Learn a Tool</h2>
      <input type="text" id="learn-tool" placeholder="Tool name (e.g., nmap, aircrack-ng, frida)">
      <button onclick="learnTool()">Start Tutorial</button>
      <div class="result" id="learn-result"></div>
    </div>
    <div class="card">
      <h2>💡 Explain a Topic</h2>
      <input type="text" id="explain-topic" placeholder="Topic (e.g., SQL injection, CVSS, zero-day)">
      <button onclick="explainTopic()">Explain</button>
      <div class="result" id="explain-result"></div>
    </div>
  </div>
</div>
<script>
function showTab(name, event) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById(name).classList.add('active');
  if (event && event.target) event.target.classList.add('active');
}
async function post(url, data) {
  const r = await fetch(url, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  return r.json();
}
async function checkPassword() {
  const pw = document.getElementById('pw-input').value;
  if (!pw) return;
  const res = await post('/api/password', {password: pw});
  const el = document.getElementById('pw-result');
  el.style.display = 'block';
  const cls = res.strength === 'Strong' ? 'badge-green' : res.strength === 'Moderate' ? 'badge-yellow' : 'badge-red';
  el.innerHTML = `<span class="badge ${cls}">${res.strength}</span> (${res.score}/6)\\n` +
    (res.feedback.length ? 'Suggestions:\\n' + res.feedback.map(f=>'  \u2022 '+f).join('\\n') : 'Great password!');
}
async function generateHash() {
  const text = document.getElementById('hash-input').value;
  const algo = document.getElementById('hash-algo').value;
  if (!text) return;
  const res = await post('/api/hash', {text, algorithm: algo});
  const el = document.getElementById('hash-result');
  el.style.display = 'block';
  el.textContent = `${algo.toUpperCase()}: ${res.hash}`;
}
const chatHist = [];
async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  const hist = document.getElementById('chat-history');
  const youDiv = document.createElement('div');
  youDiv.style.cssText = 'color:#79c0ff;margin-bottom:8px';
  const youLabel = document.createElement('strong');
  youLabel.textContent = 'You: ';
  youDiv.appendChild(youLabel);
  youDiv.appendChild(document.createTextNode(msg));
  hist.appendChild(youDiv);
  chatHist.push({role:'user', content:msg});
  const res = await post('/api/chat', {message: msg, history: chatHist});
  chatHist.push({role:'assistant', content:res.response});
  const aiDiv = document.createElement('div');
  aiDiv.style.cssText = 'color:#aff5b4;margin-bottom:12px';
  const aiLabel = document.createElement('strong');
  aiLabel.textContent = 'AI: ';
  aiDiv.appendChild(aiLabel);
  const aiText = document.createElement('span');
  aiText.textContent = res.response;
  aiDiv.appendChild(aiText);
  hist.appendChild(aiDiv);
  hist.scrollTop = hist.scrollHeight;
}
async function learnTool() {
  const tool = document.getElementById('learn-tool').value.trim();
  if (!tool) return;
  const el = document.getElementById('learn-result');
  el.style.display = 'block'; el.textContent = 'Loading...';
  const res = await post('/api/learn', {tool});
  el.textContent = res.content;
}
async function explainTopic() {
  const topic = document.getElementById('explain-topic').value.trim();
  if (!topic) return;
  const el = document.getElementById('explain-result');
  el.style.display = 'block'; el.textContent = 'Loading...';
  const res = await post('/api/explain', {topic});
  el.textContent = res.content;
}
document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});
</script>
</body>
</html>"""

    @app.route('/')
    def index():
        return render_template_string(HTML)

    @app.route('/api/password', methods=['POST'])
    def api_password():
        data = request.get_json()
        password = data.get('password', '')
        strength, score, feedback = analyze_password(password)
        return jsonify({'strength': strength, 'score': score, 'feedback': feedback})

    @app.route('/api/hash', methods=['POST'])
    def api_hash():
        data = request.get_json()
        text = data.get('text', '')
        algorithm = data.get('algorithm', 'sha256')
        result = hash_text(text, algorithm)
        return jsonify({'hash': result})

    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        data = request.get_json()
        message = data.get('message', '')
        try:
            response = agent.query(message)
        except Exception as exc:
            response = (f"AI service unavailable: {exc}. "
                        "Check your API keys (ANTHROPIC_API_KEY / OPENAI_API_KEY) "
                        "and network connectivity.")
        return jsonify({'response': response})

    @app.route('/api/learn', methods=['POST'])
    def api_learn():
        data = request.get_json()
        tool = data.get('tool', '')
        try:
            content = agent.teach_tool(tool)
        except Exception as exc:
            content = (f"AI service unavailable: {exc}. "
                       "Check your API keys and network connectivity.")
        return jsonify({'content': content})

    @app.route('/api/explain', methods=['POST'])
    def api_explain():
        data = request.get_json()
        topic = data.get('topic', '')
        try:
            content = agent.explain_topic(topic)
        except Exception as exc:
            content = (f"AI service unavailable: {exc}. "
                       "Check your API keys and network connectivity.")
        return jsonify({'content': content})

    local_ip = get_local_ip()
    print(f"\n🌐 Web Interface Starting...")
    print(f"   Local:  http://127.0.0.1:5000")
    print(f"   Mobile: http://{local_ip}:5000")
    print(f"\nOpen on your phone's browser: http://{local_ip}:5000")
    print("Press Ctrl+C to stop the server.\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
