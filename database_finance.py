import sqlite3
from faker import Faker
import random
import datetime

ELEMENTS = 100

# Gerar dados fake
def generate_brazilian_phone():
    ddd = random.choice(["11", "21", "31", "41", "51", "61", "71", "81", "91"])
    return f"({ddd}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def adapt_date(date):
    return date.strftime('%Y-%m-%d')

def convert_date(date_bytes):
    return datetime.datetime.strptime(date_bytes.decode('utf-8'), '%Y-%m-%d').date()

sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

def drop_tables():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS clientes")
    cursor.execute("DROP TABLE IF EXISTS contas_pagar")
    cursor.execute("DROP TABLE IF EXISTS contas_receber")
    cursor.execute("DROP TABLE IF EXISTS lancamentos")
    
    conn.commit()
    conn.close()

def create_database():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Criando tabelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        email TEXT,
                        telefone TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_pagar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fornecedor TEXT,
                        valor REAL,
                        vencimento DATE,
                        status TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_receber (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER,
                        valor REAL,
                        vencimento DATE,
                        status TEXT,
                        FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS lancamentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT,
                        descricao TEXT,
                        valor REAL,
                        data DATE)''')
    
    conn.commit()
    conn.close()

# Gerar dados fake
def populate_fake_data():
    fake = Faker("pt_BR")
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    fornecedores = [fake.company() for _ in range(10)]  # Apenas 10 fornecedores principais
    clientes = [fake.name() for _ in range(20)]  # 20 clientes principais
    
    for _ in range(ELEMENTS):
        cliente = random.choice(clientes)
        cursor.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
                       (cliente, fake.email(), generate_brazilian_phone()))
    
    for _ in range(ELEMENTS):
        fornecedor = random.choice(fornecedores)
        valor = round(random.uniform(300, 15000), 2)  # Maior variação nos valores
        vencimento = fake.date_between(start_date="-3M", end_date="+1M")
        status = random.choices(["Pendente", "Pago"], weights=[0.6, 0.4])[0]  # Maior chance de pendentes
        cursor.execute("INSERT INTO contas_pagar (fornecedor, valor, vencimento, status) VALUES (?, ?, ?, ?)",
                       (fornecedor, valor, vencimento, status))
    
    for _ in range(ELEMENTS):
        cliente_id = random.randint(1, 20)
        valor = round(random.uniform(500, 20000), 2)
        vencimento = fake.date_between(start_date="-2M", end_date="+1M")
        status = random.choices(["Pendente", "Recebido"], weights=[0.5, 0.5])[0]
        cursor.execute("INSERT INTO contas_receber (cliente_id, valor, vencimento, status) VALUES (?, ?, ?, ?)",
                       (cliente_id, valor, vencimento, status))
    
    for _ in range(ELEMENTS):
        tipo = random.choices(["Receita", "Despesa"], weights=[0.55, 0.45])[0]
        descricao = fake.sentence()
        valor = round(random.uniform(200, 10000), 2)
        data = fake.date_between(start_date="-3M", end_date="today")
        cursor.execute("INSERT INTO lancamentos (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)",
                       (tipo, descricao, valor, data))
    
    conn.commit()
    conn.close()

# Execução dos scripts
drop_tables()
create_database()
populate_fake_data()