document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-lang-target]").forEach(function (node) {
    node.addEventListener("click", function () {
      window.location.href = node.getAttribute("data-lang-target");
    });
  });
});
