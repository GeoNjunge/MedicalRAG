(function () {
  "use strict";

  // Get base path from config (will be set after config.js loads)
  function getBasePath() {
    return window.AppConfig?.BASE_PATH || "/frontend";
  }

  const navigationConfig = {
    doctor: [
      { name: "Dashboard", path: () => `${getBasePath()}/modules/doctor/dashboard.html` },
      { name: "Patient Management", path: () => `${getBasePath()}/modules/doctor/patients/manage.html` },
      { name: "Medical Screening", path: () => `${getBasePath()}/modules/doctor/screening/screening.html` },
      { name: "Analytics", path: () => `${getBasePath()}/modules/doctor/analytics/analytics.html` },
      { name: "Profile", path: () => `${getBasePath()}/modules/doctor/profile/profile.html` },
    ],
    patient: [
      { name: "Dashboard", path: () => `${getBasePath()}/modules/patient/dashboard.html` },
      { name: "My Records", path: () => `${getBasePath()}/modules/patient/records/view.html` },
      { name: "Profile", path: () => `${getBasePath()}/modules/patient/profile/profile.html` },
    ],
  };

  function buildNavHtml(role, user) {
    const items = navigationConfig[role] || [];
    const currentPath = window.location.pathname;

    const linksHtml = items
      .map((item) => {
        const path = typeof item.path === 'function' ? item.path() : item.path;
        const active = currentPath === path || currentPath.endsWith(path);
        return `<a href="${path}" class="nav-link${active ? " active" : ""}">
          <span>${item.name}</span>
        </a>`;
      })
      .join("");

    const userHtml = user
      ? `<div class="user-info">
            <span class="user-role">${user.role}</span>
            <span class="user-name">${user.full_name || user.username}</span>
            <button class="btn-logout" id="nav-logout-btn">Logout</button>
         </div>`
      : "";

    return `
      <nav class="app-nav">
        <div class="nav-container">
          <div class="nav-brand">
            <h1>Medical RAG</h1>
          </div>
          <div class="nav-links">
            ${linksHtml}
          </div>
          ${userHtml}
        </div>
      </nav>
    `;
  }

  function renderNavigation(options) {
    const { role, user, containerId = "navigation" } = options;
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = buildNavHtml(role, user);

    // Attach logout handler if AuthApp is available
    const logoutBtn = document.getElementById("nav-logout-btn");
    if (logoutBtn && window.AuthApp && typeof window.AuthApp.logout === "function") {
      logoutBtn.addEventListener("click", function (e) {
        e.preventDefault();
        window.AuthApp.logout();
      });
    }
  }

  window.Navigation = {
    config: navigationConfig,
    render: renderNavigation,
  };
})();
