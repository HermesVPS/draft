  const themeToggle = document.getElementById('theme-toggle');
  const themeLabel = document.getElementById('theme-label');

  // Toggle change: update theme, label & store in localStorage
  themeToggle.addEventListener('change', function () {
    const isDark = this.checked;
    const newTheme = isDark ? 'dark' : 'default';

    // Apply theme immediately
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    this.value = newTheme;

    // Update label text
    if (themeLabel) {
      themeLabel.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }
  });

  // Apply stored theme on load
  document.addEventListener('DOMContentLoaded', function () {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
      document.documentElement.setAttribute('data-theme', storedTheme);
      themeToggle.checked = storedTheme === 'dark';

      // Update label accordingly
      if (themeLabel) {
        themeLabel.textContent = storedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
      }
    }
  });