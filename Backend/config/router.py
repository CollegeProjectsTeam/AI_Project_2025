from __future__ import annotations

import os
from flask import jsonify, request, send_from_directory, render_template

from Backend.services.logging_service import Logger
from Backend.persistence.services.catalog_service import get_catalog
from Backend.services.question_service import generate_question
from Backend.services.evaluation_service import evaluate_answer

log = Logger("Router")

def _safe_payload() -> dict:
    payload = request.get_json(silent=True)
    if payload is None:
        log.warn("Missing/invalid JSON payload", {"path": request.path})
        return {}
    if not isinstance(payload, dict):
        log.warn(
            "JSON payload is not an object",
            {"path": request.path, "type": type(payload).__name__},
        )
        return {}
    return payload


def register_routes(app):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fe_dir = os.path.join(os.path.dirname(root_dir), "Frontend")
    js_dir = os.path.join(fe_dir, "js")

    log.ok(
        "Registering routes",
        {"fe_dir": fe_dir, "js_dir": js_dir},
    )

    @app.get("/")
    def home():
        log.info("Serving page", {"template": "index.html"})
        return render_template("index.html")

    @app.get("/question")
    def question_page():
        log.info("Serving page", {"template": "question.html"})
        return render_template("question.html")

    @app.get("/test")
    def test_page():
        log.info("Serving page", {"template": "test.html"})
        return render_template("test.html")

    @app.get("/js/<path:filename>")
    def js_files(filename):
        log.info("Serving js asset", {"file": filename})
        return send_from_directory(js_dir, filename)

    @app.get("/api/catalog")
    def api_catalog():
        log.info("API catalog requested")
        try:
            data = get_catalog()
            chapters = len((data or {}).get("chapters") or [])
            log.ok("API catalog returned", {"chapters": chapters})
            return jsonify(data)
        except Exception as e:
            log.error("API catalog failed", exc=e)
            return jsonify({"ok": False, "error": "internal server error"}), 500

    @app.post("/api/question")
    def api_question():
        payload = _safe_payload()
        log.info(
            "API generate question",
            {
                "chapter_number": payload.get("chapter_number"),
                "subchapter_number": payload.get("subchapter_number"),
                "has_options": bool(payload.get("options")),
            },
        )

        try:
            data = generate_question(payload)
        except Exception as e:
            log.error("generate_question crashed", exc=e)
            return jsonify({"ok": False, "error": "internal server error"}), 500

        if not data.get("ok"):
            log.warn("generate_question returned error", {"error": data.get("error")})
            return jsonify(data), 400

        q = (data.get("question") or {})
        log.ok(
            "Question generated",
            {
                "question_id": q.get("question_id"),
                "type": (q.get("meta") or {}).get("type"),
                "chapter_number": q.get("chapter_number"),
                "subchapter_number": q.get("subchapter_number"),
            },
        )
        return jsonify(data)

    @app.post("/api/question/check")
    def api_question_check():
        payload = _safe_payload()
        log.info(
            "API check answer",
            {
                "question_id": payload.get("question_id"),
                "reveal": bool(payload.get("reveal")),
                "has_answer": payload.get("answer") is not None,
            },
        )

        try:
            data = evaluate_answer(payload)
        except Exception as e:
            log.error("evaluate_answer crashed", exc=e)
            return jsonify({"ok": False, "error": "internal server error"}), 500

        if not data.get("ok"):
            log.warn("evaluate_answer returned error", {"error": data.get("error")})
            return jsonify(data), 400

        log.ok("Answer evaluated", {"correct": data.get("correct"), "score": data.get("score")})
        return jsonify(data)

    @app.post("/api/test")
    def api_test():
        log.warn("API test called (not implemented)")
        return jsonify({"ok": False, "error": "not implemented"}), 501

    log.ok("Routes registered", {"count": len(app.url_map._rules)})
