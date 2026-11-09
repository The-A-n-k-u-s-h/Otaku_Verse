(() => {
  const root = document.getElementById("waifu-questionnaire");
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  let currentQuestion = null;
  let busy = false;

  function message(text, error = false) {
    $("waifu-question-feedback").textContent = text;
    $("waifu-question-feedback").dataset.state = error ? "error" : "success";
  }
  function renderProgress(progress = {}) {
    const answered = Number(progress.answered || 0);
    const total = Number(progress.available_questions || 0);
    $("waifu-progress-count").textContent = `${answered} answered`;
    $("waifu-progress-label").textContent = total ? `${answered} of ${total} approved questions` : "No approved questions yet";
    $("waifu-progress-fill").style.width = total ? `${Math.min(100, answered / total * 100)}%` : "0%";
  }
  function renderQuestion(question) {
    currentQuestion = question;
    const container = $("waifu-question-options");
    container.replaceChildren();
    if (!question) {
      $("waifu-question-prompt").textContent = "Your profile questionnaire is complete";
      $("waifu-question-category").textContent = "Your answers have been saved.";
      $("waifu-start-button").hidden = true;
      $("waifu-profile-preview").hidden = false;
      loadProfiles();
      return;
    }
    $("waifu-question-prompt").textContent = question.prompt;
    $("waifu-question-category").textContent =
      `${question.category} · ${question.profile_type === "personality" ? "Personality" : "Romantic preference"}`;
    question.options.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "waifu-answer-option";
      button.textContent = option.text;
      button.addEventListener("click", () => submitAnswer(option.id));
      container.appendChild(button);
    });
    $("waifu-start-button").hidden = true;
  }
  async function api(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: {"Content-Type": "application/json", ...(options.headers || {})},
      ...options
    });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.message || "Request failed.");
    return data;
  }
  async function start() {
    if (busy) return;
    busy = true;
    $("waifu-start-button").disabled = true;
    try {
      const data = await api("/api/waifu/profile/start", {method: "POST", body: "{}"});
      renderProgress(data.progress);
      if (!data.question) {
        renderQuestion(null);
        message("There are no approved questions available yet.");
      } else {
        renderQuestion(data.question);
        message("Choose the answer that best represents you.");
      }
    } catch (error) {
      message(error.message, true);
      $("waifu-start-button").disabled = false;
    } finally { busy = false; }
  }
  async function submitAnswer(optionId) {
    if (busy || !currentQuestion) return;
    busy = true;
    document.querySelectorAll(".waifu-answer-option").forEach((button) => button.disabled = true);
    try {
      const data = await api("/api/waifu/profile/answer", {
        method: "POST",
        body: JSON.stringify({question_id: currentQuestion.id, option_id: optionId})
      });
      renderProgress(data.progress);
      renderQuestion(data.next_question);
      if (data.completed) message("Both profile sections have been collected.");
      else message("Answer saved. Here is your next question.");
    } catch (error) {
      message(error.message, true);
      document.querySelectorAll(".waifu-answer-option").forEach((button) => button.disabled = false);
    } finally { busy = false; }
  }
  function renderScores(targetId, values) {
    const target = $(targetId);
    target.replaceChildren();
    const entries = Object.entries(values || {});
    if (!entries.length) {
      target.textContent = "No answers recorded yet.";
      return;
    }
    entries.forEach(([key, item]) => {
      const line = document.createElement("div");
      line.className = "waifu-score-row";
      const label = document.createElement("span");
      label.textContent = key.replaceAll("_", " ");
      const score = document.createElement("strong");
      score.textContent = `${item.score}/100`;
      line.append(label, score);
      target.appendChild(line);
    });
  }
  async function loadProfiles() {
    try {
      const data = await api("/api/waifu/profile/profiles");
      renderScores("waifu-personality-scores", data.profiles.personality);
      renderScores("waifu-romantic-scores", data.profiles.romantic);
    } catch (error) { message(error.message, true); }
  }
  $("waifu-start-button").addEventListener("click", start);
})();
