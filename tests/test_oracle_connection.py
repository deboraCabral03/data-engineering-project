
import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

connection = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_TNS_NAME"),
    config_dir=os.getenv("DB_WALLET_DIR"),
    wallet_location=os.getenv("DB_WALLET_DIR"),
    wallet_password=os.getenv("DB_WALLET_PASSWORD")
)

print("Conexão com Oracle realizada com sucesso!")

def validar_cliente(cliente, cpfs_existentes):
    erros = []

    if not cliente["nome"]:
        erros.append("Nome obrigatório")

    if not cliente["email"]:
        erros.append("E-mail obrigatório")

    cpf = cliente["cpf"]

    if not cpf or len(cpf) != 11 or not cpf.isdigit():
        erros.append("CPF inválido")

    elif cpf in cpfs_existentes:
        erros.append("CPF duplicado no banco")

    return erros

clientes_teste = [
    {
        "nome": "Carlos Lima",
        "email": "carlos@email.com",
        "cpf": "45678901234"
    },
    {
        "nome": "Ana Souza",
        "email": "",
        "cpf": "56789012345"
    },
    {
        "nome": "Pedro Alves",
        "email": "pedro@email.com",
        "cpf": "45678901234"
    }
]

cpfs_existentes = {"45678901234"}

for cliente in clientes_teste:
    erros = validar_cliente(cliente, cpfs_existentes)

    if erros:
        print(cliente["nome"], "REPROVADO:", erros)
    else:
        print(cliente["nome"], "APROVADO")

try:
    with connection.cursor() as cursor:

        cursor.execute("SELECT USER FROM DUAL")
        print("Usuário conectado:", cursor.fetchone()[0])

        clientes = [
            ("Maria Silva", "maria@email.com", "12345678901"),
            ("João Santos", "joao@email.com", "23456789012"),
            ("Ana Costa", "ana@email.com", "34567890123")
        ]

        cursor.executemany("""
            INSERT INTO CLIENTES (NOME, EMAIL, CPF)
            VALUES (:1, :2, :3)
        """, clientes)

        connection.commit()

        print(f"{cursor.rowcount} clientes inseridos!")

        cursor.execute("""
            SELECT ID_CLIENTE, NOME, EMAIL, CPF, DATA_CADASTRO
            FROM CLIENTES
            ORDER BY ID_CLIENTE
        """)

        resultados = cursor.fetchall()

        for cliente in resultados:
            print(cliente)

finally:
    connection.close()
    print("Conexão encerrada.")
