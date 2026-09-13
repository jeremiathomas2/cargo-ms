(function(){
  "use strict";

  var ROOT = document.getElementById("page-content");
  var EXCLUDED_PREFIXES = ["/admin/", "/media/", "/static/", "mailto:", "tel:", "javascript:"];
  var lastPath = window.location.pathname + window.location.search;
  var fetching = false;

  function isInternal(href){
    if(!href) return false;
    if(href.charAt(0) === "#") return false;
    if(/^(https?:)?\/\//i.test(href)){
      try{
        var url = new URL(href, window.location.origin);
        return url.origin === window.location.origin;
      }catch(e){ return false; }
    }
    return true;
  }

  function isExcluded(href){
    var path = href.split("#")[0].split("?")[0].toLowerCase();
    for(var i=0;i<EXCLUDED_PREFIXES.length;i++){
      if(path.indexOf(EXCLUDED_PREFIXES[i]) === 0) return true;
    }
    return false;
  }

  function canPjax(link){
    if(!link || link.hasAttribute("data-no-pjax")) return false;
    if(link.getAttribute("download") !== null) return false;
    if((link.getAttribute("target") || "").toLowerCase() === "_blank") return false;
    var href = link.getAttribute("href");
    if(!href) return false;
    if(!isInternal(href)) return false;
    if(isExcluded(href)) return false;
    return true;
  }

  function executeSwappedScripts(container){
    var scripts = container.querySelectorAll("script");
    for(var i=0;i<scripts.length;i++){
      var old = scripts[i];
      var type = (old.getAttribute("type") || "").toLowerCase();
      if(type === "application/json" || type === "application/ld+json" || type === "text/template") continue;
      var fresh = document.createElement("script");
      fresh.async = false;
      if(old.src){
        fresh.src = old.src;
      }else{
        fresh.textContent = old.textContent;
      }
      old.parentNode.replaceChild(fresh, old);
    }
  }

  function afterSwap(container){
    window.dispatchEvent(new CustomEvent("pjax:load", { detail: { container: container } }));
    if(window.Alpine && Alpine.initTree){
      try{ Alpine.initTree(container); }catch(e){}
    }
    if(window.htmx && htmx.process){
      try{ htmx.process(container); }catch(e){}
    }
    document.querySelectorAll("#page-content .reveal").forEach(function(el){
      el.classList.remove("reveal");
      void el.offsetWidth;
      el.classList.add("reveal");
    });
  }

  function updateSidebarActive(path){
    var normalized = path.split("#")[0].split("?")[0];
    document.querySelectorAll("#sidebar .nav-item").forEach(function(el){
      var href = el.getAttribute("href");
      if(!href) return;
      var base = href.split("#")[0].split("?")[0];
      if(!base || base === "/") return;
      var active = normalized === base || normalized.indexOf(base.endsWith("/") ? base : base + "/") === 0;
      el.classList.toggle("active", active);
    });
  }

  function swapContent(html, url, push){
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, "text/html");
    var title = doc.querySelector("title");
    var frag = doc.getElementById("page-content");

    if(!frag){
      window.location.href = url;
      return;
    }

    ROOT.innerHTML = frag.innerHTML;
    executeSwappedScripts(ROOT);

    if(title) document.title = title.textContent;
    document.body.classList.remove("sidebar-open");
    window.scrollTo(0, 0);
    lastPath = url.replace(window.location.origin, "");
    updateSidebarActive(lastPath);
    afterSwap(ROOT);

    if(push){
      try{ history.pushState({ path: lastPath }, "", lastPath); }catch(e){}
    }
  }

  function loadPage(url, push){
    if(fetching) return;
    fetching = true;
    fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest", "Accept": "text/html" },
      credentials: "same-origin"
    }).then(function(res){
      if(!res.ok) throw new Error("HTTP " + res.status);
      return res.text();
    }).then(function(html){
      swapContent(html, url, push);
    }).catch(function(){
      window.location.href = url;
    }).finally(function(){
      fetching = false;
    });
  }

  document.addEventListener("click", function(e){
    if(e.defaultPrevented) return;
    if(e.button !== 0) return;
    if(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var link = e.target.closest ? e.target.closest("a") : null;
    if(!link) return;
    if(!canPjax(link)) return;

    var url = link.href;
    var path = url.replace(window.location.origin, "");
    if(path === lastPath){
      e.preventDefault();
      return;
    }
    e.preventDefault();
    loadPage(url, true);
  }, true);

  window.addEventListener("popstate", function(){
    var path = window.location.pathname + window.location.search;
    if(path !== lastPath){
      loadPage(window.location.href, false);
    }
  });

  window.addEventListener("DOMContentLoaded", function(){
    updateSidebarActive(window.location.pathname);
  });

})();