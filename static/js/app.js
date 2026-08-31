(function(){
  "use strict";

  /* ============ THEME TOGGLE ============ */
  var htmlEl = document.documentElement;
  var themeBtn = document.getElementById("themeToggle");
  window._tileLayer = null;

  function applyTheme(t){
    htmlEl.setAttribute("data-theme", t);
    if(t === "dark"){ htmlEl.classList.add("dark"); }
    else { htmlEl.classList.remove("dark"); }
    if(themeBtn){
      var useEl = themeBtn.querySelector(".knob svg use");
      if(useEl){ useEl.setAttribute("href", t==="dark" ? "#i-moon" : "#i-sun"); }
    }
    try{ localStorage.setItem("shehena-theme", t); }catch(e){}
    if(window.L && window._tileLayer){
      var url = t==="dark"
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
      window._tileLayer.setUrl(url);
    }
  }
  if(themeBtn){
    themeBtn.addEventListener("click", function(){
      applyTheme(htmlEl.getAttribute("data-theme")==="dark" ? "light" : "dark");
    });
  }
  (function initTheme(){
    var saved = null;
    try{ saved = localStorage.getItem("shehena-theme"); }catch(e){}
    if(!saved && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) saved = "dark";
    applyTheme(saved || "light");
  })();

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
  function setupDropdown(btnId, dropId){
    var btn = document.getElementById(btnId), drop = document.getElementById(dropId);
    if(!btn || !drop) return;
    btn.addEventListener("click", function(e){
      e.stopPropagation();
      var isOpen = drop.classList.contains("open");
      document.querySelectorAll(".dropdown.open").forEach(function(d){ d.classList.remove("open"); });
      if(!isOpen) drop.classList.add("open");
    });
  }
  setupDropdown("notifBtn", "notifDropdown");
  setupDropdown("userBtn", "userDropdown");
  document.addEventListener("click", function(){
    document.querySelectorAll(".dropdown.open").forEach(function(d){ d.classList.remove("open"); });
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
