"""Pruebas del modo produccion (--prod): solo carga el formato fijo, sin panel.

Levanta el servidor real en un puerto efimero y comprueba las rutas con HTTP.
"""

import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app  # noqa: E402
import zk_panel  # noqa: E402


class _Server:
    def __init__(self, prod):
        app.Handler.PROD = prod
        zk_panel.G["myip"] = "127.0.0.1"
        zk_panel.G["file"] = None
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        zk_panel.G["port"] = self.srv.server_address[1]
        self.base = f"http://127.0.0.1:{self.srv.server_address[1]}"
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def post(self, path, obj):
        data = json.dumps(obj).encode()
        req = urllib.request.Request(self.base + path, data=data,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()
        app.Handler.PROD = False


def test_prod_sirve_pagina_minima():
    s = _Server(prod=True)
    try:
        code, body = s.get("/")
        assert code == 200
        assert "Cargar formato" in body and "prod.js" in body
    finally:
        s.close()


def test_prod_bloquea_panel_y_editor():
    s = _Server(prod=True)
    try:
        assert s.get("/panel")[0] == 404
        assert s.get("/app.js")[0] == 404
        assert s.get("/api/wg/presets")[0] == 404
        assert s.get("/api/wg/saved")[0] == 404
        # endpoints POST del editor fuera
        assert s.post("/api/wg/build", {"formats": []})[0] == 404
        assert s.post("/api/setfile", {})[0] == 404
    finally:
        s.close()


def test_prod_info_es_el_formato_semilla():
    s = _Server(prod=True)
    try:
        code, body = s.get("/api/wg/prod_info")
        assert code == 200
        j = json.loads(body)
        assert j["name"] == "Wiegand26 (site 12)"
        assert j["spec"]["card_format"] == "ESSSSSSSSCCCCCCCCCCCCCCCCO"
        assert j["spec"]["format_type"] == 3
    finally:
        s.close()


def test_prod_load_preview_construye_pasos():
    s = _Server(prod=True)
    try:
        code, body = s.post("/api/wg/prod_load_preview", {"backup": True})
        assert code == 200
        j = json.loads(body)
        assert j["steps"] and any("u.sql" in st["cmd"] for st in j["steps"])
        # el archivo quedo registrado con el bloque INSERT del formato fijo
        assert zk_panel.G["file"] is not None
        sql = zk_panel.G["file"]["data"].decode("utf-8")
        assert "HID_FORMAT" in sql and "ESSSSSSSSCCCCCCCCCCCCCCCCO" in sql
    finally:
        s.close()


def test_prod_load_exige_sn():
    s = _Server(prod=True)
    try:
        assert s.post("/api/wg/prod_load", {})[0] == 400
        assert s.post("/api/wg/prod_load", {"sn": "all"})[0] == 400
    finally:
        s.close()


def test_prod_state_sigue_disponible():
    # /api/state (y el protocolo del reloj) deben pasar en produccion.
    s = _Server(prod=True)
    try:
        code, body = s.get("/api/state")
        assert code == 200
        assert "devices" in json.loads(body)
    finally:
        s.close()


def test_normal_mantiene_panel_y_editor():
    s = _Server(prod=False)
    try:
        assert s.get("/panel")[0] == 200
        assert s.get("/api/wg/presets")[0] == 200
        assert s.get("/")[1].count("Editor de formato") == 1
        # en modo normal /api/wg/prod_info no entrega el JSON del formato fijo
        assert "Wiegand26 (site 12)" not in s.get("/api/wg/prod_info")[1]
    finally:
        s.close()


if __name__ == "__main__":
    import traceback

    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}"); passed += 1
            except Exception:
                print(f"FAIL {name}"); traceback.print_exc(); failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
