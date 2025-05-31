import os
import sqlite3
import pandas as pd

# Ruta de la base de datos card_games
ROOT_FOLDER = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases"
#DB_FOLDER = "card_games"
DB_FOLDER = "codebase_community"
#DB_FOLDER = "student_club"
#DB_FOLDER = "european_football_2"
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

    # Asegúrate que el LIMIT esté en 30
    #query = "SELECT * FROM rulings LIMIT 300;"
    '''query = """SELECT sql
FROM sqlite_master
WHERE type = 'table' AND name = 'comments';
""" '''
    '''query = """SELECT *
FROM comments
WHERE PostId = 11;
""" '''
    '''query = """ SELECT *
FROM posts
WHERE Id = 11 AND PostTypeId = 1;
""" '''
    query = """ SELECT Id, SUBSTR(Body, 1, 300) AS BodyPreview
FROM posts
LIMIT 25;""" 
    '''query =  """
        SELECT 
            c.Id AS comment_id,
            c.Text AS comment_text,
            c.CreationDate AS comment_date,
            p.Id AS post_id,
            p.Title AS post_title,
            p.Body AS post_body,
            p.Score AS post_score
        FROM comments c
        LEFT JOIN posts p ON c.PostId = p.Id
        LIMIT 30;
    """ '''
    
    df = pd.read_sql_query(query, conn)

    print("\nPrimeras 30 filas de la tabla 'rulings':")
    print(df.to_markdown(index=False, tablefmt='grid'))

except Exception as e:
    print(f"Error al acceder a la base de datos: {e}")
finally:
    conn.close()
