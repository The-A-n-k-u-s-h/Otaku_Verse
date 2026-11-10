(() => {
  const characterForm = document.getElementById("characterForm");
  const questionForm = document.getElementById("questionForm");
  const message = document.getElementById("formMessage");
  const showMessage = (text, bad=false) => { message.textContent=text; message.className="form-message "+(bad?"error":"success"); };

  if (characterForm) {
    characterForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(characterForm);
      const traits = {personality:{}, romantic:{}};
      document.querySelectorAll("[data-profile][data-trait]").forEach(input => {
        traits[input.dataset.profile][input.dataset.trait] = Number(input.value);
      });
      const sources = String(form.get("sources") || "").split(/\r?\n/).map(x=>x.trim()).filter(Boolean).map(line=>{
        const [name,url,verified] = line.split("|").map(x=>x.trim());
        return {name,url,verified:(verified||"").toLowerCase()==="yes"};
      });
      const payload = {
        name:form.get("name"), anime_title:form.get("anime_title"), aliases:form.get("aliases"),
        description:form.get("description"), biography:form.get("biography"),
        image_url:form.get("image_url"), gif_url:form.get("gif_url"), image_source_url:form.get("image_source_url"),
        traits, sources
      };
      try {
        const id=characterForm.dataset.id;
        const url=id?`/operator/waifu/api/characters/${id}`:"/operator/waifu/api/characters";
        await adminRequest(url,id?"PUT":"POST",payload);
        showMessage("Draft saved. Submit it for review from the character list when ready.");
        setTimeout(()=>location.href="/operator/waifu/characters",700);
      } catch(error) { showMessage(error.message,true); }
    });
  }

  if (questionForm) {
    const type=document.getElementById("profileType");
    const trait=document.getElementById("traitKey");
    const optionRows=document.getElementById("optionRows");
    const traitOptions={
      personality:["introversion","emotionality","ambition","independence","playfulness","communication","loyalty","conflict_style"],
      romantic:["affection","communication_preference","support_style","personal_space","temperament","relationship_dynamic","trust","shared_values"]
    };
    const labels={
      introversion:"Introversion",emotionality:"Emotionality",ambition:"Ambition",independence:"Independence",
      playfulness:"Playfulness",communication:"Communication",loyalty:"Loyalty",conflict_style:"Conflict style",
      affection:"Affection",communication_preference:"Communication preference",support_style:"Support style",
      personal_space:"Personal space",temperament:"Temperament",relationship_dynamic:"Relationship dynamic",
      trust:"Trust",shared_values:"Shared values"
    };
    function fillTraits(selected) {
      const values=traitOptions[type.value];
      trait.innerHTML=values.map(key=>`<option value="${key}">${labels[key]}</option>`).join("");
      if(selected && values.includes(selected)) trait.value=selected;
    }
    fillTraits(window.WAIFU_QUESTION_DATA?.trait_key);
    type.addEventListener("change",()=>fillTraits());
    document.getElementById("addOption").addEventListener("click",()=>{
      if(optionRows.children.length>=8) return showMessage("Maximum 8 options allowed.",true);
      const row=document.createElement("div"); row.className="option-row";
      row.innerHTML='<input class="option-text" placeholder="Answer option" required><input class="option-image" type="url" placeholder="Answer image URL"><input class="option-gif" type="url" placeholder="Answer GIF URL"><input class="option-audio" type="url" placeholder="Answer audio URL"><input class="option-score" type="number" min="0" max="100" value="50" required><button type="button" class="btn small danger">Remove</button>';
      row.querySelector("button").addEventListener("click",()=>row.remove()); optionRows.appendChild(row);
    });
    questionForm.addEventListener("submit",async event=>{
      event.preventDefault();
      const form=new FormData(questionForm);
      const options=[...optionRows.querySelectorAll(".option-row")].map(row=>({
        text:row.querySelector(".option-text").value.trim(),
        score:Number(row.querySelector(".option-score").value),
        image_url:row.querySelector(".option-image")?.value.trim() || "",
        gif_url:row.querySelector(".option-gif")?.value.trim() || "",
        audio_url:row.querySelector(".option-audio")?.value.trim() || ""
      }));
      const payload={
        prompt:form.get("prompt"),category:form.get("category"),profile_type:form.get("profile_type"),
        trait_key:form.get("trait_key"),explanation:form.get("explanation"),
        display_order:Number(form.get("display_order")||0),is_required:form.get("is_required")==="on",options,
        image_url:form.get("image_url"),gif_url:form.get("gif_url"),audio_url:form.get("audio_url"),
        image_source_url:form.get("image_source_url"),difficulty:form.get("difficulty"),
        scheduled_start_at:form.get("scheduled_start_at") || null,scheduled_end_at:form.get("scheduled_end_at") || null
      };
      try {
        const id=questionForm.dataset.id;
        const url=id?`/operator/waifu/api/questions/${id}`:"/operator/waifu/api/questions";
        await adminRequest(url,id?"PUT":"POST",payload);
        showMessage("Question draft saved.");
        setTimeout(()=>location.href="/operator/waifu/questions",700);
      } catch(error) { showMessage(error.message,true); }
    });
  }
})();
