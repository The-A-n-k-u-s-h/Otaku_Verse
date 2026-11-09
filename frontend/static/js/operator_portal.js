(() => {
  const form = document.getElementById('operator-change-form');
  if (!form) return;
  const message = document.getElementById('operator-change-message');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = form.querySelector('button[type="submit"]');
    const data = new FormData(form);
    const parseOptionalJson = (value, field) => {
      if (!value.trim()) return {};
      try { return JSON.parse(value); }
      catch { throw new Error(`${field} must contain valid JSON.`); }
    };
    let payload;
    try {
      payload = {
        feature: form.dataset.feature,
        action: data.get('action'),
        summary: data.get('summary'),
        before: parseOptionalJson(data.get('before') || '', 'Before'),
        after: parseOptionalJson(data.get('after') || '', 'After')
      };
    } catch (error) {
      message.textContent = error.message;
      return;
    }
    submit.disabled = true;
    message.textContent = 'Saving...';
    try {
      const response = await fetch('/operator/api/activity', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.message || 'Could not save this change.');
      message.textContent = 'Change recorded. Refreshing activity...';
      window.location.reload();
    } catch (error) {
      message.textContent = error.message;
    } finally {
      submit.disabled = false;
    }
  });
})();
