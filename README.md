# TFG-Info Project Documentation

## Overview

This project provides tools and scripts for evaluating, processing, and analyzing runs and qrels (relevance judgments) for misinformation retrieval tasks, using both traditional and LLM-based approaches. It supports multiple years of TREC-style datasets and integrates with OpenAI and Ollama LLMs.

---

## Table of Contents

- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Main Scripts](#main-scripts)
  - [get_runs.py](#get_runspy)
  - [gpt.py](#gptpy)
  - [trec_utils.py](#trec_utilspy)
  - [download_docs.py](#download_docspy)
  - [combine_runs.py](#combine_runspy)
  - [clean_runs.py](#clean_runspy)
  - [find_differences.py](#find_differencespy)
  - [plot_compatibilities.py](#plot_compatibilitiespy)
  - [plot_rbo.py](#plot_rbopy)
  - [confussion.py](#confussionpy)
  - [test.py](#testpy)
  - [test_lucene.py](#test_lucenepy)
- [Shell Scripts](#shell-scripts)
- [Resources and Data](#resources-and-data)
- [How to Run](#how-to-run)
- [License](#license)

---

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

**Main dependencies:**
- requests
- pyserini
- python-dotenv
- rbo
- tiktoken
- pandas
- matplotlib
- argparse
- ollama
- dotenv

---

## Project Structure

```
.
├── get_runs.py
├── gpt.py
├── trec_utils.py
├── download_docs.py
├── combine_runs.py
├── clean_runs.py
├── find_differences.py
├── plot_compatibilities.py
├── plot_rbo.py
├── confussion.py
├── test.py
├── test_lucene.py
├── requirements.txt
├── run.sh
├── auxiliary.sh
├── default_compatibilities.sh
├── resources/
├── runs/
├── stats/
├── downloaded_docs/
├── venv/
└── ...
```

---

## Main Scripts

### `get_runs.py`

- **Purpose:** Generates LLM-based runs for given topics and qrels using prompt templates. Supports both featured and non-featured prompts, and can use either OpenAI or Ollama models.
- **Usage:**  
  ```bash
  python get_runs.py --year 2021 <prompt_file> <output_folder/file> <topics> --model <gpt|llama3>
  ```
- **Key Functions:**
  - `get_prompt_template_list()`: Generates all prompt combinations for featured prompts.
  - `run_run_list()`: Evaluates documents for each topic and writes results.
  - `get_runs_featured_prompt()`, `get_runs_non_featured_prompt()`: Main entry points for running with different prompt types.

---

### `gpt.py`

- **Purpose:** Provides a unified interface for evaluating prompts using either OpenAI or Ollama LLMs, with token counting and prompt filling.
- **Key Functions:**
  - `set_model()`: Switches between supported models.
  - `evaluate()`: Evaluates a prompt using the selected model.
  - `fill_prompt()`: Fills a prompt template with topic and document data.

---

### `trec_utils.py`

- **Purpose:** Utility functions for handling TREC qrels, topics, and document content. Handles multiple years and formats.
- **Key Functions:**
  - `set_year()`, `get_year_data()`: Set and retrieve data for a specific year.
  - `read_line_from_qrel()`, `get_qrels_dict()`: Parse and load qrels.
  - `get_doc_content()`: Retrieve document text from Lucene indexes.

---

### `download_docs.py`

- **Purpose:** Downloads and saves document texts for a given year and set of runs, using Pyserini and Lucene indexes.
- **Usage:**  
  Edit the `YEAR` variable and run:
  ```bash
  python download_docs.py
  ```

---

### `combine_runs.py`

- **Purpose:** Combines usefulness, supportiveness, and credibility run files into a single file for further analysis.
- **Usage:**  
  ```bash
  python combine_runs.py <directory> --usefulness_run <file> --supportiveness_run <file> --credibility_run <file>
  ```

---

### `clean_runs.py`

- **Purpose:** Cleans run files by removing duplicates and entries not present in any qrel.

---

### `find_differences.py`

- **Purpose:** Compares two qrel/run files and reports differences in the last two columns (e.g., label mismatches).

---

### `plot_compatibilities.py`

- **Purpose:** Reads compatibility scores and generates plots for helpful and harmful compatibilities for each prompt.

---

### `plot_rbo.py`

- **Purpose:** Computes and plots Rank-Biased Overlap (RBO) between system rankings using official and LLM qrels.

---

### `confussion.py`

- **Purpose:** Computes confusion matrices and statistics (Cohen's Kappa, MAE) for runs vs. qrels, and can generate LaTeX tables for reporting.

---

### `test.py`

- **Purpose:** Minimal example of using the Ollama LLM API.
- **Usage:**
  ```python
  import ollama
  response = ollama.chat(model='llama3:8b-instruct-q4_1', messages=[{'role': 'user', 'content': 'Hello!'}])
  print(response)
  ```

---

### `test_lucene.py`

- **Purpose:** Example script for testing document retrieval from Lucene indexes using Pyserini.

---

## Shell Scripts

- **`run.sh`**: Example SLURM job script for running evaluation and confusion matrix generation.
- **`auxiliary.sh`**: Example SLURM job script for running LLM-based runs.
- **`default_compatibilities.sh`**: Automates compatibility evaluation for different years and qrels.

---

## Resources and Data

- **resources/**: Contains prompt templates, participant runs, and other supporting files.
- **runs/**: Stores generated run files.
- **stats/**: Stores evaluation results, matrices, and plots.
- **downloaded_docs/**: Stores downloaded document texts.

---

## How to Run

1. **Set up your environment:**
   - Install dependencies: `pip install -r requirements.txt`
   - Set up environment variables as needed (e.g., API keys in `.env`).

2. **Generate runs:**
   - Use `get_runs.py` with the appropriate arguments.

3. **Evaluate and analyze:**
   - Use the plotting and confusion matrix scripts as needed.
---


