// MR- La Rima de la Doncella de la Escarcha · Importa la aventura en un mundo vacío, registra su paquete en
// MR- Dirección (barra del Narrador) y ofrece la Lotería de Auril de cada luna nueva.
const MOD = "mr-doncella-escarcha";
const PACK = `${MOD}.aventura`;
const { DialogV2 } = foundry.applications.api;
const esc = s => foundry.utils.escapeHTML?.(String(s)) ?? String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

Hooks.once("init", () => {
  game.settings.register(MOD, "importada", { scope: "world", config: false, type: Boolean, default: false });
});

/* ---------- Importación ---------- */
function mundoVacio() {
  // El sistema Mist crea por su cuenta un objeto «scene-data» por escena: no cuenta como contenido.
  const sin = ["actors", "journal", "playlists", "macros", "tables", "cards"].every(c => !game[c]?.size)
    && game.items.contents.every(i => i.type === "scene-data");
  return sin && game.scenes.contents.every(s => s.background?.src?.startsWith("nue/") && !s.tokens.size);
}
export async function importarAventura({ confirmar = false } = {}) {
  if (!game.user.isGM) return ui.notifications.warn("La Rima: solo el Narrador puede importar la aventura.");
  const pack = game.packs.get(PACK);
  if (!pack) return ui.notifications.error("La Rima: no encuentro el compendio de la aventura.");
  if (confirmar && !mundoVacio()) {
    const ok = await DialogV2.confirm({
      window: { title: "Importar la aventura", icon: "fa-solid fa-file-import" },
      content: "<p>Este mundo ya tiene contenido. Al importar se <b>sobrescriben</b> los documentos de la aventura que hayas cambiado.</p>",
      yes: { label: "Importar", icon: "fa-solid fa-file-import" }, no: { label: "Cancelar" }, rejectClose: false
    });
    if (!ok) return;
  }
  ui.notifications.info("La Rima: importando la aventura…");
  const adv = (await pack.getDocuments())[0];
  await adv.import({ dialog: false });
  await game.settings.set(MOD, "importada", true);
  await game.scenes.find(s => s.getFlag(MOD, "slug") === "ciudad-bryn-shander")?.activate();
  ui.notifications.info("La Rima: aventura importada. Empieza por el diario «Diez Ciudades» del Manual del Narrador.");
}

/* ---------- MR- Dirección ---------- */
let registrado = false;
async function registrarDireccion(api) {
  if (registrado || !api?.registerPack) return;
  try {
    const pack = await (await fetch(`modules/${MOD}/content/direccion.json`)).json();
    api.registerPack(pack); registrado = true;
  } catch (e) { console.error(`${MOD} | no se pudo registrar el paquete de dirección`, e); }
}
Hooks.on("mrDireccion.ready", registrarDireccion);

/* ---------- Lotería de Auril ---------- */
const VECINOS = ["Jarl Brenhalla, curtidor", "Mina Hojafría, tejedora de redes", "el viejo Torsk, pescador", "Edda Pellejos, carbonera", "Bram, mozo de cuadras",
  "Ulla la Quieta, viuda", "Hekla Turbaseca, panadera", "Orrin Tresdedos, tallador de hueso", "Siv, la hija del herrero", "Gudrun Mirahielo, curandera",
  "Pell Barrenador, minero", "Yrsa Copodenieve, niña de diez años", "Kettil el Sordo, leñador", "Asta Remendona, sastra", "Ivar Pocasluces, sereno"];
export async function loteria() {
  if (!game.user.isGM) return;
  const ciudades = { "Bryn Shander": 0, "Targos": 0, "Bremen": 0, "Termalaine": 0, "Bosque Solitario": 0, "Caer-Konig": 0, "Caer-Dineval": 0, "Puerto Este": 0, "Buenaguamiel": 0, "Refugio de Dougan": 0 };
  const opciones = Object.keys(ciudades).map(c => `<option>${c}</option>`).join("");
  const r = await DialogV2.prompt({
    window: { title: "Lotería de Auril", icon: "fa-solid fa-snowflake" },
    content: `<p>Cada luna nueva, cada ciudad sortea a quién dejará a la intemperie como ofrenda a la Doncella de la Escarcha.</p>
      <div class="form-group"><label>Ciudad</label><select name="ciudad">${opciones}</select></div>
      <div class="form-group"><label>Nombres (uno por línea; vacío = vecinos de ejemplo)</label><textarea name="nombres" rows="5"></textarea></div>`,
    ok: { label: "Sacar un nombre", icon: "fa-solid fa-hand", callback: (ev, b) => ({ ciudad: b.form.elements.ciudad.value, nombres: b.form.elements.nombres.value }) },
    rejectClose: false
  });
  if (!r) return;
  const lista = r.nombres.split("\n").map(s => s.trim()).filter(Boolean);
  const pool = lista.length ? lista : VECINOS;
  const nombre = pool[Math.floor(Math.random() * pool.length)];
  const campana = game.playlists.contents.flatMap(p => p.sounds.contents).find(s => s.getFlag(MOD, "slug") === "campana");
  campana?.parent.playSound(campana);
  ChatMessage.create({ content: `<div class="mr-rima-loteria"><img src="modules/${MOD}/assets/scenes/portada.webp" alt=""><h3>La lotería de ${esc(r.ciudad)}</h3>
    <p>La campana suena tres veces. El Portavoz mete la mano en el bote de hueso y lee, sin levantar la vista:</p><p class="nombre">${esc(nombre)}</p>
    <p class="nota">Esta noche lo dejarán sin abrigo más allá de la empalizada. Salvo que alguien haga algo.</p></div>` });
}

/* ---------- Configuración ---------- */
Hooks.on("renderSettings", (app, html) => {
  if (!game.user.isGM) return;
  const raiz = html instanceof HTMLElement ? html : html[0];
  const sitio = raiz?.querySelector("section.settings");
  if (!sitio || raiz.querySelector(".mr-rima-ajustes")) return;
  const sec = document.createElement("section");
  sec.className = "mr-rima-ajustes flexcol";
  sec.innerHTML = `<h4 class="divider">MR- La Rima de la Doncella</h4>
    <button type="button" data-rima="importar"><i class="fa-solid fa-file-import" inert></i> Importar la aventura</button>
    <button type="button" data-rima="loteria"><i class="fa-solid fa-snowflake" inert></i> Lotería de Auril</button>`;
  sec.addEventListener("click", ev => {
    const a = ev.target.closest("button[data-rima]")?.dataset.rima;
    if (a === "importar") importarAventura({ confirmar: true });
    else if (a === "loteria") loteria();
  });
  sitio.after(sec);
});

Hooks.once("ready", async () => {
  game.modules.get(MOD).api = { importarAventura, loteria };
  await registrarDireccion(game.modules.get("mr-direccion")?.api);
  if (!game.modules.get("mr-direccion")?.active && game.user.isGM)
    ui.notifications.warn("La Rima: activa el módulo «MR- Dirección» para tener la barra del Narrador.", { permanent: true });
  // En `ready` activeGM puede no estar resuelto todavía: solo se descarta si ya hay otro Narrador activo.
  const otroGM = game.users.activeGM && game.users.activeGM !== game.user;
  if (game.user.isGM && !otroGM && !game.settings.get(MOD, "importada") && mundoVacio()) {
    try { await importarAventura(); } catch (e) { console.error(`${MOD} | importación automática fallida`, e); }
  }
});
