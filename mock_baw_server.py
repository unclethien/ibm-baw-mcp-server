#!/usr/bin/env python3
# Mock BAW server for local MCP server testing.
# Uses only Python stdlib — no extra dependencies required.
#
# Mimics the two BAW endpoints the MCP server calls:
#   POST /bpm/system/login          → returns a CSRF token
#   GET  /bpm/exposed-services      → returns a fake OpenAPI spec (loan demo)
#   POST /bpm/restapi/submit-loan   → simulates a BAW REST service call
#
# Usage:
#   python mock_baw_server.py          # starts on port 8001
#   python mock_baw_server.py 9000     # starts on a custom port

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "LoanApplication", "version": "1.0"},
    "servers": [{"url": f"http://localhost:{PORT}/bpm/restapi"}],
    "paths": {
        "/submit-loan": {
            "post": {
                "operationId": "submitLoan",
                "summary": "Submit a new loan application",
                "description": (
                    "Creates a new loan application for a customer. "
                    "Provide the applicant name, requested loan amount in USD, "
                    "and optionally their credit score (300-850)."
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["applicant_name", "amount"],
                                "properties": {
                                    "applicant_name": {
                                        "type": "string",
                                        "description": "Full name of the applicant",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Loan amount requested in USD",
                                    },
                                    "credit_score": {
                                        "type": "integer",
                                        "description": "Applicant credit score (300-850)",
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Application submitted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "application_id": {"type": "string"},
                                        "status": {"type": "string"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}

EXPOSED_SERVICES_RESPONSE = {
    "exposed_services": [
        {
            "name": "LoanApplication",
            "description": "Submit and manage loan applications",
            "type": "rest",
            "container": "LoanApp",
            "definitionUrl": f"http://localhost:{PORT}/api",
            "definition": OPENAPI_SPEC,
        }
    ]
}


class MockBAWHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        print(f"  [mock-baw] {format % args}")

    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/bpm/system/login":
            self.send_json({"csrf_token": "mock-csrf-token", "expiration": 7200})
        elif path == "/bpm/restapi/submit-loan":
            body = self.read_body()
            self.send_json({
                "application_id": "LOAN-2025-MOCK-001",
                "status": "PENDING_REVIEW",
                "applicant": body.get("applicant_name", "Unknown"),
                "amount": body.get("amount", 0),
                "credit_score": body.get("credit_score", "not provided"),
                "message": (
                    f"Loan application for {body.get('applicant_name', 'Unknown')} "
                    f"of ${body.get('amount', 0):,} submitted successfully."
                ),
            })
        else:
            self.send_json({"error": f"Unknown POST path: {path}"}, status=404)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/bpm/exposed-services":
            self.send_json(EXPOSED_SERVICES_RESPONSE)
        else:
            self.send_json({"error": f"Unknown GET path: {path}"}, status=404)


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), MockBAWHandler)
    print(f"Mock BAW server running on http://localhost:{PORT}")
    print(f"  POST /bpm/system/login       → CSRF token")
    print(f"  GET  /bpm/exposed-services   → 1 fake tool (LoanApplication)")
    print(f"  POST /bpm/restapi/submit-loan → mock loan response")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
