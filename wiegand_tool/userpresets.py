"""Almacen de formatos preconfigurados por el usuario.

Guarda formatos ya armados (con un nombre) en un JSON local para poder
cargarlos despues directo al editor y a la tabla, sin tener que leer una
tarjeta con el Arduino cada vez.

El archivo ``user_presets.json`` vive junto a ``app.py`` (raiz del proyecto) y
NO se versiona: cada instalacion mantiene los suyos. La primera vez se crea con
una semilla (DEFAULT_PRESETS). Cada entrada es ``{"name": str, "spec": {...}}``
donde ``spec`` es el mismo formato que usa el editor / ``format_from_spec``.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

# Ruta por defecto: raiz del proyecto (un nivel arriba de wiegand_tool/).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_PATH = os.path.join(_ROOT, "user_presets.json")

# Semilla inicial: el Wiegand26 (site 12) de las capturas de Marcelo.
# site_code queda en 0 (SiteCode NULL): el facility 12 viaja en los bits S de la
# tarjeta; el reloj muestra el numero de tarjeta. El nombre lo deja identificado.
DEFAULT_PRESETS: List[dict] = [
    {
        "name": "Wiegand26 (site 12)",
        "spec": {
            "name": "Wiegand26",
            "card_format": "ESSSSSSSSCCCCCCCCCCCCCCCCO",
            "parities": [
                {"kind": "even", "covers": list(range(1, 13))},
                {"kind": "odd", "covers": list(range(13, 25))},
            ],
            "format_type": 3,   # entrada / lectura
            "status": 1,
            "site_code": 0,
        },
    },
]


class UserPresetError(ValueError):
    pass


def _path() -> str:
    return os.environ.get("WG_USER_PRESETS", STORE_PATH)


def _read_file(path: str) -> Optional[List[dict]]:
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, list):
        return None
    return [e for e in data if isinstance(e, dict) and e.get("name") and e.get("spec")]


def _write_file(path: str, entries: List[dict]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load() -> List[dict]:
    """Devuelve la lista de presets guardados; siembra el archivo la 1a vez."""
    path = _path()
    entries = _read_file(path)
    if entries is None:
        entries = [dict(e) for e in DEFAULT_PRESETS]
        try:
            _write_file(path, entries)
        except OSError:
            pass  # si no se puede escribir, igual devolvemos la semilla
    return entries


def save(name: str, spec: dict) -> List[dict]:
    """Guarda (o reemplaza por nombre) un preset. Devuelve la lista actualizada."""
    name = (name or "").strip()
    if not name:
        raise UserPresetError("el preset necesita un nombre")
    if not isinstance(spec, dict):
        raise UserPresetError("spec invalido")
    entries = load()
    entries = [e for e in entries if e.get("name") != name]
    entries.append({"name": name[:60], "spec": spec})
    entries.sort(key=lambda e: e["name"].lower())
    _write_file(_path(), entries)
    return entries


def delete(name: str) -> List[dict]:
    """Elimina un preset por nombre. Devuelve la lista actualizada."""
    name = (name or "").strip()
    entries = [e for e in load() if e.get("name") != name]
    _write_file(_path(), entries)
    return entries
