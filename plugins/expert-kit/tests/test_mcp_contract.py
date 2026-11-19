"""L2 Contract tests for Zero-Dependency Stdio JSON-RPC 2.0 MCP server."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[1]
MCP_SERVER = PLUGIN_ROOT / "core" / "mcp" / "server.py"


class McpContractTests(unittest.TestCase):
    def _send(self, messages: list, env_extra: dict | None = None) -> list:
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        stdin_blob = "\n".join(json.dumps(m) for m in messages) + "\n"
        proc = subprocess.run(
            [sys.executable, str(MCP_SERVER)],
            input=stdin_blob,
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]

    def test_initialize_list_and_call_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            responses = self._send(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {"protocolVersion": "2025-03-26", "clientInfo": {"name": "test"}},
                    },
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "ping"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
                    {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {"name": "check_context_budget", "arguments": {"path": str(PLUGIN_ROOT)}},
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 5,
                        "method": "tools/call",
                        "params": {"name": "plugin_diagnostics", "arguments": {}},
                    },
                    {"jsonrpc": "2.0", "id": 6, "method": "nonexistent/method"},
                ],
                env_extra={"EXPERT_KIT_DATA": tmp},
            )

            by_id = {r["id"]: r for r in responses}
            self.assertEqual(by_id[1]["result"]["serverInfo"]["name"], "expert-diagnostics")
            self.assertEqual(by_id[2]["result"], {})

            tool_names = {t["name"] for t in by_id[3]["result"]["tools"]}
            self.assertEqual(tool_names, {"plugin_diagnostics", "check_context_budget"})

            budget_payload = json.loads(by_id[4]["result"]["content"][0]["text"])
            self.assertTrue(budget_payload["ok"])
            self.assertGreaterEqual(budget_payload["filesChecked"], 2)

            diag_payload = json.loads(by_id[5]["result"]["content"][0]["text"])
            self.assertEqual(diag_payload["plugin"], "expert-kit")
            self.assertTrue(diag_payload["ok"], diag_payload)

            self.assertEqual(by_id[6]["error"]["code"], -32601)
            self.assertTrue((pathlib.Path(tmp) / "logs" / "mcp.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
