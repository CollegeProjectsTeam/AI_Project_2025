# AI_Project_2025 — SmarTest

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**SmarTest** is an educational application that generates and evaluates exam-style questions for the **Artificial Intelligence** course.  
It uses AI assistants (ChatGPT, Gemini, CoPilot) **during development** to generate questions, answers, and code.

> ⚠️ AI assistants are only used during development, not by end users.

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
