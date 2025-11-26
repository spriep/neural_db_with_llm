# Neural Databases: Extending SQL with LLM-based UDFs

![LLM](https://img.shields.io/badge/Model-Pythia_1.4B-blueviolet) ![BIRD-SQL](https://img.shields.io/badge/Dataset-BIRD_Mini--Dev-blue) ![Status](https://img.shields.io/badge/Status-Experimental-orange)

## 📌 Project Overview

This repository explores the integration of **Large Language Models (LLMs)** into traditional relational databases to solve complex queries that standard SQL cannot handle alone.

The core concept is the implementation of **LLM-based User Defined Functions (UDFs)**. Unlike traditional scalar or table-valued functions, these UDFs leverage the semantic understanding of LLMs to perform tasks such as **Sentiment Analysis**, **Text Summarization**, and **Commonsense Inference** directly within a query workflow.

## 🧠 Core Concept: What is an LLM-UDF?

A User-Defined Function (UDF) typically extends SQL with custom logic. In this project, UDFs are reimagined as AI-driven modules:
* **Standard SQL:** `SELECT price FROM products WHERE category = 'electronics';`
* **LLM-Enhanced SQL:** `SELECT product_name FROM products WHERE UDF_Sentiment(review_text) = 'positive';`

We defined **6 distinct UDF Types** to categorize these capabilities:
1.  **Sentiment Analysis:** Interpreting emotional tone in reviews.
2.  **Entity Extraction:** Identifying names/places in unstructured text.
3.  **Summarization:** Condensing long text fields.
4.  **Text Classification:** Categorizing entries without explicit tags.
5.  **Temporal Reasoning:** Understanding natural language time expressions.
6.  **Commonsense Inference:** Drawing conclusions based on general world knowledge.

## 📊 Dataset & Benchmarking

The project utilizes the **BIRD Benchmark (Mini-Dev version)**, a dataset of high-quality text-to-SQL pairs derived from 11 distinct databases.

**Data Selection Strategy:**
Given the limitations of the "Lite" dataset, a custom analysis script was developed to identify tables with rich textual content suitable for LLM tasks. We selected high-density columns (e.g., `Match` descriptions in European Football, `Posts` in Codebase Community) to generate meaningful test samples.

**Annotation Schema:**
A strict JSON schema was designed to ground-truth the experiments, capturing the natural language question, the expected SQL query, and the specific UDF justification required to solve it.

## ⚙️ Experimental Setup

**Hardware Constraints & Model Choice:**
Due to the lack of access to proprietary APIs (GPT-4) or cloud GPUs, this project was engineered to run entirely on **local hardware**.
* **Model:** `EleutherAI/pythia-1.4b` (Open Source, hosted on Hugging Face).
* **Reasoning:** Provides a viable trade-off between resource consumption and reasoning capability for a local environment.

## 📉 Results & Analysis

We evaluated the model's ability to generate valid SQL+UDF queries under two paradigms:

### 1. Zero-Shot Performance
* **Setup:** The model was tasked with generating queries without prior examples.
* **Outcome:** The model struggled with syntax, often generating broken SQL or missing standard clauses (e.g., `GROUP BY`). However, it successfully identified the *intent* of the query, attempting to insert logic where appropriate.

### 2. Few-Shot Performance
* **Setup:** The model was provided with 3 context examples before the target question.
* **Outcome:** Significant improvement in logic. While syntax errors persisted, the model demonstrated a much stronger ability to correctly incorporate the specific UDF function calls (e.g., `extract_entities(...)`) requested in the prompt.

**Key Takeaway:** Even smaller, locally-run LLMs show strong potential for Neural Database tasks when provided with adequate context (Few-Shot), paving the way for more efficient, privacy-preserving AI-SQL integrations.

---

*Project developed at Università degli Studi Roma Tre / Universidad de León.*
