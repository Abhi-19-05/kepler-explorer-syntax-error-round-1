// Page transition handling
document.addEventListener('DOMContentLoaded', function() {
  // Remove any fade-out class when page loads
  const fadePage = document.querySelector(".fade-page");
  if (fadePage) {
    fadePage.classList.remove("fade-out");
  }
  
  // Handle navigation clicks
  document.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", function(e) {
      // Only handle internal links
      if (this.hostname === window.location.hostname || !this.hostname) {
        e.preventDefault();
        
        const fadePage = document.querySelector(".fade-page");
        const targetUrl = this.href;
        
        // Add fade out class
        if (fadePage) {
          fadePage.classList.add("fade-out");
          
          // Wait for fade animation, then navigate
          setTimeout(() => {
            window.location.href = targetUrl;
          }, 400); // Match this with CSS transition time
        } else {
          // Fallback if no fade page
          window.location.href = targetUrl;
        }
      }
    });
  });
  
  // Handle browser back/forward buttons
  window.addEventListener('pageshow', function(event) {
    const fadePage = document.querySelector(".fade-page");
    if (fadePage) {
      fadePage.classList.remove("fade-out");
    }
  });
});

// Optional: Add loading state for external links
window.addEventListener('beforeunload', function() {
  // This ensures fade out happens even if user clicks browser refresh
  const fadePage = document.querySelector(".fade-page");
  if (fadePage) {
    fadePage.classList.add("fade-out");
  }
});