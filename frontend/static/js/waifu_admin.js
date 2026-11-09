async function adminRequest(url, method="GET", body=null) {
  const options = {method, headers: {"Content-Type":"application/json"}};
  if (body !== null) options.body = JSON.stringify(body);
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) throw new Error(data.message || "Request failed.");
  return data;
}
async function changeStatus(kind, id, status) {
  if (!confirm(`Change this ${kind === "characters" ? "character" : "question"} to ${status.replace("_"," ")}?`)) return;
  try {
    await adminRequest(`/operator/waifu/api/${kind}/${id}/status`, "POST", {status});
    location.reload();
  } catch (error) { alert(error.message); }
}
async function removeRecord(kind, id) {
  if (!confirm("Delete this record permanently? This cannot be undone.")) return;
  try {
    await adminRequest(`/operator/waifu/api/${kind}/${id}`, "DELETE");
    location.reload();
  } catch (error) { alert(error.message); }
}
