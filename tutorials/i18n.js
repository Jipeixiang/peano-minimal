// Language switch shared by every page.
// Elements marked data-lang="zh-CN" or data-lang="en" are shown only in that language (see site.css).
// Buttons marked data-lang-btn="zh-CN" / "en" switch the language; the choice is remembered per browser.
(function () {
  var KEY = "peano-notes-lang";
  var LANGS = ["zh-CN", "en"];

  function stored() {
    try {
      var v = localStorage.getItem(KEY);
      if (LANGS.indexOf(v) >= 0) return v;
    } catch (e) {}
    return null;
  }

  function initial() {
    return stored() || "en";
  }

  function apply(lang) {
    document.documentElement.lang = lang;
    var buttons = document.querySelectorAll("[data-lang-btn]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute("aria-pressed", String(buttons[i].getAttribute("data-lang-btn") === lang));
    }
    document.dispatchEvent(new CustomEvent("langchange", { detail: lang }));
  }

  window.SiteLang = {
    get: function () { return document.documentElement.lang === "zh-CN" ? "zh-CN" : "en"; },
    set: function (lang) {
      try { localStorage.setItem(KEY, lang); } catch (e) {}
      apply(lang);
    },
    // Pick the string for the current language from {"zh-CN": ..., "en": ...}.
    pick: function (obj) { return obj[this.get()] || obj.en || obj["zh-CN"] || ""; }
  };

  document.documentElement.lang = initial();

  function wire() {
    var buttons = document.querySelectorAll("[data-lang-btn]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function () { SiteLang.set(this.getAttribute("data-lang-btn")); });
    }
    apply(SiteLang.get());
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
