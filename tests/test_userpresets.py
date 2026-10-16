"""Pruebas del almacen de formatos preconfigurados (userpresets)."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from wiegand_tool import userpresets  # noqa: E402


def _fresh_store():
    path = tempfile.mktemp(suffix=".json")
    os.environ["WG_USER_PRESETS"] = path
    return path


def test_siembra_wiegand26_site12():
    _fresh_store()
    entries = userpresets.load()
    assert len(entries) == 1
    e = entries[0]
    assert e["name"] == "Wiegand26 (site 12)"
    assert e["spec"]["card_format"] == "ESSSSSSSSCCCCCCCCCCCCCCCCO"
    assert e["spec"]["format_type"] == 3


def test_guardar_y_releer_persiste():
    path = _fresh_store()
    userpresets.load()  # siembra
    spec = {"name": "MiW34", "card_format": "E" + "C" * 32 + "O",
            "parities": [], "format_type": 3, "status": 1, "site_code": 0}
    userpresets.save("MiW34", spec)
    # releer desde disco (otra "sesion")
    again = userpresets._read_file(path)
    names = [e["name"] for e in again]
    assert "MiW34" in names and "Wiegand26 (site 12)" in names


def test_guardar_mismo_nombre_reemplaza():
    _fresh_store()
    userpresets.load()
    userpresets.save("X", {"card_format": "ECO", "format_type": 3})
    userpresets.save("X", {"card_format": "EECO", "format_type": 1})
    xs = [e for e in userpresets.load() if e["name"] == "X"]
    assert len(xs) == 1
    assert xs[0]["spec"]["format_type"] == 1


def test_borrar():
    _fresh_store()
    userpresets.load()
    userpresets.save("Y", {"card_format": "ECO"})
    userpresets.delete("Y")
    assert all(e["name"] != "Y" for e in userpresets.load())


def test_guardar_sin_nombre_falla():
    _fresh_store()
    try:
        userpresets.save("", {"card_format": "ECO"})
        assert False
    except userpresets.UserPresetError:
        pass


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
