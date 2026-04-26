import os, zipfile, subprocess, sys, psutil, shutil, time
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "ckrpro_ultimate_fit_2026"

UPLOAD_FOLDER = "servers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
processes = {}

# --- Ultra Premium UI (Mobile Fit) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CKRPRO | ULTRA HUB</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        :root { --blue: #007AFF; --red: #FF453A; --green: #32D74B; --glass: rgba(255, 255, 255, 0.08); }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { margin: 0; background: #000; color: #fff; font-family: -apple-system, sans-serif; overflow-x: hidden; }
        
        .header { position: fixed; top: 0; width: 100%; height: 60px; background: rgba(0,0,0,0.8); backdrop-filter: blur(15px); display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #222; z-index: 1000; }
        .container { padding: 15px; width: 100%; max-width: 450px; margin: 70px auto 20px; }
        
        .card { background: var(--glass); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; margin-bottom: 20px; text-align: center; }
        
        /* Fixed Input Box */
        input[type="text"] { width: 100%; padding: 14px; margin: 10px 0; background: #111; border: 1px solid #333; border-radius: 12px; color: #fff; text-align: center; font-size: 15px; outline: none; }
        input[type="text"]:focus { border-color: var(--blue); }
        
        /* Icon-only Upload */
        .upload-circle { width: 65px; height: 65px; background: rgba(255,255,255,0.05); border: 2px dashed #444; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 10px auto; position: relative; transition: 0.3s; }
        .upload-circle:hover { border-color: var(--blue); background: rgba(0,122,255,0.1); }
        .upload-circle input { position: absolute; opacity: 0; width: 100%; height: 100%; cursor: pointer; }
        
        .btn-main { width: 100%; padding: 15px; background: var(--blue); color: #fff; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 10px; }
        /* Bot Cards */
        .bot-item { background: rgba(255,255,255,0.04); border-radius: 18px; padding: 16px; margin-bottom: 12px; border: 1px solid #222; }
        .status-dot { float: right; font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: bold; }
        .on { background: rgba(50, 215, 75, 0.1); color: var(--green); border: 1px solid var(--green); }
        .off { background: rgba(255, 69, 58, 0.1); color: var(--red); border: 1px solid var(--red); }
        
        /* Control Buttons Grid */
        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; }
        .c-btn { padding: 11px; border-radius: 10px; border: none; font-weight: bold; font-size: 12px; display: flex; align-items: center; justify-content: center; gap: 6px; color: #fff; cursor: pointer; }
        .b-run { background: var(--green); color: #000; }
        .b-stop { background: var(--red); }
        .b-restart { background: #FF9F0A; color: #000; }
        .b-logs { background: #5856D6; }
        .b-del { background: #333; color: var(--red); grid-column: span 2; margin-top: 4px; }
        /* Log Screen */
        .log-view { display: none; background: #000; color: #0f0; padding: 12px; border-radius: 10px; font-family: monospace; font-size: 11px; margin-top: 10px; max-height: 150px; overflow: auto; border: 1px solid #333; text-align: left; }
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight: 900; font-size: 20px;">CKRPRO <span style="color:var(--blue)">ULTRA</span></div>
    </div>
    <div class="container">
        <div class="card">
            <h4 style="margin:0; opacity:0.6; font-size:13px;">DEPLOY NEW BOT</h4>
            <form action="/deploy" method="POST" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="Enter Bot Name" required>
                <div class="upload-circle">
                    <i class="fa-solid fa-file-zipper fa-xl"></i>
                    <input type="file" name="zip" required onchange="toast('File Selected!')">
                </div>
                <button type="submit" class="btn-main">LAUNCH PROJECT</button>
            </form>
        </div>
        <h3 style="font-size: 14px; opacity:0.5; margin-left:10px;">SERVERS</h3>
        {% for s in servers %}
        <div class="bot-item">
            <span class="status-dot {{ 'on' if s.running else 'off' }}">
                {{ 'ACTIVE' if s.running else 'OFFLINE' }}
            </span>
            <b style="font-size: 17px;">{{ s.name }}</b>
            
            <div class="controls">
                {% if not s.running %}
                <button class="c-btn b-run" onclick="api('start', '{{ s.name }}')"><i class="fa-solid fa-play"></i> RUN</button>
                {% else %}
                <button class="c-btn b-stop" onclick="api('stop', '{{ s.name }}')"><i class="fa-solid fa-stop"></i> STOP</button>
                {% endif %}
                
                <button class="c-btn b-restart" onclick="api('restart', '{{ s.name }}')"><i class="fa-solid fa-rotate-right"></i> RESTART</button>
                <button class="c-btn b-logs" onclick="toggleLogs('{{ s.name }}')"><i class="fa-solid fa-terminal"></i> LOGS</button>
                <button class="c-btn b-del" onclick="del('{{ s.name }}')"><i class="fa-solid fa-trash"></i> DELETE</button>
            </div>
            <div id="logs-{{ s.name }}" class="log-view"><code>Loading logs...</code></div>
        </div>
        {% endfor %}
    </div>
    <script>
        function toast(msg) {
            Swal.fire({ text: msg, toast: true, position: 'top', showConfirmButton: false, timer: 2000, background: '#111', color: '#fff' });
        }
        async function api(act, name) {
            Swal.showLoading();
            await fetch(`/api/${act}/${name}`, {method:'POST'});
            location.reload();
        }
        async function toggleLogs(name) {
            const div = document.getElementById(`logs-${name}`);
            div.style.display = div.style.display === 'block' ? 'none' : 'block';
            if(div.style.display === 'block') {
                const r = await fetch(`/api/logs/${name}`);
                const d = await r.json();
                div.innerHTML = `<code>${d.logs.replace(/\\n/g, '<br>')}</code>`;
            }
        }
        function del(name) {
            Swal.fire({
                title: 'Delete?',
                text: "Bot data will be removed!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#FF453A',
                confirmButtonText: 'Yes, Delete'
            }).then((res) => { if(res.isConfirmed) api('delete', name); });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    servers = []
    if os.path.exists(UPLOAD_FOLDER):
        for f in os.listdir(UPLOAD_FOLDER):
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, f)):
                servers.append({"name": f, "running": f in processes})
    return render_template_string(HTML_UI, servers=servers)

@app.route("/deploy", methods=["POST"])
def deploy():
    name = request.form.get("name").strip().replace(" ", "_")
    file = request.files.get("zip")
    if name and file:
        path = os.path.join(UPLOAD_FOLDER, name)
        os.makedirs(path, exist_ok=True)
        z_p = os.path.join(path, "server.zip")
        file.save(z_p)
        with zipfile.ZipFile(z_p, 'r') as z: z.extractall(path)
    return redirect(url_for('index'))

@app.route("/api/<act>/<name>", methods=["POST"])
def action(act, name):
    path = os.path.join(UPLOAD_FOLDER, name)
    if act == "start":
        entry = "bot.py" if os.path.exists(os.path.join(path, "bot.py")) else "main.py"
        log_f = open(os.path.join(path, "logs.txt"), "a")
        processes[name] = subprocess.Popen([sys.executable, entry], cwd=path, stdout=log_f, stderr=log_f)
    elif act == "stop" and name in processes:
        processes[name].terminate()
        processes.pop(name)
    elif act == "restart":
        if name in processes: processes[name].terminate()
        time.sleep(1)
        entry = "bot.py" if os.path.exists(os.path.join(path, "bot.py")) else "main.py"
        log_f = open(os.path.join(path, "logs.txt"), "a")
        processes[name] = subprocess.Popen([sys.executable, entry], cwd=path, stdout=log_f, stderr=log_f)
    elif act == "delete":
        if name in processes: processes[name].terminate(); processes.pop(name)
        shutil.rmtree(path)
    return jsonify({"ok": True})

@app.route("/api/logs/<name>")
def get_logs(name):
    l_p = os.path.join(UPLOAD_FOLDER, name, "logs.txt")
    logs = open(l_p).read()[-1500:] if os.path.exists(l_p) else "No logs yet."
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
