import os
import sqlite3
import pandas as pd

# Ruta de la base de datos card_games
ROOT_FOLDER = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases"
DB_FOLDER = "card_games"
DB_FILE = None

# Buscar el archivo SQLite
folder_path = os.path.join(ROOT_FOLDER, DB_FOLDER)
for file in os.listdir(folder_path):
    if file.endswith(".sqlite") or file.endswith(".db"):
        DB_FILE = os.path.join(folder_path, file)
        break

if DB_FILE is None:
    print(f"No se encontró archivo SQLite en {folder_path}")
    exit()

print(f"BASE DE DATOS: {DB_FOLDER}")
print(f"Archivo: {os.path.basename(DB_FILE)}")

# Conectar y consultar
try:
    conn = sqlite3.connect(DB_FILE)

    query = query = """
        SELECT 
            id, 
            date, 
            text, 
            uuid, 
            SUM(CASE WHEN text = 'text1' THEN 1 ELSE 0 END) AS text1, 
            SUM(CASE WHEN text = 'text2' THEN 1 ELSE 0 END) AS text2, 
            SUM(CASE WHEN text = 'text3' THEN 1 ELSE 0 END) AS text3, 
            SUM(CASE WHEN text = 'text4' THEN 1 ELSE 0 END) AS text4, 
            SUM(CASE WHEN text = 'text5' THEN 1 ELSE 0 END) AS text5, 
            SUM(CASE WHEN text = 'text6' THEN 1 ELSE 0 END) AS text6
        FROM rulings
        GROUP BY id, date, text, uuid
    """


    df = pd.read_sql_query(query, conn)

    print("\nPrimeras 30 filas de la tabla 'rulings':")
    print(df.to_markdown(index=False, tablefmt='grid'))

except Exception as e:
    print(f"Error al acceder a la base de datos: {e}")
finally:
    conn.close()
