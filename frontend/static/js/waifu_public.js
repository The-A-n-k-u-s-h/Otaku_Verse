(() => {
  const start=document.getElementById("loadQuestions");
  const area=document.getElementById("questionArea");
  const empty=document.getElementById("emptyQuestions");
  const prompt=document.getElementById("questionPrompt");
  const category=document.getElementById("questionCategory");
  const options=document.getElementById("answerOptions");
  const next=document.getElementById("nextQuestion");
  const message=document.getElementById("questionMessage");
  const count=document.getElementById("questionCount");
  const bar=document.getElementById("progressBar");
  let questions=[], index=0, selected=null;
  async function load() {
    const response=await fetch("/api/waifu/questions");
    const data=await response.json();
    questions=data.items||[];
    if(!questions.length){empty.hidden=false;return;}
    start.hidden=true; area.hidden=false; render();
  }
  function render(){
    selected=null; next.disabled=true; message.textContent="";
    const q=questions[index]; prompt.textContent=q.prompt; category.textContent=`${q.profile_type} · ${q.category}`;
    count.textContent=`Question ${index+1} of ${questions.length}`;
    bar.style.width=`${((index+1)/questions.length)*100}%`;
    options.innerHTML="";
    q.options.forEach(option=>{
      const button=document.createElement("button"); button.type="button"; button.className="answer-option"; button.textContent=option.text;
      button.addEventListener("click",()=>{
        options.querySelectorAll("button").forEach(b=>b.classList.remove("selected"));
        button.classList.add("selected"); selected=option.id; next.disabled=false;
      });
      options.appendChild(button);
    });
    next.textContent=index===questions.length-1?"Finish preview":"Continue";
  }
  start.addEventListener("click",()=>load().catch(()=>{message.textContent="Could not load questions. Please try again."; }));
  next.addEventListener("click",()=>{
    if(selected===null)return;
    if(index<questions.length-1){index++;render();}
    else {
      area.innerHTML='<article class="question-panel"><p class="eyebrow">QUESTION BANK PREVIEW COMPLETE</p><h2>You have reached the end of the approved questions.</h2><p>The matching calculation and final character reveal will be connected in a later module.</p><a class="primary" href="/">Return home</a></article>';
    }
  });
})();
