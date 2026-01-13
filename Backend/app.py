from __future__ import annotations

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, g

from config.router import register_routes
from Backend.services.logging_service import Logger


log = Logger("FlaskApp")

def create_app() -> Flask:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(root_dir)
    fe_dir = os.path.join(project_dir, "Frontend")
    html_dir = os.path.join(fe_dir, "html")

    app = Flask(
        __name__,
        template_folder=html_dir,
        static_folder=fe_dir,
        static_url_path="/frontend",
    )

    log.info("Registering routes")
    register_routes(app)
    log.ok("Routes registered", {"count": len(app.url_map._rules)})

    @app.before_request
    def _before_request():
        g._start_time = time.perf_counter()
        log.info("BE <- FE request", {"method": request.method, "path": request.path})

    @app.after_request
    def _after_request(response):
        elapsed_ms = int(
            (time.perf_counter() - getattr(g, "_start_time", time.perf_counter())) * 1000
        )
        log.ok(
            "BE -> FE response",
            {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "ms": elapsed_ms,
            },
        )
        return response

    @app.errorhandler(Exception)
    def _handle_exception(e: Exception):
        log.error("Unhandled exception", {"method": request.method, "path": request.path}, exc=e)
        return {"ok": False, "error": "internal server error"}, 500

    @app.route('/favicon.ico')
    def favicon():
        return "", 204


    return app


if __name__ == "__main__":
    app = create_app()
    host = "127.0.0.1"
    port = 5000
    log.ok("Starting Flask server", {"host": host, "port": port, "debug": False})
    app.run(host=host, port=port, debug=False)