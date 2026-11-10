
(() => {
 const file=document.getElementById("waifuJsonFile"), preview=document.getElementById("waifuJsonPreview"),
 apply=document.getElementById("waifuJsonApply"), output=document.getElementById("waifuJsonMessage");
 let parsed=null;
 async function send(url){
  const r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},credentials:"same-origin",body:JSON.stringify(parsed)});
  const data=await r.json(); if(!r.ok) throw new Error((data.errors||[data.message||"Import failed"]).join("\\n")); return data;
 }
 preview?.addEventListener("click",async()=>{
  apply.disabled=true; parsed=null;
  try{if(!file.files[0])throw new Error("Choose a JSON file first.");parsed=JSON.parse(await file.files[0].text());const result=await send("/operator/waifu/api/json/import/preview");output.textContent=`Valid JSON. ${result.question_count} questions and ${result.character_count} characters found. Import creates drafts requiring review.`;apply.disabled=false;}
  catch(e){output.textContent=e.message;}
 });
 apply?.addEventListener("click",async()=>{
  if(!parsed)return;
  try{const result=await send("/operator/waifu/api/json/import");output.textContent=`Imported ${result.imported_question_ids.length} questions and ${result.imported_character_ids.length} characters as drafts.`;apply.disabled=true;}
  catch(e){output.textContent=e.message;}
 });
})();
