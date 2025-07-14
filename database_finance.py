import sqlite3
from faker import Faker
import random
import datetime

ELEMENTS = 100  # Nombre d'éléments à générer

# Générer un numéro de téléphone brésilien fictif
def generer_telephone_bresilien():
    ddd = random.choice(["11", "21", "31", "41", "51", "61", "71", "81", "91"])
    return f"({ddd}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"

# Adapter et convertir les dates pour SQLite
def adapter_date(date):
    return date.strftime('%Y-%m-%d')

def convertir_date(date_bytes):
    return datetime.datetime.strptime(date_bytes.decode('utf-8'), '%Y-%m-%d').date()

# Enregistrer l'adaptation de types pour SQLite
sqlite3.register_adapter(datetime.date, adapter_date)
sqlite3.register_converter("DATE", convertir_date)

# Supprimer les tables existantes si elles existent
def supprimer_tables():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS clients")
    cursor.execute("DROP TABLE IF EXISTS factures_a_payer")
    cursor.execute("DROP TABLE IF EXISTS factures_a_recevoir")
    cursor.execute("DROP TABLE IF EXISTS transactions")
    
    conn.commit()
    conn.close()

# Créer les tables de la base de données
def creer_base_de_donnees():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT,
                        email TEXT,
                        telephone TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS factures_a_payer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fournisseur TEXT,
                        montant REAL,
                        date_echeance DATE,
                        statut TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS factures_a_recevoir (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        montant REAL,
                        date_echeance DATE,
                        statut TEXT,
                        FOREIGN KEY(client_id) REFERENCES clients(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT,
                        description TEXT,
                        montant REAL,
                        date DATE)''')
    
    conn.commit()
    conn.close()

# Remplir la base avec des données fictives
def remplir_donnees_fictives():
    fake = Faker("fr_FR")  # Utiliser le faker français pour des noms francophones
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    fournisseurs = [fake.company() for _ in range(10)]
    clients = [fake.name() for _ in range(20)]
    
    for _ in range(ELEMENTS):
        client = random.choice(clients)
        cursor.execute("INSERT INTO clients (nom, email, telephone) VALUES (?, ?, ?)",
                       (client, fake.email(), generer_telephone_bresilien()))
    
    for _ in range(ELEMENTS):
        fournisseur = random.choice(fournisseurs)
        montant = round(random.uniform(300, 15000), 2)
        date_echeance = fake.date_between(start_date="-3M", end_date="+1M")
        statut = random.choices(["En attente", "Payé"], weights=[0.6, 0.4])[0]
        cursor.execute("INSERT INTO factures_a_payer (fournisseur, montant, date_echeance, statut) VALUES (?, ?, ?, ?)",
                       (fournisseur, montant, date_echeance, statut))
    
    for _ in range(ELEMENTS):
        client_id = random.randint(1, 20)
        montant = round(random.uniform(500, 20000), 2)
        date_echeance = fake.date_between(start_date="-2M", end_date="+1M")
        statut = random.choices(["En attente", "Reçu"], weights=[0.5, 0.5])[0]
        cursor.execute("INSERT INTO factures_a_recevoir (client_id, montant, date_echeance, statut) VALUES (?, ?, ?, ?)",
                       (client_id, montant, date_echeance, statut))
    
    for _ in range(ELEMENTS):
        type_transaction = random.choices(["Recette", "Dépense"], weights=[0.55, 0.45])[0]
        description = fake.sentence()
        montant = round(random.uniform(200, 10000), 2)
        date = fake.date_between(start_date="-3M", end_date="today")
        cursor.execute("INSERT INTO transactions (type, description, montant, date) VALUES (?, ?, ?, ?)",
                       (type_transaction, description, montant, date))
    
    conn.commit()
    conn.close()

# Exécuter les fonctions
supprimer_tables()
creer_base_de_donnees()
remplir_donnees_fictives()
