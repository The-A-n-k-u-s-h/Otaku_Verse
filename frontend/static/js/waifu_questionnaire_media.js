/* Load after waifu_questionnaire.js. Enhances the existing question renderer safely. */
(() => {
  const root = document.getElementById("waifu-questionnaire");
  if (!root) return;
  const prompt = document.getElementById("waifu-question-prompt");
  const options = document.getElementById("waifu-question-options");
  if (!prompt || !options) return;

  const mediaNode = (media, label) => {
    if (!media) return null;
    const wrap = document.createElement("div");
    wrap.className = "waifu-media-block";
    const imageUrl = media.gif_url || media.image_url || "";
    if (imageUrl) {
      const img = document.createElement("img");
      img.src = imageUrl;
      img.alt = label;
      img.loading = "lazy";
      img.className = "waifu-question-media";
      img.addEventListener("error", () => {
        img.replaceWith(Object.assign(document.createElement("span"), {
          className: "waifu-media-fallback",
          textContent: "Media unavailable"
        }));
      }, {once:true});
      wrap.appendChild(img);
    }
    if (media.audio_url) {
      const audio = document.createElement("audio");
      audio.controls = true;
      audio.preload = "none";
      audio.src = media.audio_url;
      audio.className = "waifu-audio";
      wrap.appendChild(audio);
    }
    return wrap.childNodes.length ? wrap : null;
  };

  const originalText = prompt.textContent;
  const observer = new MutationObserver(() => {
    const question = window.currentWaifuQuestion || null;
    if (!question || !question.prompt) return;
    if (prompt.dataset.mediaQuestionId === String(question.id)) return;
    prompt.dataset.mediaQuestionId = String(question.id);
    const node = mediaNode(question.media || {
      image_url: question.image_url,
      gif_url: question.gif_url,
      audio_url: question.audio_url
    }, "Question media");
    const old = root.querySelector(".waifu-question-media-wrap");
    if (old) old.remove();
    if (node) {
      node.classList.add("waifu-question-media-wrap");
      prompt.insertAdjacentElement("afterend", node);
    }
    options.querySelectorAll(".waifu-answer-option").forEach((button, index) => {
      const option = question.options?.[index];
      if (!option) return;
      const oldMedia = button.querySelector(".waifu-answer-media");
      if (oldMedia) oldMedia.remove();
      const media = mediaNode(option.media || {
        image_url: option.image_url,
        gif_url: option.gif_url,
        audio_url: option.audio_url
      }, "Answer option media");
      if (media) {
        media.classList.add("waifu-answer-media");
        button.appendChild(media);
      }
    });
  });
  observer.observe(root, {subtree:true, childList:true, characterData:true});
  // The core questionnaire script can expose its current object through this
  // small hook. See INSTALL_MODULE4.txt for the one-line integration.
})();
