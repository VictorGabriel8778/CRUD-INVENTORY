from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import pandas as pd
from flask import send_file, Response
import sqlite3
import time

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id= str(id)
        self.username= username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id))
    resultado = c.fetchone()
    conn.close()

    if resultado:
        return User(id=resultado[0], username=resultado[1])
    
    return None

def user_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        );
    ''')
    
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco REAL NOT NULL,
                    product_created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
    conn.commit()
    conn.close()

user_db()
init_db()

@app.route('/')
def registerPage():
    return render_template('register.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route("/graphic")
def GraphicPage():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT nome, quantidade FROM produtos")
    produtos = c.fetchall()

    conn.close()

    return render_template(
        "graphic.html",
        produtos=produtos
    )

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()
    conn.close()
    return jsonify(produtos)

@app.route('/api/adicionar', methods=['POST'])
def adicionar_produto():

    dados = request.get_json()

    nome = dados['nome']
    quantidade = dados['quantidade']
    preco = dados['preco']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)",
        (nome, quantidade, preco))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Produto adicionado com sucesso!"
    }), 201

@app.route('/remover/<int:id>', methods=['DELETE'])
def remover_produto(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM produtos WHERE id = ?", (id,))
    conn.commit()
    conn.close()    

    return jsonify({
        "mensagem": "Produto removido com sucesso!"
    })

@app.route('/atualizar_produto/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.get_json() 
    quantidade = dados['quantidade']
    preco = dados['preco']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE produtos SET quantidade = ?, preco = ? WHERE id = ?', (quantidade, preco, id)) 
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Produto atualizado com sucesso"})

@app.route('/exportar_excel', methods=['GET'])
def exportar_excel():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM produtos",conn)
    conn.close()

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio_database.xlsx"}
    )
    
@app.route('/login/request', methods=['GET'])
def login():
    dados = request.get_json()
    username = dados['username'].lower()
    password = dados['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username))
    result = c.fetchone()
    if result == username:
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        senha = c.fetchone()
    else:
        return jsonify({"erro": "Usuario nao encontrado"})

@app.route('/register/insert', methods=['GET','POST'])
def register():
    dados = request.get_json()
    username = dados['username'].lower()
    password = dados['password']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    if result:
        conn.close()
        return jsonify({"erro": "Usuário já cadastrado, tente outro username"}), 409
    else:
        senha_criptograda = generate_password_hash(password)
        c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,senha_criptograda))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Usuário cadastrado com sucesso"}), 201


if __name__ == '__main__':
    app.run(debug=True)