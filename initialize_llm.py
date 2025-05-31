import os
from llm_test import LLMUDFs
from llm_test import DatasetProcessor

if __name__ == "__main__":
    DATASET_DIR = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\1.BIG_DATA_INTEGRATION\mini_dev-main\mini_dev_data\dev_databases"                  # Carpeta donde están tus JSON
    INPUT_JSON    = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\3.NEURAL_DBs\quest_database\todos.json"     # Archivo JSON con tu lista de especificaciones
    OUTPUT_SQL    = r"C:\Users\saioa\Desktop\ROMA_TRE\Advanced_topics_computer_science\3.NEURAL_DBs\quest_database\results\generated_sql.json"    # Archivo donde se guardarán las consultas generadas
    MODEL_NAME    = "EleutherAI/pythia-1.4b" # O el modelo que prefieras de HF
    #MODEL_NAME = "./finetuned-model"
    HF_TOKEN_ENV  = "HF_TOKEN"              # No voy a utilizarlo pero bueno


    processor = DatasetProcessor(
        dataset_path=DATASET_DIR,
        model=MODEL_NAME,
        hf_token_env=HF_TOKEN_ENV
    )

    sql_queries: dict = processor.generate_sql_queries(INPUT_JSON)

    processor.save_sql_queries(sql_queries, OUTPUT_SQL)

    print(f"Se generaron {len(sql_queries)} consultas SQL y se guardaron en '{OUTPUT_SQL}'")
