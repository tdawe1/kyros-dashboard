#!/usr/bin/env python3
import json
import sys
import traceback


class JSONRPCServer:
    def __init__(self):
        self.methods = {}

    def method(self, name):
        def deco(fn):
            self.methods[name] = fn
            return fn

        return deco

    def _send(self, obj):
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def _error(self, _id, code, message, data=None):
        err = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        self._send({"jsonrpc": "2.0", "id": _id, "error": err})

    def serve(self):
        # Line-delimited JSON-RPC over stdio (simple scaffolding)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                _id = req.get("id")
                method = req.get("method")
                params = req.get("params", {})
                if method == "initialize":
                    self._send(
                        {
                            "jsonrpc": "2.0",
                            "id": _id,
                            "result": {
                                "capabilities": {
                                    "experimental": True,
                                }
                            },
                        }
                    )
                    continue
                fn = self.methods.get(method)
                if not fn:
                    self._error(_id, -32601, f"Method not found: {method}")
                    continue
                result = fn(params)
                self._send({"jsonrpc": "2.0", "id": _id, "result": result})
            except Exception as e:
                tb = traceback.format_exc()
                self._error(None, -32603, str(e), {"traceback": tb})


__all__ = ["JSONRPCServer"]
