// Las URL con /va/ son explícitas; las URL sin prefijo admiten detección.
(() => {
  const script = document.currentScript;
  const routes = { es: script.dataset.es, va: script.dataset.va };
  const current = script.dataset.language;
  const storageKey = "edusemanari.idioma";
  const valid = language => language === "es" || language === "va";
  const explicit = new URLSearchParams(location.search).get("lang");
  let preferred;
  try {
    preferred = localStorage.getItem(storageKey);
    if (valid(explicit)) localStorage.setItem(storageKey, explicit);
  } catch (_) {
    // El selector sigue funcionando mediante ?lang= aunque se bloquee el almacenamiento.
  }
  if (valid(explicit)) preferred = explicit;
  else if (!valid(preferred)) {
    preferred = "es";
    for (const locale of navigator.languages || [navigator.language]) {
      if (/^(ca|va)(-|$)/i.test(locale)) { preferred = "va"; break; }
      if (/^es(-|$)/i.test(locale)) { preferred = "es"; break; }
    }
  }
  if ((current === "es" || valid(explicit)) && preferred !== current && routes[preferred]) {
    const target = new URL(routes[preferred], location.origin);
    target.search = location.search;
    target.hash = location.hash;
    location.replace(target.href);
    return;
  }
  document.addEventListener("click", event => {
    const link = event.target.closest?.("a[data-idioma]");
    if (!link || !valid(link.dataset.idioma)) return;
    try { localStorage.setItem(storageKey, link.dataset.idioma); } catch (_) {}
  });
})();
