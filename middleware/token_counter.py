# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: TOKEN BUDGET LEDGER MIDDLEWARE
# COMPLIANCE: ZERO EM-DASHES; EXPLICIT TYPING; ALWAYS POSITIVE
# ==============================================================================

import os
import sqlite3
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from typing import Dict, Any

class TokenCounterMiddleware(BaseHTTPMiddleware):
    """Intercepts Port 5000 API traffic to monitor, count, and log token consumption budgets."""

    def __init__(self, app: Any, db_path: str = "/app/data/private_kernel.db"):
        super().__init__(app)
        self.db_path = db_path

    def _estimate_tokens(self, text: str) -> int:
        """Computes approximate token count using standard 4-character-per-token heuristic."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _resolve_db_path(self) -> str:
        """Resolves the active database file path depending on native or container execution environment."""
        db_file = self.db_path
        # If absolute path is missing or we are running on Windows host, fallback to local relative data folder
        if not os.path.isabs(db_file) or (os.name == 'nt' and db_file.startswith("/app")):
            db_file = os.path.join(os.getcwd(), "data", "private_kernel.db")
        return db_file

    def _log_token_transaction(self, endpoint: str, input_tokens: int, output_tokens: int):
        """Persists the token transaction record to the SQLite private kernel database."""
        db_file = self._resolve_db_path()
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        try:
            conn = sqlite3.connect(db_file, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT INTO token_budget_ledger (timestamp, endpoint, input_tokens, output_tokens, cost_allocation)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, endpoint, input_tokens, output_tokens, "owner_draw_allocation"))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f" : Token Ledger Warning: Unable to log transaction: {str(e)}")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        body_bytes = await request.body()
        async def receive() -> Dict[str, Any]:
            return {"type": "http.request", "body": body_bytes, "more_body": False}
        request._receive = receive

        input_text = body_bytes.decode("utf-8", errors="ignore")
        input_tokens = self._estimate_tokens(input_text)

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        if hasattr(response, "body_iterator"):
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
        else:
            response_body = getattr(response, "body", b"")

        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        output_text = response_body.decode("utf-8", errors="ignore")
        output_tokens = self._estimate_tokens(output_text)

        endpoint_path = request.url.path
        self._log_token_transaction(endpoint_path, input_tokens, output_tokens)

        return response
