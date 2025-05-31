'''
Funcionalidad del script:

Se conecta a la base de datos card_games.sqlite.

Busca en la tabla rulings todas las filas donde el campo text contenga "Hail of Arrows".

Si alguna de esas filas tiene un uuid que aparece también en otras tablas, te indica en qué otras tablas hay registros asociados con ese uuid.
'''

import os
import sqlite3
import pandas as pd

# Ruta de la base de datos card_games
ROOT_FOLDER = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases"
#db_folder = "card_games"
#db_folder = "codebase_community"
db_folder = "student_club"
db_file = None

# Buscar el archivo .sqlite
folder_path = os.path.join(ROOT_FOLDER, db_folder)
for file in os.listdir(folder_path):
    if file.endswith(".sqlite") or file.endswith(".db"):
        db_file = os.path.join(folder_path, file)
        break

if db_file is None:
    print(f"No se encontró archivo SQLite en {folder_path}")
    exit()

print(f"BASE DE DATOS: {db_folder}")
print(f"Archivo: {os.path.basename(db_file)}")

# Conectar a la base de datos
conn = sqlite3.connect(db_file)

try:
    # Buscar registros que mencionan "Hail of Arrows" en la tabla rulings
    #query = """
    #    SELECT * FROM rulings WHERE text LIKE '%Hail of Arrows%';
    #"""
    #query = """
    #    SELECT * FROM rulings WHERE text LIKE '%Bandage%';
    #"""
    #query = """
    #    SELECT * FROM rulings WHERE text LIKE '%mana%';
    #"""
    #query = """
    #    SELECT * FROM rulings WHERE text LIKE '%clone%';
    #"""
    #query = """
    #    SELECT * FROM comments WHERE LOWER(Body) LIKE '%bayesian%' OR LOWER(Title) LIKE '%bayesian%';
    #"""
    query = """
        SELECT * FROM event WHERE LOWER(event_name) LIKE '%officer%' OR LOWER(notes) LIKE '%men%';
    """
    df_rulings = pd.read_sql_query(query, conn)

    if df_rulings.empty:
        print("No se encontraron registros que mencionen 'Hail of Arrows'.")
    else:
        print("\nRegistros en 'rulings' que mencionan 'Hail of Arrows':")
        print(df_rulings.to_markdown(index=False, tablefmt='grid'))

        # Obtener todos los nombres de las tablas en la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = [row[0] for row in cursor.fetchall()]

        # Verificar si hay otras tablas con registros que compartan el mismo uuid
        uuids = df_rulings['uuid'].unique()
        print("\nBuscando relaciones con otras tablas usando 'uuid':")

        for table in all_tables:
            #if table.lower() == "rulings":
            if table.lower() == "superpower":
                continue  # Ya consultamos rulings

            for uuid in uuids:
                cursor.execute(f"""
                    SELECT * FROM `{table}` WHERE uuid = ? LIMIT 3;
                """, (uuid,))
                results = cursor.fetchall()
                if results:
                    print(f"Coincidencias encontradas en la tabla '{table}' para uuid = {uuid}:")
                    df_related = pd.read_sql_query(f"SELECT * FROM `{table}` WHERE uuid = '{uuid}'", conn)
                    print(df_related.head(3).to_markdown(index=False, tablefmt='grid'))

except Exception as e:
    print(f"Error durante la consulta: {e}")
finally:
    conn.close()
