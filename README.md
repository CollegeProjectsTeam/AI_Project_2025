# AI_Project_2025 — SmarTest

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**SmarTest** is an AI-powered educational application that generates and evaluates exam-style questions for the **Artificial Intelligence** course.  
It uses AI assistants (ChatGPT, Gemini, CoPilot) **during development** to generate questions, answers, and code.

> ⚠️ AI assistants are only used during development, not by end users.

---

## Team

- **Bostan Georgiana:**
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

## Minimum Question Types

1. **Search Problems:** Identify best solving strategy (n-queens, Hanoi, graph coloring, etc.)  
2. **Game Theory (Normal Form):** Detect pure Nash equilibria  
3. **Constraint Satisfaction:** Solve partial assignments using Backtracking + optimization  
4. **Adversarial Search (Minimax):** Compute root value and visited leaf nodes with Alpha-Beta pruning  

> Additional question types, explanations, references, or difficulty levels improve scoring.

---

## Installation

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required libraries
pip install pyscopg2-binary python-dotenv
