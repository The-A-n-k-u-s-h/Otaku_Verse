(() => {
  const output = document.getElementById("waifu-ai-output");
  if (!output) return;
  const show = (message, isError = false) => {
    output.textContent = message;
    output.dataset.state = isError ? "error" : "success";
  };
  async function submitForm(form, endpoint) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      show("Generating drafts. Please wait...");
      try {
        const payload = Object.fromEntries(new FormData(form).entries());
        const response = await fetch(endpoint, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "same-origin",
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "Generation failed.");
        show(data.message);
      } catch (error) {
        show(error.message || "An unexpected error occurred.", true);
      } finally {
        button.disabled = false;
      }
    });
  }
  submitForm(document.getElementById("waifu-question-generator"), "/operator/waifu/ai/questions/generate");
  submitForm(document.getElementById("waifu-character-discovery"), "/operator/waifu/ai/characters/discover");
})();
