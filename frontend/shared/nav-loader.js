// Navigation Loader - Add to existing shared JS or create new file
document.addEventListener("DOMContentLoaded", () => {
  // Highlight active link
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-links a");
  const basePath = window.AppConfig?.BASE_PATH || "/frontend";

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    // Normalize paths for comparison using base path
    const normalizedHref = href.replace(basePath, "").replace(/^\//, "");
    const normalizedPath = currentPath.replace(basePath, "").replace(/^\//, "");
    if (normalizedPath.includes(normalizedHref) || currentPath === href || currentPath.endsWith(href)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
});
