# AI_Project_2025 — SmarTest

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**SmarTest** is an educational application that generates and evaluates exam-style questions for the **Artificial Intelligence** course.  
It uses AI assistants (ChatGPT, Gemini, CoPilot) **during development** to generate questions, answers, and code.

> AI assistants are only used during development, not by end users.

---

## Team

- **Bostan Georgiana**  
- **Ginghina Mihai**  
- **Acasandrei Nicu**  

---

## Features

- Generate questions from selected topics or lectures  
- Specify number of questions  
- Display questions in a GUI or export as PDFs  
- Evaluate user answers (0–100%) with optional explanations  
- Build full tests from multiple questions  
- Log all AI interactions during development  

---

## Installation

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required libraries
pip install psycopg2-binary python-dotenv

# Install flask for web in python
pip install flask

```

## Environment Configuration

The project uses a **`.env` file** to store database and configuration settings.  

Create a `.env` file in the project root with the following content:

```env
DATABASE_NAME=SmarTest
HOST=localhost
PORT=5432
USER=postgres
PASSWORD=your_password
```

## How the Application Works

SmarTest is a Flask web application with a static frontend that generates questions from Artificial Intelligence topics (CSP, search strategies, game theory - minmax/nash) using template-based question generators dedicated to each subchapter. The frontend consumes backend APIs, displays questions, and allows answer verification.

### Question Generation
- **Endpoint:** `POST /api/question`
- **Minimum payload:** `{ "chapter_number": <int>, "subchapter_number": <int> }`
- **Optional parameters:** 
  - `difficulty` (easy|medium|hard) - defaults to `medium` if not specified
  - `options` - generator-specific parameters (e.g., numeric parameters for CSP)
- **Flow:** Backend searches for a question template matching the chapter/subchapter/difficulty combination, then delegates generation to the dedicated subchapter handler. Response includes `question_id`, question text, metadata (type, options), and optionally multiple-choice answers.
- **Answer verification:** `POST /api/question/check` receives `{ question_id, answer, reveal? }` and returns `correct`, `score` (0-100%), plus explanation if available.

### Difficulty Levels
- **`easy`, `medium`, `hard`** — Selects the appropriate template and, for subchapters using numeric parameters (e.g., CSP), adjusts automatically generated ranges (number of variables, constraints, domain sizes, etc.).

### Question Types Available
The application can generate questions for the following AI topics:
- **Constraint Satisfaction Problems (CSP)** - N-Queens, Graph Coloring, Sudoku variations
- **Search Strategies** - BFS, DFS, A*, Greedy algorithms with custom problems
- **Game Theory** - Minmax algorithm with alpha-beta pruning, Nash equilibrium (pure and mixed strategies)

### Test Generation
- **Endpoint:** `POST /api/generate-test` (alias `/api/test/generate`)
- **Payload:** 
  ```json
  {
    "num_questions": <int>,
    "difficulty": "easy|medium|hard",
    "subchapters": ["1:2", {"chapter_number":1,"subchapter_number":2}, ...]
  }
  ```
- **Behavior:** Generates exactly `num_questions` questions, randomly selecting subchapters from the provided list. For each question, retries up to 5 times with randomized options if generation fails (e.g., CSP generator cannot create valid instance).
- **Safety limits:** Maximum `num_questions * 10` total attempts. If the requested number cannot be reached, response contains `partial_test` and `error_code = GENERATION_FAILED`.
- **Success response:** `{"ok": true, "test": [...]}`
- **Error response:** `{"ok": false, "error_code": "BAD_INPUT", "error": "..."}`

### Frontend Interface
- **Test Page:** User submits generation payload, saves response in `sessionStorage`, and redirects to Question Test page.
- **Question Test Page:** Renders question list, allows navigation and verification of each question, displaying feedback (correct/incorrect, score, explanations, JSON details) after answer submission.

