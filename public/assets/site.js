document.addEventListener("DOMContentLoaded", function () {
  var sections = document.querySelectorAll("[data-reveal]");
  var introOverlay = document.querySelector(".intro-overlay");
  var introEnterButton = document.querySelector(".intro-overlay-enter");
  var introStorageKey = "tyler_intro_dismissed";

  function canUseStorage() {
    try {
      return Boolean(window.sessionStorage);
    } catch (error) {
      return false;
    }
  }

  function introWasDismissed() {
    if (!canUseStorage()) {
      return false;
    }
    return window.sessionStorage.getItem(introStorageKey) === "1";
  }

  function clearIntroDismissed() {
    if (!canUseStorage()) {
      return;
    }
    window.sessionStorage.removeItem(introStorageKey);
  }

  function markIntroDismissed() {
    if (!canUseStorage()) {
      return;
    }
    window.sessionStorage.setItem(introStorageKey, "1");
  }

  function isReloadNavigation() {
    var entries = window.performance && window.performance.getEntriesByType
      ? window.performance.getEntriesByType("navigation")
      : [];

    if (entries && entries.length > 0) {
      return entries[0].type === "reload";
    }

    if (window.performance && window.performance.navigation) {
      return window.performance.navigation.type === 1;
    }

    return false;
  }

  function dismissIntro() {
    if (!introOverlay || introOverlay.classList.contains("is-exiting")) {
      return;
    }

    markIntroDismissed();
    introOverlay.classList.add("is-exiting");
    document.documentElement.classList.remove("intro-locked");
    document.body.classList.remove("intro-locked");

    window.setTimeout(function () {
      if (introOverlay && introOverlay.parentNode) {
        introOverlay.parentNode.removeChild(introOverlay);
      }
    }, 900);
  }

  if (introOverlay) {
    if (isReloadNavigation()) {
      clearIntroDismissed();
    }

    if (introWasDismissed()) {
      introOverlay.parentNode.removeChild(introOverlay);
    } else {
      document.documentElement.classList.add("intro-locked");
      document.body.classList.add("intro-locked");

      if (introEnterButton) {
        introEnterButton.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          dismissIntro();
        });
      }

      /* Safety net: the overlay is one big "enter" target, so a click
         anywhere on it (not just the button) dismisses it too. */
      introOverlay.addEventListener("click", function () {
        dismissIntro();
      });

      introOverlay.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          dismissIntro();
        }
      });
    }
  }

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    sections.forEach(function (section) {
      observer.observe(section);
    });
  } else {
    sections.forEach(function (section) {
      section.classList.add("is-visible");
    });
  }

  document.querySelectorAll("[data-year]").forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });

  if (window.renderMathInElement) {
    document.querySelectorAll(".article-shell").forEach(function (node) {
      window.renderMathInElement(node, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false }
        ],
        throwOnError: false
      });
    });
  }

  /* ── Magazine edition: page-turn transitions between internal pages ── */
  var magazineRoot = document.body.classList.contains("magazine");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (magazineRoot && !reduceMotion) {
    document.body.classList.add("is-page-in");

    document.addEventListener("click", function (event) {
      if (event.defaultPrevented || event.button !== 0) {
        return;
      }
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }
      var target = event.target;
      while (target && target !== document && !(target.tagName && target.tagName.toLowerCase() === "a")) {
        target = target.parentNode;
      }
      if (!target || target.tagName.toLowerCase() !== "a") {
        return;
      }
      var href = target.getAttribute("href") || "";
      if (!href || href.charAt(0) === "#") {
        return;
      }
      if (target.target && target.target !== "_self") {
        return;
      }
      if (target.origin !== window.location.origin) {
        return;
      }
      if (/\.(pdf|zip|png|jpe?g|webp|gif|svg|mp4|ico)([?#].*)?$/i.test(href)) {
        return;
      }
      var destination = new URL(href, window.location.href).href;
      if (destination === window.location.href) {
        return;
      }
      event.preventDefault();
      document.body.classList.add("is-turning-out");
      window.setTimeout(function () {
        window.location.href = destination;
      }, 460);
    });

    window.addEventListener("pagehide", function () {
      document.body.classList.remove("is-turning-out");
    });

    window.addEventListener("pageshow", function (event) {
      if (event.persisted) {
        document.body.classList.remove("is-turning-out");
      }
    });
  }
});
