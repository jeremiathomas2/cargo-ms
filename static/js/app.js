(function(){
  "use strict";

  /* ============ THEME TOGGLE ============ */
  var htmlEl = document.documentElement;
  var themeBtn = document.getElementById("themeToggle");
  window._tileLayer = null;
  var THEME_KEY = "shehena-theme";

  function getStoredTheme(){
    try{ return localStorage.getItem(THEME_KEY); }catch(e){ return null; }
  }
  function setStoredTheme(t){
    try{ localStorage.setItem(THEME_KEY, t); }catch(e){}
  }

  function syncKnobIcon(t){
    if(!themeBtn) return;
    var useEl = themeBtn.querySelector(".knob svg use");
    if(!useEl) return;
    var val = t === "dark" ? "#i-moon" : "#i-sun";
    useEl.setAttribute("href", val);
    useEl.setAttributeNS("http://www.w3.org/1999/xlink", "href", val);
  }
  function syncMapTiles(t){
    if(window.L && window._tileLayer){
      var url = t==="dark"
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
      try{ window._tileLayer.setUrl(url); }catch(e){}
    }
  }

  function writeThemeAttrs(t){
    htmlEl.setAttribute("data-theme", t);
    if(t === "dark"){ htmlEl.classList.add("dark"); }
    else { htmlEl.classList.remove("dark"); }
  }

  function applyTheme(t){
    writeThemeAttrs(t);
    setStoredTheme(t);
    syncKnobIcon(t);
    syncMapTiles(t);
  }

  (function initTheme(){
    var current = htmlEl.getAttribute("data-theme") || "light";
    var stored = getStoredTheme();

    if(!stored){
      setStoredTheme(current);
    } else if(stored !== current){
      writeThemeAttrs(stored);
      current = stored;
    }

    syncKnobIcon(current);

    if(window.L){
      syncMapTiles(current);
    } else if(document.readyState === "loading"){
      document.addEventListener("DOMContentLoaded", function once(){
        syncMapTiles(htmlEl.getAttribute("data-theme"));
      }, { once: true });
    }

    if(window.matchMedia){
      try{
        var mql = window.matchMedia("(prefers-color-scheme: dark)");
        var listener = function(e){
          if(!getStoredTheme()){
            applyTheme(e.matches ? "dark" : "light");
          }
        };
        if(mql.addEventListener) mql.addEventListener("change", listener);
        else if(mql.addListener) mql.addListener(listener);
      }catch(err){}
    }
  })();

  if(themeBtn){
    themeBtn.addEventListener("click", function(){
      var next = htmlEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }

  /* ============ SIDEBAR TOGGLES ============ */
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("backdrop");
  var collapseBtn = document.getElementById("collapseToggle");

  if(collapseBtn && sidebar){
    collapseBtn.addEventListener("click", function(){
      sidebar.classList.toggle("collapsed");
    });
  }
  var menuBtn = document.getElementById("menuToggle");
  if(menuBtn && sidebar){
    menuBtn.addEventListener("click", function(){
      sidebar.classList.add("mobile-open");
    });
  }
  if(backdrop){
    backdrop.addEventListener("click", function(){
      sidebar.classList.remove("mobile-open");
    });
  }

  /* ============ DROPDOWNS ============ */
  function closeAllDropdowns(){
    document.querySelectorAll(".dropdown.open").forEach(function(d){ d.classList.remove("open"); });
  }
  function setupDropdown(btnId, dropId){
    var btn = document.getElementById(btnId), drop = document.getElementById(dropId);
    if(!btn || !drop) return;
    btn.addEventListener("click", function(e){
      e.stopPropagation();
      e.preventDefault();
      var isOpen = drop.classList.contains("open");
      closeAllDropdowns();
      if(!isOpen) drop.classList.add("open");
    });
    drop.addEventListener("click", function(e){
      if(e.target.closest("a") || e.target.closest("button[type='submit']")) return;
      e.stopPropagation();
    });
  }
  setupDropdown("notifBtn", "notifDropdown");
  setupDropdown("userBtn", "userDropdown");
  document.addEventListener("click", closeAllDropdowns);
  document.addEventListener("keydown", function(e){
    if(e.key === "Escape") closeAllDropdowns();
  });

  /* ============ GLOBAL SEARCH (shipment filter helper ============ */
  var searchInput = document.getElementById("searchInput");
  if(searchInput){
    searchInput.addEventListener("input", function(){
      var q = searchInput.value.trim().toLowerCase();
      document.querySelectorAll(".ship-row").forEach(function(row){
        if(!q){ row.style.display = ""; return; }
        var txt = row.textContent.toLowerCase();
        row.style.display = txt.indexOf(q) > -1 ? "" : "none";
      });
      if(window.htmx){
        // optional HTMX integration
      }
    });
  }

  /* ============ HTMX CONFIG ============ */
  if(window.htmx){
    document.body.addEventListener("htmx:afterSwap", function(e){
      if(window.Alpine) Alpine.initTree(e.detail.target);
    });
  }

})();
