#DATABASE PATH: C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases


### QUE SE ME GUARDE EN UN ARCHIVO UN TROZO DE CADA TABLA Y EL TOP 15 COLUMNAS CON MAS INFO
###THE PURPOSE OF THIS CODE WAS GETTING FAMILIAR WITH THE DATA AND SAVING IN A TEXT FILE SOME ENTRIES OF EACH TABLE AND THE TOP 15 COLUMNS WITH MORE TEXTUAL INFO
'''
import os
import sqlite3
import pandas as pd
import sys 

# Ruta principal donde están las 13 carpetas
ROOT_FOLDER = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases"
# Ruta de salida del archivo
OUTPUT_FILE = "resumen_bases.txt"
# Guardar estadísticas de columnas textuales
text_column_stats = []

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f  # Redirigir stdout al archivo

    for db_folder in os.listdir(ROOT_FOLDER):
        folder_path = os.path.join(ROOT_FOLDER, db_folder)

        if os.path.isdir(folder_path):
            db_file = None
            for file in os.listdir(folder_path):
                if file.endswith(".sqlite") or file.endswith(".db"):
                    db_file = os.path.join(folder_path, file)
                    break

            if db_file is None:
                print(f"[{db_folder}] No se encontró archivo SQLite.")
                continue

            print(f"\n\nBASE DE DATOS: {db_folder}")
            print(f" Archivo: {os.path.basename(db_file)}\n")

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                if not tables:
                    print("No hay tablas en esta base de datos.\n")
                    continue

                for (table_name,) in tables:
                    print(f"  Tabla: {table_name}")
                    try:
                        df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT 5", conn)
                        print(f"    Columnas: {', '.join(df.columns)}")
                        print(df.to_markdown(index=False, tablefmt='grid'))

                        # Ahora calcular longitudes medias para columnas textuales
                        df_full = pd.read_sql_query(f"SELECT * FROM `{table_name}`", conn)
                        for col in df_full.columns:
                            if df_full[col].dtype == object:
                                col_data = df_full[col].dropna().astype(str)
                                if not col_data.empty:
                                    avg_length = col_data.str.len().mean()
                                    text_column_stats.append({
                                        "database": db_folder,
                                        "table": table_name,
                                        "column": col,
                                        "avg_length": avg_length
                                    })

                    except Exception as e:
                        print(f"    Error al leer la tabla '{table_name}': {e}")
            finally:
                conn.close()

    # Restaurar la salida a consola
    sys.stdout = original_stdout

    # Volver a imprimir también en consola el resumen textual
    print("Top 10 columnas con más contenido textual:\n")

    if text_column_stats:
        # Crear un DataFrame para ordenar
        df_stats = pd.DataFrame(text_column_stats)
        top10 = df_stats.sort_values(by="avg_length", ascending=False).head(15)

        print(top10.to_markdown(index=False, tablefmt='grid'))

        # También escribir en el archivo
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\nTop 10 columnas con más contenido textual:\n\n")
            f.write(top10.to_markdown(index=False, tablefmt='grid'))
            f.write("\n")

    else:
        print("No se encontraron columnas de texto.")
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\nNo se encontraron columnas de texto.\n")
'''            
