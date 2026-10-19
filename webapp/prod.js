"use strict";
// Version de produccion: solo carga el formato preconfigurado fijo.
const $ = (id) => document.getElementById(id);
const api = async (path, body) => {
  const r = await fetch(path, body ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
  } : undefined);
  const j = await r.json().catch(() => ({ error: "respuesta no-JSON" }));
  if (!r.ok) throw new Error(j.error || ("HTTP " + r.status));
  return j;
};
const msg = (el, text, kind) => {
  el.textContent = text; el.className = "msg show " + (kind || "");
  if (!text) el.className = "msg";
};

// ---------- info del formato fijo ----------
async function loadInfo() {
  try {
    const j = await api("/api/wg/prod_info");
    const s = j.spec || {};
    const tipo = { 3: "entrada", 1: "salida", 2: "interno" }[s.format_type] || s.format_type;
    $("fmtname").textContent = j.name || s.name || "formato";
    $("fmtmeta").textContent = `${s.card_format || ""} · ${tipo}`;
  } catch (e) {
    $("fmtname").textContent = "(no disponible)";
    msg($("loadmsg"), e.message, "err");
  }
}

// ---------- carga ----------
async function loadPreview() {
  try {
    const j = await api("/api/wg/prod_load_preview", { sn: $("sn").value, backup: $("dobackup").checked });
    $("loadview").style.display = "block";
    $("loadview").textContent = j.steps.map(s => `${s.cmd}\n   # ${s.descripcion}`).join("\n");
    msg($("loadmsg"), "", "");
  } catch (e) { msg($("loadmsg"), e.message, "err"); }
}
async function doLoad() {
  const sn = $("sn").value;
  if (!sn || sn === "all") { msg($("loadmsg"), "Elige un SN específico.", "err"); return; }
  if (!confirm(`Cargar el formato en ${sn} y REINICIAR el reloj. ¿Continuar?`)) return;
  try {
    const j = await api("/api/wg/prod_load", { sn, backup: $("dobackup").checked });
    msg($("loadmsg"), `Encolados ${j.queued} comandos a ${j.sn}. El reloj los ejecuta en su próximo sondeo.`, "ok");
  } catch (e) { msg($("loadmsg"), e.message, "err"); }
}

// ---------- dispositivos (poll) ----------
async function tick() {
  try {
    const s = await (await fetch("/api/state")).json();
    const sns = Object.keys(s.devices || {});
    const sel = $("sn"), cur_sn = sel.value;
    sel.innerHTML = sns.length ? sns.map(x => `<option value="${x}">${x}</option>`).join("")
                               : '<option value="">(sin relojes)</option>';
    if (sns.includes(cur_sn)) sel.value = cur_sn;
    const n = sns.length;
    $("devchip").classList.toggle("on", n > 0);
    $("devtxt").textContent = n ? (n + " reloj" + (n > 1 ? "es" : "") + " · " + sns.join(", ")) : "Sin relojes";
    $("hdrsub").textContent = `${s.myip || ""}${s.port ? ":" + s.port : ""} · producción`;
  } catch (e) {}
}

// ---------- init ----------
function init() {
  $("btnloadprev").onclick = loadPreview;
  $("btnload").onclick = doLoad;
  loadInfo();
  setInterval(tick, 2000); tick();
}
init();
