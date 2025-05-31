import os
import json
import requests
import re
from typing import List, Dict, Any, Optional, Union
from transformers import pipeline


class LLMUDFs:
    def __init__(self, model: str = "EleutherAI/pythia-1.4b", 
                 hf_token_env: str = "HF_TOKEN", 
                 use_api: bool = False):
        self.model_name = model
        self.hf_token_env = hf_token_env
        self.use_api = use_api
        self.hf_token = os.getenv(self.hf_token_env)
        
        if use_api and not self.hf_token:
            print(f"Advertencia: {hf_token_env} no establecido. Se usará el modelo en modo local.")
            self.use_api = False
        
        if not use_api:
            try:
                self.generator = pipeline("text-generation", model=model)
                print(f"Modelo {model} cargado correctamente en modo local.")
            except Exception as e:
                print(f"Error al cargar el modelo: {e}")
                print("Intentando con un modelo más ligero...")
                try:
                    fallback_model = "EleutherAI/gpt-neo-125m"
                    self.generator = pipeline("text-generation", model=fallback_model)
                    self.model_name = fallback_model
                    print(f"Modelo de respaldo {fallback_model} cargado correctamente.")
                except Exception as e2:
                    print(f"Error crítico al cargar modelos: {e2}")
                    raise RuntimeError("No se pudo inicializar ningún modelo LLM.")
    
    def generate_response(self, prompt: str, max_length: int = None, max_new_tokens=150) -> str:
        if self.use_api:
            return self._generate_via_api(prompt, max_new_tokens)
        else:
            return self._generate_locally(prompt, max_new_tokens)
    
    def _generate_locally(self, prompt: str, max_new_tokens: int) -> str:
        try:
            # Calcular la longitud del input
            input_length = len(prompt.split())  # Aproximación simple de tokens
            # Establecer max_length como input + tokens nuevos + margen de seguridad
            calculated_max_length = input_length + max_new_tokens + 50
            
            results = self.generator(
                prompt, 
                max_length=calculated_max_length,
                max_new_tokens=max_new_tokens,  # Usar max_new_tokens si está disponible
                do_sample=True, 
                temperature=0.7, 
                num_return_sequences=1,
                pad_token_id=self.generator.tokenizer.eos_token_id,
                truncation=True
            )
            generated_text = results[0]['generated_text']
            response = generated_text[len(prompt):] if generated_text.startswith(prompt) else generated_text
            return response.strip()
        except Exception as e:
            print(f"Error al generar respuesta: {e}")
            # Intentar con una configuración más simple si falla
            try:
                results = self.generator(
                    prompt, 
                    max_length=len(prompt.split()) + max_new_tokens,
                    do_sample=True, 
                    temperature=0.7, 
                    num_return_sequences=1,
                    pad_token_id=self.generator.tokenizer.eos_token_id
                )
                generated_text = results[0]['generated_text']
                response = generated_text[len(prompt):] if generated_text.startswith(prompt) else generated_text
                return response.strip()
            except Exception as e2:
                return f"Error al generar respuesta: {str(e2)}"
    
    def _generate_via_api(self, prompt: str, max_new_tokens: int) -> str:
        API_URL = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,  # Usar max_new_tokens en lugar de max_length
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False  # Solo devolver el texto generado
            }
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                response_text = generated_text[len(prompt):] if generated_text.startswith(prompt) else generated_text
                return response_text.strip()
            else:
                return "Error: Formato de respuesta inesperado de la API"
        except Exception as e:
            print(f"Error en la API de Hugging Face: {e}")
            return f"Error al usar la API: {str(e)}"
    
    def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]: # ----------------------------> UDF
        prompt = f"""Clasifica el siguiente texto en una de estas categorías: {', '.join(categories)}
        
        Texto: {text}
        
        Categoría:"""
        response = self.generate_response(prompt, max_new_tokens=30)  # Cambiado a max_new_tokens
        result = {}
        selected_category = None
        
        for category in categories:
            if category.lower() in response.lower():
                selected_category = category
                break
        if not selected_category and categories:
            selected_category = categories[0]
        
        for category in categories:
            result[category] = 0.8 if category == selected_category else 0.2 / (len(categories) - 1) if len(categories) > 1 else 0
        
        return result
    
    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, str]]: # ------------> UDF
        if entity_types:
            entity_types_str = ", ".join(entity_types)
            prompt = f"""Extrae las siguientes entidades del texto: {entity_types_str}
            
            Texto: {text}
            
            Entidades (formato "TIPO: TEXTO"):"""
        else:
            prompt = f"""Extrae las entidades nombradas (personas, lugares, organizaciones) del siguiente texto:
            
            Texto: {text}
            
            Entidades (formato "TIPO: TEXTO"):"""
        
        response = self.generate_response(prompt, max_new_tokens=100)  # Cambiado a max_new_tokens
        entities = []
        lines = response.split("\n")
        
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    entity_type = parts[0].strip()
                    entity_text = parts[1].strip()
                    if entity_text:
                        entities.append({"type": entity_type, "text": entity_text})
        
        return entities
    
    def summarize(self, text: str, max_words: int = 50) -> str: # ---------------------> UDF
        prompt = f"""Resume el siguiente texto en aproximadamente {max_words} palabras:
        
        {text}
        
        Resumen:"""
        return self.generate_response(prompt, max_new_tokens=max_words * 2)  # Cambiado a max_new_tokens
    
    def generate_sql_query(self, question: str, table_schema: str, 
                          udf_types: List[str] = None, 
                          sql_hints: Dict[str, bool] = None) -> str:
        udf_types_str = ", ".join(udf_types) if udf_types else "Ninguno"
        
        hints_text = ""
        if sql_hints:
            hints_list = []
            if sql_hints.get("requires_join"): hints_list.append("se requiere un JOIN")
            if sql_hints.get("requires_group_by"): hints_list.append("se requiere GROUP BY")
            if sql_hints.get("multiple_udfs"): hints_list.append("se requieren múltiples UDFs")
            if hints_list: hints_text = "Pistas SQL: " + ", ".join(hints_list) + ".\n"
        
        prompt = f"""Genera una consulta SQL para responder la siguiente pregunta:
        
        Pregunta: {question}
        
        Esquema de la tabla:
        {table_schema}
        
        UDFs necesarios: {udf_types_str}
        {hints_text}
        
        Por favor, genera una consulta SQL válida y completa. Incluye los UDFs necesarios como funciones personalizadas en la consulta.
        
        Consulta SQL:"""
        
        response = self.generate_response(prompt, max_new_tokens=200)  # Cambiado a max_new_tokens
        return self._extract_sql_query(response)
    
    def _extract_sql_query(self, text: str) -> str:
        sql_pattern = re.compile(r"```sql\s*(.*?)\s*```", re.DOTALL)
        matches = sql_pattern.findall(text)
        if matches:
            return matches[0].strip()
        
        if "SELECT" in text.upper():
            lines = text.split('\n')
            sql_lines = []
            started = False
            for line in lines:
                if ("SELECT" in line.upper()) and not started:
                    started = True
                if started:
                    sql_lines.append(line)
            return '\n'.join(sql_lines).strip()
        
        return text.strip()


