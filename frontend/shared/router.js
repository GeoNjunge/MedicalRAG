// Path Router - Fixes all paths in HTML to work in any environment
// This script should be loaded early, right after config.js

(function() {
  'use strict';
  
  // Wait for config to be available
  function initRouter() {
    if (!window.AppConfig) {
      // Retry after a short delay
      setTimeout(initRouter, 10);
      return;
    }
    
    const basePath = window.AppConfig.BASE_PATH;
    
    // Function to fix a path
    function fixPath(path) {
      if (!path) return path;
      
      // Skip external URLs
      if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('//')) {
        return path;
      }
      
      // Skip data URIs and anchors
      if (path.startsWith('data:') || path.startsWith('#') || path.startsWith('javascript:')) {
        return path;
      }
      
      // If path already starts with basePath, return as is
      if (path.startsWith(basePath)) {
        return path;
      }
      
      // If path starts with /frontend/, replace with basePath
      if (path.startsWith('/frontend/')) {
        return basePath + path.substring('/frontend'.length);
      }
      
      // If path starts with /frontend (without trailing slash)
      if (path === '/frontend' || path.startsWith('/frontend/')) {
        return basePath + (path === '/frontend' ? '' : path.substring('/frontend'.length));
      }
      
      // For relative paths, they should work as-is, but if they're meant to be from frontend root
      // and start with /, we need to handle them
      if (path.startsWith('/') && !path.startsWith(basePath)) {
        // This is an absolute path from root, convert to basePath relative
        return basePath + path;
      }
      
      return path;
    }
    
    // Fix all href attributes
    function fixHrefs() {
      const links = document.querySelectorAll('a[href]');
      links.forEach(link => {
        const href = link.getAttribute('href');
        const fixed = fixPath(href);
        if (fixed !== href) {
          link.setAttribute('href', fixed);
        }
      });
    }
    
    // Fix all src attributes (scripts, images, etc.)
    function fixSrcs() {
      const elements = document.querySelectorAll('[src]');
      elements.forEach(el => {
        const src = el.getAttribute('src');
        const fixed = fixPath(src);
        if (fixed !== src) {
          el.setAttribute('src', fixed);
        }
      });
    }
    
    // Fix all link href attributes (CSS)
    function fixLinkHrefs() {
      const links = document.querySelectorAll('link[href]');
      links.forEach(link => {
        const href = link.getAttribute('href');
        const fixed = fixPath(href);
        if (fixed !== href) {
          link.setAttribute('href', fixed);
        }
      });
    }
    
    // Run fixes immediately and also when DOM is ready
    // This ensures paths are fixed even if script loads after DOM
    function runFixes() {
      fixHrefs();
      fixSrcs();
      fixLinkHrefs();
    }
    
    // Run immediately if possible
    if (document.body) {
      runFixes();
    }
    
    // Also run when DOM is ready (if not already)
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', runFixes);
    } else {
      // DOM already loaded, run immediately
      setTimeout(runFixes, 0);
    }
    
    // Also fix dynamically added elements
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            // Fix hrefs
            if (node.hasAttribute && node.hasAttribute('href')) {
              const href = node.getAttribute('href');
              const fixed = fixPath(href);
              if (fixed !== href) {
                node.setAttribute('href', fixed);
              }
            }
            // Fix srcs
            if (node.hasAttribute && node.hasAttribute('src')) {
              const src = node.getAttribute('src');
              const fixed = fixPath(src);
              if (fixed !== src) {
                node.setAttribute('src', fixed);
              }
            }
            // Fix nested elements
            const nestedLinks = node.querySelectorAll && node.querySelectorAll('a[href], [src], link[href]');
            if (nestedLinks) {
              nestedLinks.forEach(el => {
                const attr = el.hasAttribute('href') ? 'href' : 'src';
                const value = el.getAttribute(attr);
                const fixed = fixPath(value);
                if (fixed !== value) {
                  el.setAttribute(attr, fixed);
                }
              });
            }
          }
        });
      });
    });
    
    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true
    });
  }
  
  // Start initialization
  initRouter();
})();

