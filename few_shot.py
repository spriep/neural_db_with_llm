import json
from llm_test import LLMUDFs

def build_few_shot_prompt_with_examples(new_question_item):
    #Construye un prompt con ejemplos SQL concretos
    
    # Ejemplos hardcodeados con SQL real
    examples = [
        {
            "question": "How does the 'Hail of Arrows' card work?",
            "schema": "CREATE TABLE rulings (id INTEGER, date TEXT, text TEXT, uuid TEXT);",
            "udfs": "summarization",
            "sql": "SELECT summarize(text, 120) as card_mechanics FROM rulings WHERE text LIKE '%Hail of Arrows%' ORDER BY date DESC;"
        },
        {
            "question": "What key entities are mentioned in questions on Likert scales and how would the topic be classified?",
            "schema": "CREATE TABLE posts (Id INTEGER PRIMARY KEY, Body TEXT, Title TEXT, Tags TEXT); CREATE TABLE comments (Id INTEGER, PostId INTEGER, Text TEXT);",
            "udfs": "Entity Extraction, Text Classification, Temporal Reasoning",
            "sql": "SELECT extract_entities(p.Body, ['scale', 'data', 'method', 'person']) as key_entities, classify_text(p.Body, ['social_sciences', 'mathematics', 'psychology']) as topic_classification FROM posts p WHERE p.Tags LIKE '%likert%' OR p.Title LIKE '%Likert%';"
        },
        {
            "question": "Is the opinion on Likert scales doubtful?",
            "schema": "CREATE TABLE posts (Id INTEGER PRIMARY KEY, Body TEXT, Title TEXT); CREATE TABLE comments (Id INTEGER, PostId INTEGER, Text TEXT);",
            "udfs": "Sentiment Analysis",
            "sql": "SELECT analyze_sentiment(CONCAT(p.Title, ' ', p.Body), ['positive', 'negative', 'doubtful', 'neutral']) as opinion_sentiment FROM posts p WHERE p.Title LIKE '%Likert%' OR p.Body LIKE '%Likert scale%';"
        }
    ]
    
    prompt_parts = ["Generate a SQL query using the required UDFs:\n"]
    
    # Añadir ejemplos
    for i, ex in enumerate(examples, 1):
        prompt_parts.append(f"""Example {i}:
Question: {ex['question']}
Schema: {ex['schema']}
UDFs: {ex['udfs']}
SQL: {ex['sql']}
""")
    
    # Nueva pregunta
    schema = "\n".join(new_question_item["table_schema"]) if isinstance(new_question_item["table_schema"], list) else new_question_item["table_schema"]
    udf_str = ", ".join(new_question_item.get("udf_types", []))
    
    prompt_parts.append(f"""New Question:
Question: {new_question_item["question"]}
Schema: {schema}
UDFs: {udf_str}
SQL:""")
    
    return "\n".join(prompt_parts)

def load_few_shot_examples(file_path, max_examples=3):
    #Reduce a solo 3 ejemplos para evitar prompts muy largos
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[:max_examples]

if __name__ == "__main__":
    EXAMPLES_FILE = "todos.json"
    NEW_QUESTION_ID = "query_009"

    model = LLMUDFs(model="EleutherAI/pythia-1.4b")

    with open(EXAMPLES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_question_item = next((item for item in data if item["unique_id"] == NEW_QUESTION_ID), None)

    if not new_question_item:
        raise ValueError(f"Question ID {NEW_QUESTION_ID} not found")

    # Usar el prompt mejorado
    prompt = build_few_shot_prompt_with_examples(new_question_item)

    print("Prompt sent to model:\n")
    print(prompt)
    print("\nGenerating SQL...\n")

    # Usar parámetros más conservadores
    sql = model.generate_response(prompt, max_new_tokens=80)

    print("Generated SQL query:\n")
    print(sql)