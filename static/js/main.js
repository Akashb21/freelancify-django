/* Main Freelancify Interactive Script */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // 2. Notifications Popover Toggle
  const notifBtn = document.getElementById('notifications-dropdown-btn');
  const notifMenu = document.getElementById('notifications-dropdown-menu');

  if (notifBtn && notifMenu) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!notifMenu.contains(e.target) && !notifBtn.contains(e.target)) {
        notifMenu.classList.add('hidden');
      }
    });
  }

  // 3. Auto-dismiss Toast Alerts
  const toastAlerts = document.querySelectorAll('.toast-alert');
  toastAlerts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  });
});
