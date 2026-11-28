
import os
import oracledb
from dotenv import load_dotenv


def validar_cliente(cliente, cpfs_processados):
    erros = []

    if not cliente["nome"].strip():
        erros.append("Nome obrigatorio")

    if not cliente["email"].strip():
        erros.append("Email obrigatorio")

    cpf = cliente["cpf"]

    if len(cpf) != 11 or not cpf.isdigit():
        erros.append("CPF invalido")

    if cpf in cpfs_processados:
        erros.append("CPF duplicado no lote")

    return erros


def cliente_existe(cursor, cpf):
    cursor.execute(
        "SELECT 1 FROM CLIENTES WHERE CPF = :cpf",
        {"cpf": cpf}
    )
    return cursor.fetchone() is not None


def inserir_cliente(cursor, cliente):
    cursor.execute(
        """
        INSERT INTO CLIENTES (NOME, EMAIL, CPF)
        VALUES (:nome, :email, :cpf)
        """,
        cliente,
    )


load_dotenv()

connection = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_TNS_NAME"),
    config_dir=os.getenv("DB_WALLET_DIR"),
    wallet_location=os.getenv("DB_WALLET_DIR"),
    wallet_password=os.getenv("DB_WALLET_PASSWORD"),
)

print("Conexao com Oracle realizada com sucesso!")

try:
    with connection.cursor() as cursor:

        cursor.execute("SELECT USER FROM DUAL")
        print("Usuario conectado:", cursor.fetchone()[0])

        clientes = [
            {"nome": "Carlos Lima", "email": "carlos@email.com", "cpf": "45663301234"},
            {"nome": "Ana Souza", "email": "", "cpf": "56789012345"},
            {"nome": "Pedro Alves", "email": "pedro@email.com", "cpf": "45678901234"},
        ]

        cpfs_processados = set()

        recebidos = len(clientes)
        inseridos = 0
        rejeitados = 0

        for cliente in clientes:
            try:
                erros = validar_cliente(cliente, cpfs_processados)

                if erros:
                    rejeitados += 1
                    print(f"{cliente['nome']}: REPROVADO - {erros}")
                    continue


                if cliente_existe(cursor, cliente["cpf"]):
                    rejeitados += 1
                    print(
                        f"{cliente['nome']}: REPROVADO - "
                        "CPF ja cadastrado no banco"
                    )
                    continue

                cursor.execute("SAVEPOINT antes_do_insert")
                
                inserir_cliente(cursor, cliente)

                cpfs_processados.add(cliente["cpf"])
                inseridos += 1

                print(f"{cliente['nome']}: APROVADO")

            except oracledb.DatabaseError as erro:
                cursor.execute("ROLLBACK TO antes_do_insert")
                rejeitados += 1
                print(f"{cliente['nome']}: ERRO NO BANCO - {erro}")

        connection.commit()

        print("\n===== RELATORIO DA CARGA =====")
        print(f"Registros recebidos: {recebidos}")
        print(f"Registros inseridos: {inseridos}")
        print(f"Registros rejeitados: {rejeitados}")

finally:
    connection.close()
    print("Conexao encerrada.")
