
(() => {
 const form=document.getElementById("operatorCreateForm"), message=document.getElementById("operatorMessage");
 if(form) form.addEventListener("submit",async e=>{
  e.preventDefault(); const data=Object.fromEntries(new FormData(form).entries());
  try{const r=await fetch("/operator/waifu/api/operators",{method:"POST",headers:{"Content-Type":"application/json"},credentials:"same-origin",body:JSON.stringify(data)});const j=await r.json();if(!r.ok)throw new Error(j.message||"Could not create account.");message.textContent="Account created. Reloading...";location.reload();}
  catch(err){message.textContent=err.message;}
 });
 document.querySelectorAll("button[data-id]").forEach(btn=>btn.addEventListener("click",async()=>{
  try{const r=await fetch(`/operator/waifu/api/operators/${btn.dataset.id}/active`,{method:"POST",headers:{"Content-Type":"application/json"},credentials:"same-origin",body:JSON.stringify({active:btn.dataset.active==="1"})});const j=await r.json();if(!r.ok)throw new Error(j.message);location.reload();}
  catch(err){alert(err.message);}
 }));
})();
