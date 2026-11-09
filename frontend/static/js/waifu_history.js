(() => {
  const list = document.getElementById("history-list");
  const status = document.getElementById("history-status");
  const clearButton = document.getElementById("clear-history");
  const dialog = document.getElementById("history-detail-dialog");
  const detailContent = document.getElementById("history-detail-content");

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  async function api(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: { "Accept": "application/json", ...(options.headers || {}) },
      ...options
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || "Request failed.");
    }
    return data;
  }

  function makeCard(record) {
    const card = element("article", "history-card");
    if (record.image_url) {
      const image = element("img", "history-image");
      image.src = record.image_url;
      image.alt = record.character_name;
      image.loading = "lazy";
      image.onerror = () => image.remove();
      card.appendChild(image);
    }

    const body = element("div", "history-card-body");
    body.appendChild(element("p", "history-anime", record.anime_title));
    body.appendChild(element("h2", "", record.character_name));
    body.appendChild(element("strong", "history-score",
      `${Number(record.overall_score).toFixed(1)}% compatibility`));
    body.appendChild(element("p", "history-date", record.created_at));

    const actions = element("div", "history-actions");
    const view = element("button", "history-button", "View details");
    view.type = "button";
    view.addEventListener("click", () => showDetail(record.id));

    const remove = element("button", "history-button history-button-muted", "Delete");
    remove.type = "button";
    remove.addEventListener("click", () => removeRecord(record.id));

    actions.append(view, remove);
    body.appendChild(actions);
    card.appendChild(body);
    return card;
  }

  async function loadHistory() {
    list.replaceChildren();
    status.textContent = "Loading your history...";
    try {
      const data = await api("/api/waifu/history/");
      if (!data.history.length) {
        status.textContent = "You have no saved matches yet.";
        clearButton.disabled = true;
        return;
      }
      clearButton.disabled = false;
      status.textContent = `${data.history.length} saved match(es)`;
      data.history.forEach(record => list.appendChild(makeCard(record)));
    } catch (error) {
      status.textContent = error.message;
    }
  }

  async function showDetail(id) {
    try {
      const data = await api(`/api/waifu/history/${id}`);
      const record = data.record;
      const snapshot = record.snapshot;
      const explanation = record.explanation || {};
      detailContent.replaceChildren();

      detailContent.appendChild(element("p", "history-anime",
        snapshot.character.anime_title));
      detailContent.appendChild(element("h2", "", snapshot.character.name));
      detailContent.appendChild(element("p", "",
        `Overall: ${snapshot.compatibility.overall_score}%`));
      detailContent.appendChild(element("p", "",
        `Personality: ${snapshot.compatibility.personality_score}%`));
      detailContent.appendChild(element("p", "",
        `Romantic: ${snapshot.compatibility.romantic_score}%`));
      detailContent.appendChild(element("h3", "", explanation.title || "Your match"));
      detailContent.appendChild(element("p", "", explanation.summary || ""));
      detailContent.appendChild(element("p", "", explanation.personality_fit || ""));
      detailContent.appendChild(element("p", "", explanation.romantic_fit || ""));
      detailContent.appendChild(element("p", "", explanation.overall_fit || ""));
      detailContent.appendChild(element("p", "history-disclaimer",
        explanation.caveat || "Entertainment result only."));
      dialog.showModal();
    } catch (error) {
      status.textContent = error.message;
    }
  }

  async function removeRecord(id) {
    if (!window.confirm("Delete this match from your history?")) return;
    try {
      await api(`/api/waifu/history/${id}`, { method: "DELETE" });
      await loadHistory();
    } catch (error) {
      status.textContent = error.message;
    }
  }

  clearButton.addEventListener("click", async () => {
    if (!window.confirm("Clear all your saved match history? This cannot be undone.")) return;
    try {
      await api("/api/waifu/history/", { method: "DELETE" });
      await loadHistory();
    } catch (error) {
      status.textContent = error.message;
    }
  });

  document.getElementById("close-history-detail").addEventListener("click", () => {
    dialog.close();
  });

  document.addEventListener("DOMContentLoaded", loadHistory);
})();
