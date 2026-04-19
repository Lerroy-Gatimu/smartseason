/**
 * SmartSeason — main.js
 * Vanilla JS only. No frameworks.
 *
 * Handles:
 *  1. Hamburger / sidebar drawer toggle (mobile)
 *  2. Auto-dismiss flash messages
 *  3. Active nav link highlighting
 *  4. Confirm-before-delete buttons
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── 1. Hamburger / Sidebar Drawer ────────────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const sidebar   = document.getElementById('sidebar');
  const overlay   = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('visible');
    hamburger.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    // Prevent body scroll while drawer is open
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', function () {
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  // Close when clicking the overlay
  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar on escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
      closeSidebar();
    }
  });

  // Close sidebar when a nav link is tapped (on mobile)
  if (sidebar) {
    sidebar.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 768) {
          closeSidebar();
        }
      });
    });
  }

  // ── 2. Active Nav Link ───────────────────────────────────────────────────
  // Highlights the sidebar link that matches the current URL path
  const currentPath = window.location.pathname;

  document.querySelectorAll('.sidebar-nav a').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    } else if (href === '/dashboard/' && currentPath === '/dashboard/') {
      link.classList.add('active');
    }
  });

  // ── 3. Auto-Dismiss Flash Messages ──────────────────────────────────────
  // Messages disappear after 4.5 seconds, or immediately on close click
  document.querySelectorAll('.alert').forEach(function (alert) {
    // Close button
    var closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        dismissAlert(alert);
      });
    }

    // Auto dismiss after 4500ms
    setTimeout(function () {
      dismissAlert(alert);
    }, 4500);
  });

  function dismissAlert(alert) {
    alert.style.transition = 'opacity .3s ease, transform .3s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(20px)';
    setTimeout(function () {
      if (alert.parentNode) {
        alert.parentNode.removeChild(alert);
      }
    }, 320);
  }

  // ── 4. Confirm Before Delete ─────────────────────────────────────────────
  // Any form with data-confirm="..." will show a browser confirm dialog
  // before submitting. Used on delete forms.
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var msg = form.getAttribute('data-confirm') || 'Are you sure?';
      if (!window.confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // ── 5. Filter Form Auto-Submit on Select Change ──────────────────────────
  // On the field list page, changing a dropdown filter auto-submits
  document.querySelectorAll('.filter-bar select').forEach(function (sel) {
    sel.addEventListener('change', function () {
      this.closest('form').submit();
    });
  });

});
