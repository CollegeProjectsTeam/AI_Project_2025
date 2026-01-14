from __future__ import annotations

import os
from flask import Blueprint, jsonify, request, send_from_directory, render_template

from Backend.services.logging_service import Logger
from Backend.persistence.services.catalog_service import get_catalog
from Backend.services.question_service import generate_question
from Backend.services.evaluation_service import evaluate_answer
from Backend.services.test_service import generate_test, fetch_test_details

router = Blueprint('router', __name__)
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

    # Adding new routes for SmarTest logic
    @app.post("/api/test/generate")
    def api_generate_test():
        payload = _safe_payload()
        if not isinstance(payload, dict):
            log.error("Invalid payload format", {"payload": payload})
            return jsonify({"ok": False, "error": "Invalid payload format. Expected a JSON object."}), 400

        log.info("API generate test", {"payload": payload})

        try:
            data = generate_test(payload)
        except Exception as e:
            log.error("generate_test crashed", exc=e)
            return jsonify({"ok": False, "error": "internal server error"}), 500

        if not data.get("ok"):
            code = (data.get("error_code") or "").upper()
            status = 400 if code == "BAD_INPUT" else 500
            log.warn("generate_test returned error", {"error": data.get("error"), "error_code": code, "status": status})
            return jsonify(data), status

        log.ok("Test generated", {"test_id": data.get("test_id")})
        return jsonify(data)

    @app.get("/api/test/details")
    def api_fetch_test_details():
        test_id = request.args.get("test_id")
        log.info("API fetch test details", {"test_id": test_id})

        try:
            data = fetch_test_details(test_id)
        except Exception as e:
            log.error("fetch_test_details crashed", exc=e)
            return jsonify({"ok": False, "error": "internal server error"}), 500

        if not data.get("ok"):
            log.warn("fetch_test_details returned error", {"error": data.get("error")})
            return jsonify(data), 400

        log.ok("Test details fetched", {"test_id": test_id})
        return jsonify(data)

    @app.get("/api/subchapters")
    def fetch_subchapters():
        try:
            catalog = get_catalog()
            out = []

            for ch in catalog.get("chapters", []):
                ch_no = ch.get("chapter_number")
                for sub in ch.get("subchapters", []):
                    out.append({
                        "chapter_number": ch_no,
                        "subchapter_number": sub.get("subchapter_number"),
                        "name": sub.get("subchapter_name"),
                        # id “compozit” pentru checkbox:
                        "id": f"{ch_no}:{sub.get('subchapter_number')}",
                    })

            return jsonify({"ok": True, "subchapters": out})
        except Exception as e:
            log.error("Error fetching subchapters", exc=e)
            return jsonify({"ok": False, "error": "Internal server error"}), 500

    @app.post("/api/generate-test")
    def api_generate_test_alias():
        return api_generate_test()

    @app.get("/question_test")
    def question_test_page():
        return render_template("question_test.html")

    log.ok("Routes registered", {"count": len(app.url_map._rules)})
