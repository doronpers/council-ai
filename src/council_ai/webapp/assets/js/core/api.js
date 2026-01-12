/**
 * API client functions
 */

let cachedInfo = null;

/**
 * Load application info from API
 */
export async function loadInfo() {
  if (cachedInfo) {
    return cachedInfo;
  }
  
  const res = await fetch("/api/info");
  const data = await res.json();
  cachedInfo = data;
  return data;
}

/**
 * Submit consultation request
 */
export async function submitConsultation(payload) {
  const res = await fetch("/api/consult", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Request failed.");
  }
  
  return await res.json();
}