class DatasetProcessor:
    def __init__(self, dataset_path: str, model: str = "EleutherAI/pythia-1.4b", hf_token_env: str = "HF_TOKEN"):
        self.dataset_path = dataset_path
        if not os.getenv(hf_token_env):
            print(f"Advertencia: {hf_token_env} no establecido. Se usará modelo local.")
        self.llm_udfs = LLMUDFs(model=model, hf_token_env=hf_token_env)

    def load_dataset(self, filename: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.dataset_path, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar {filename}: {e}")
            return []

    def process_text_data(self, data: List[Dict[str, Any]], text_field: str, operation: str = "summarize", **kwargs) -> List[Dict[str, Any]]:
        result_data = []
        for item in data:
            if text_field not in item:
                print(f"Advertencia: campo '{text_field}' no encontrado.")
                result_data.append(item)
                continue
            
            text = item[text_field]
            processed = item.copy()
            if operation == "summarize":
                processed["summary"] = self.llm_udfs.summarize(text, kwargs.get("max_words", 50))
            elif operation == "classify":
                categories = kwargs.get("categories", [])
                processed["classification"] = self.llm_udfs.classify_text(text, categories) if categories else {}
            elif operation == "extract_entities":
                processed["entities"] = self.llm_udfs.extract_entities(text, kwargs.get("entity_types"))
            else:
                print(f"Operación desconocida: {operation}")
            result_data.append(processed)
        return result_data

    def generate_sql_queries(self, json_file: str) -> Dict[str, str]:
        data = self.load_dataset(json_file)
        results = {}
        for item in data:
            uid = item.get("unique_id", "unknown")
            if not item.get("question") or not item.get("table_schema"):
                results[uid] = "ERROR: Datos insuficientes para generar SQL"
                continue
            results[uid] = self.llm_udfs.generate_sql_query(
                question=item["question"],
                table_schema=item["table_schema"],
                udf_types=item.get("udf_types", []),
                sql_hints=item.get("sql_hints", {})
            )
        return results

    def save_processed_data(self, data: Union[List[Dict[str, Any]], Dict[str, Any]], output_filename: str) -> None:
        path = os.path.join(self.dataset_path, output_filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Datos guardados en {path}")
        except Exception as e:
            print(f"Error al guardar {path}: {e}")

    def save_sql_queries(self, queries: Dict[str, str], output_filename: str) -> None:
        formatted = {
            query_id: {
                "generated_sql": sql,
                "timestamp": None,
                "model_used": self.llm_udfs.model_name
            } for query_id, sql in queries.items()
        }
        self.save_processed_data(formatted, output_filename)