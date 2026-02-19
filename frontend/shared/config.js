// Centralized configuration for the Medical RAG frontend
// Change the backend URL here to update it across the entire application

(function() {
  'use strict';
  
  // Auto-detect base path from current location
  // Works in both development (file://) and production (http/https)
  function detectBasePath() {
    const pathname = window.location.pathname || "/";

    // Case 1: app is deployed under a /frontend prefix (common in this repo)
    if (pathname.includes("/frontend/")) {
      const frontendIndex = pathname.indexOf("/frontend/");
      return pathname.substring(0, frontendIndex + "/frontend".length);
    }
    if (pathname === "/frontend" || pathname.endsWith("/frontend")) {
      return pathname === "/frontend" ? "/frontend" : pathname;
    }

    // Case 2: app is served with frontend folder as the web root (Live Server / Five Server)
    // Example: /modules/patient/dashboard.html -> base should be ""
    const anchors = ["/modules/", "/auth/", "/shared/", "/assets/"];
    for (const a of anchors) {
      const idx = pathname.indexOf(a);
      if (idx !== -1) return pathname.substring(0, idx); // often ""
    }

    // Case 3: /index.html at web root
    if (pathname === "/" || pathname.endsWith("/index.html")) return "";

    // Default fallback (keeps backwards compatibility if served under /frontend)
    return "";
  }

  const AppConfig = {
    // Backend API base URL
    BACKEND_URL: "http://medicalner-backend-uaenorth.uaenorth.azurecontainer.io:8000",
    
    // Frontend base path (auto-detected)
    BASE_PATH: detectBasePath(),
    
    // API endpoints (relative paths, will be appended to BACKEND_URL)
    API_ENDPOINTS: {
      // Add any endpoint-specific configurations here if needed
    },
    
    // Routing utility functions
    getPath: function (relativePath) {
      // Remove leading slash if present
      const cleanPath = relativePath.startsWith('/') ? relativePath.substring(1) : relativePath;

      // BASE_PATH may be "" when frontend is served as the web root.
      if (!this.BASE_PATH) return "/" + cleanPath;

      // Ensure base path ends with /
      const base = this.BASE_PATH.endsWith("/") ? this.BASE_PATH : this.BASE_PATH + "/";

      return base + cleanPath;
    },
    
    // Get absolute URL for a path
    getUrl: function (relativePath) {
      // origin is "null" for file://, so fallback to relative
      if (!window.location.origin || window.location.origin === "null") return this.getPath(relativePath);
      return window.location.origin + this.getPath(relativePath);
    },
    
    // Get relative path from frontend root
    getRelativePath: function(fullPath) {
      if (fullPath.startsWith(this.BASE_PATH)) {
        return fullPath.substring(this.BASE_PATH.length);
      }
      return fullPath;
    }
  };

  // Make config available globally
  window.AppConfig = AppConfig;
  
  // Also create a global routing helper for convenience
  window.getPath = function(path) {
    return AppConfig.getPath(path);
  };
  
  window.getUrl = function(path) {
    return AppConfig.getUrl(path);
  };
})();

