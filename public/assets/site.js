document.addEventListener("DOMContentLoaded", function () {
  var sections = document.querySelectorAll("[data-reveal]");
  var introOverlay = document.querySelector(".intro-overlay");
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

      introOverlay.addEventListener("click", dismissIntro);
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
});
