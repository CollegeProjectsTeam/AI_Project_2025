import os
from flask import jsonify, request, send_from_directory

from Backend.persistence.services.catalog_service import get_catalog
from Backend.services.question_service import generate_question
from Backend.services.evaluation_service import evaluate_answer

def register_routes(app):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fe_dir = os.path.join(os.path.dirname(root_dir), "Frontend")
    html_dir = os.path.join(fe_dir, "html")
    js_dir = os.path.join(fe_dir, "js")

    @app.get("/")
    def home():
        return send_from_directory(html_dir, "index.html")

    @app.get("/question")
    def question_page():
        return send_from_directory(html_dir, "question.html")

    @app.get("/test")
    def test_page():
        return send_from_directory(html_dir, "test.html")

    @app.get("/frontend/<path:filename>")
    def frontend_files(filename):
        return send_from_directory(fe_dir, filename)

    @app.get("/js/<path:filename>")
    def js_files(filename):
        return send_from_directory(js_dir, filename)

    @app.get("/api/catalog")
    def api_catalog():
        data = get_catalog()
        return jsonify(data)

    @app.post("/api/question")
    def api_question():
        payload = request.get_json(silent=True) or {}
        data = generate_question(payload)
        if not data.get("ok"):
            return jsonify(data), 400
        return jsonify(data)

    @app.post("/api/question/check")
    def api_question_check():
        payload = request.get_json(silent=True) or {}
        data = evaluate_answer(payload)
        if not data.get("ok"):
            return jsonify(data), 400
        return jsonify(data)

    @app.post("/api/test")
    def api_test():
        return jsonify({"ok": False, "error": "not implemented"}), 501
