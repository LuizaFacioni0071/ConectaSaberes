import sqlite3
from werkzeug.security import generate_password_hash

# Nome do arquivo do banco (tem que ser igual ao do app.py)
DB_NAME = 'conecta.db'

def init_db():
    print(f"Conectando ao banco de dados '{DB_NAME}'...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. LIMPEZA (RESET) ---
    # Remove as tabelas antigas para criar novas do zero.
    # CUIDADO: Isso apaga todos os dados existentes!
    cursor.execute('DROP TABLE IF EXISTS conexoes')
    cursor.execute('DROP TABLE IF EXISTS usuarios')

    # --- 2. CRIAÇÃO DAS TABELAS ---
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            whatsapp TEXT,
            area TEXT,
            bio TEXT
        )
    ''')

    # Tabela de Conexões (Métricas)
    cursor.execute('''
        CREATE TABLE conexoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentor_id INTEGER,
            mentorado_id INTEGER,
            data_conexao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mentor_id) REFERENCES usuarios (id),
            FOREIGN KEY (mentorado_id) REFERENCES usuarios (id)
        )
    ''')

    # --- 3. DADOS DE TESTE (MOCK DATA) ---
    # Cria mentores falsos para você testar a busca e o botão do WhatsApp.
    
    print("Criando dados de teste...")
    
    # Gera um hash de senha seguro (a senha para todos será '123456')
    senha_padrao = generate_password_hash('123456')

    mentores_ficticios = [
        (
            'Ana Silva', 
            'ana@teste.com', 
            senha_padrao, 
            'mentor', 
            '11999999999', 
            'Tecnologia', 
            'Desenvolvedora Full Stack com 5 anos de exp. Posso ajudar com Python e React.'
        ),
        (
            'Carlos Souza', 
            'carlos@teste.com', 
            senha_padrao, 
            'mentor', 
            '21988888888', 
            'Saúde', 
            'Enfermeiro Chefe. Mentoria sobre carreira hospitalar e residência.'
        ),
        (
            'Mariana Oliveira', 
            'mari@teste.com', 
            senha_padrao, 
            'mentor', 
            '31977777777', 
            'Educação', 
            'Pedagoga. Ajudo na estruturação de projetos acadêmicos e TCC.'
        ),
        (
            'João Pedro',
            'joao@teste.com',
            senha_padrao,
            'mentorado',
            '11966666666',
            'Tecnologia',
            'Estudante buscando primeira oportunidade.'
        )
    ]

    cursor.executemany('''
        INSERT INTO usuarios (nome, email, senha, tipo, whatsapp, area, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', mentores_ficticios)

    conn.commit()
    conn.close()
    print(">>> Sucesso! Banco de dados inicializado com dados de teste.")

if __name__ == '__main__':
    init_db()