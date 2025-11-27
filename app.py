from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_conecta_saberes' # Necessário para segurança da sessão
DB_NAME = 'conecta.db'

# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================

def get_db():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome (ex: usuario['email'])
    return conn

def criar_tabelas():
    """
    Cria as tabelas automaticamente se elas não existirem.
    Isso garante que o projeto rode mesmo se o arquivo .db for apagado.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'mentor' ou 'mentorado'
            whatsapp TEXT,
            area TEXT, -- Ex: Tecnologia, Saúde, Educação
            bio TEXT
        )
    ''')
    
    # 2. Tabela de Métricas (Conexões)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conexoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentor_id INTEGER,
            mentorado_id INTEGER,
            data_conexao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mentor_id) REFERENCES usuarios (id),
            FOREIGN KEY (mentorado_id) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    conn.close()

# Executa a criação das tabelas ao iniciar a aplicação
with app.app_context():
    criar_tabelas()


# ==========================================
# ROTAS PÚBLICAS (Acesso livre)
# ==========================================

@app.route('/')
def index():
    """Página Inicial (Landing Page)."""
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Rota para criar conta."""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        whatsapp = request.form['whatsapp']
        area = request.form['area']
        bio = request.form['bio']

        # Criptografa a senha para segurança (Objetivo 1)
        senha_hash = generate_password_hash(senha)

        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO usuarios (nome, email, senha, tipo, whatsapp, area, bio) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (nome, email, senha_hash, tipo, whatsapp, area, bio)
            )
            conn.commit()
            flash('Cadastro realizado com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Este e-mail já está cadastrado.', 'error')
        finally:
            conn.close()
            
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de Autenticação."""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        # Verifica se usuário existe E se a senha bate
        if usuario and check_password_hash(usuario['senha'], senha):
            # Salva dados na sessão (Cookie seguro)
            session['user_id'] = usuario['id']
            session['user_nome'] = usuario['nome']
            session['user_tipo'] = usuario['tipo']
            session['user_area'] = usuario['area'] 
            return redirect(url_for('match'))
        else:
            flash('Email ou senha incorretos.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Encerra a sessão do usuário."""
    session.clear()
    return redirect(url_for('index'))


# ==========================================
# ROTAS PRIVADAS (Requer Login)
# ==========================================

@app.route('/perfil')
def perfil():
    """Visualiza os dados do usuário logado."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('perfil.html', usuario=usuario)

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    """Permite ao usuário alterar seus próprios dados (CRUD - Update)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # SALVAR DADOS (POST)
    if request.method == 'POST':
        nome = request.form['nome']
        whatsapp = request.form['whatsapp']
        area = request.form['area']
        bio = request.form['bio']
        
        try:
            conn.execute('''
                UPDATE usuarios 
                SET nome = ?, whatsapp = ?, area = ?, bio = ?
                WHERE id = ?
            ''', (nome, whatsapp, area, bio, session['user_id']))
            conn.commit()
            
            # Atualiza sessão para refletir mudança de nome no menu imediatamente
            session['user_nome'] = nome
            session['user_area'] = area
            
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('perfil'))
        except:
            flash('Erro ao atualizar. Tente novamente.', 'error')
        finally:
            conn.close()

    # CARREGAR FORMULÁRIO (GET)
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('editar_perfil.html', usuario=usuario)

@app.route('/match')
def match():
    """O Coração do Sistema: Lista mentores ou mostra painel."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tipo_usuario = session['user_tipo']
    filtro_area = request.args.get('area') # Pega filtro da URL se existir (?area=Tecnologia)

    conn = get_db()
    
    # Se sou MENTORADO, vejo lista de MENTORES (Objetivo 2)
    if tipo_usuario == 'mentorado':
        query = "SELECT * FROM usuarios WHERE tipo = 'mentor'"
        params = []
        
        if filtro_area:
            query += " AND area = ?"
            params.append(filtro_area)
            
        mentores = conn.execute(query, params).fetchall()
        conn.close()
        return render_template('match.html', lista=mentores, tipo_visao='procurar_mentores')
    
    # Se sou MENTOR, vejo meu painel
    else:
        conn.close()
        return render_template('match.html', tipo_visao='painel_mentor')

# ==========================================
# API E MÉTRICAS (Invisível ao usuário)
# ==========================================

@app.route('/registrar_conexao/<int:mentor_id>')
def registrar_conexao(mentor_id):
    """
    Registra no banco que um aluno clicou no WhatsApp do mentor.
    Atende ao Objetivo 4 (Validação do Piloto).
    """
    if 'user_id' in session:
        mentorado_id = session['user_id']
        conn = get_db()
        conn.execute('INSERT INTO conexoes (mentor_id, mentorado_id) VALUES (?, ?)',
                     (mentor_id, mentorado_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': 'Conexão registrada'})
    
    return jsonify({'status': 'erro', 'mensagem': 'Não logado'}), 401

if __name__ == '__main__':
    app.run(debug=True)