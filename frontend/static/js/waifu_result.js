(() => {
  const loading = document.getElementById("waifu-result-loading");
  const errorPanel = document.getElementById("waifu-result-error");
  const errorMessage = document.getElementById("waifu-result-error-message");
  const content = document.getElementById("waifu-result-content");

  function showError(message) {
    if (loading) loading.hidden = true;
    if (content) content.hidden = true;
    if (errorPanel) errorPanel.hidden = false;
    if (errorMessage) {
      errorMessage.textContent = message || "An unexpected error occurred.";
    }
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value ?? "";
  }

  function renderResult(data) {
    const result = data?.result || {};
    const character = result.character || {};
    const scores = result.compatibility || {};
    const explanation = result.explanation || {};

    setText("match-headline", explanation.headline);
    setText("match-summary", explanation.summary);
    setText("match-name", character.name);
    setText("match-anime", character.anime_title);
    setText("match-description", character.description);
    setText("match-biography", character.biography);
    setText("score-overall", scores.overall !== undefined ? `${scores.overall}%` : "");
    setText("score-personality", scores.personality !== undefined ? `${scores.personality}%` : "");
    setText("score-romantic", scores.romantic !== undefined ? `${scores.romantic}%` : "");
    setText("personality-reason", explanation.personality_reason);
    setText("romantic-reason", explanation.romantic_reason);
    setText("compatibility-message", explanation.compatibility_message);

    const image = document.getElementById("match-image");
    const gif = document.getElementById("match-gif");
    if (image) {
      image.hidden = !character.image_url;
      if (character.image_url) image.src = character.image_url;
      else image.removeAttribute("src");
      image.onerror = () => { image.hidden = true; };
    }
    if (gif) {
      gif.hidden = !character.gif_url;
      if (character.gif_url) gif.src = character.gif_url;
      else gif.removeAttribute("src");
      gif.onerror = () => { gif.hidden = true; };
    }

    const list = document.getElementById("strongest-connections");
    if (list) {
      list.replaceChildren();
      (explanation.strongest_connections || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
      });
    }

    if (loading) loading.hidden = true;
    if (errorPanel) errorPanel.hidden = true;
    if (content) content.hidden = false;
  }

  async function loadResult() {
    try {
      const response = await fetch("/api/waifu/result/", {
        method: "GET",
        credentials: "same-origin",
        headers: { Accept: "application/json" }
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data?.message || "Could not load your match.");
      }
      renderResult(data);
    } catch (error) {
      showError(error.message);
    }
  }

  document.addEventListener("DOMContentLoaded", loadResult);
})();