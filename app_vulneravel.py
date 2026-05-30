# app_vulneravel.py
# Aplicação Flask com múltiplas vulnerabilidades intencionais
# ATENÇÃO: Este arquivo é apenas para fins educacionais - NÃO use em produção!

import sqlite3
import subprocess
import hashlib
import os
import pickle
import yaml
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

# ─────────────────────────────────────────────
# VULNERABILIDADE 1: Chave secreta hardcoded
# ─────────────────────────────────────────────
app.secret_key = "minha_senha_super_secreta_123"
DB_PASSWORD = "admin123"
API_KEY = "sk-prod-abc123xyz789"

# ─────────────────────────────────────────────
# VULNERABILIDADE 2: SQL Injection
# ─────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ERRO: concatenação direta de input do usuário na query SQL
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    if user:
        return "Login bem-sucedido!"
    return "Credenciais inválidas"


# ─────────────────────────────────────────────
# VULNERABILIDADE 3: XSS (Cross-Site Scripting)
# ─────────────────────────────────────────────
@app.route("/greet")
def greet():
    name = request.args.get("name", "visitante")

    # ERRO: interpolação direta de input do usuário no template HTML
    template = "<h1>Olá, " + name + "!</h1>"
    return render_template_string(template)


# ─────────────────────────────────────────────
# VULNERABILIDADE 4: Command Injection
# ─────────────────────────────────────────────
@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")

    # ERRO: shell=True com input do usuário permite injeção de comandos
    result = subprocess.run("ping -c 1 " + host, shell=True, capture_output=True, text=True)
    return result.stdout


# ─────────────────────────────────────────────
# VULNERABILIDADE 5: Path Traversal
# ─────────────────────────────────────────────
@app.route("/file")
def read_file():
    filename = request.args.get("name", "")

    # ERRO: sem validação do caminho, permite leitura de qualquer arquivo
    with open("/var/data/" + filename, "r") as f:
        return f.read()


# ─────────────────────────────────────────────
# VULNERABILIDADE 6: Senha com hash fraco (MD5)
# ─────────────────────────────────────────────
def hash_password(password):
    # ERRO: MD5 é criptograficamente quebrado para senhas
    return hashlib.md5(password.encode()).hexdigest()


# ─────────────────────────────────────────────
# VULNERABILIDADE 7: Deserialização insegura
# ─────────────────────────────────────────────
@app.route("/load_session", methods=["POST"])
def load_session():
    data = request.data

    # ERRO: pickle.loads com dados externos permite execução de código arbitrário
    session_data = pickle.loads(data)
    return str(session_data)


# ─────────────────────────────────────────────
# VULNERABILIDADE 8: YAML com parser inseguro
# ─────────────────────────────────────────────
@app.route("/config", methods=["POST"])
def load_config():
    config_text = request.data.decode()

    # ERRO: yaml.load sem Loader permite execução de código Python
    config = yaml.load(config_text)
    return str(config)


# ─────────────────────────────────────────────
# VULNERABILIDADE 9: Debug mode em produção
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # ERRO: debug=True expõe informações sensíveis e permite RCE
    app.run(debug=True, host="0.0.0.0", port=5000)
