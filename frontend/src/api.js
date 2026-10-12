// All talking to the FastAPI backend happens here.
const BASE = import.meta.env.VITE_API_URL || "/api";

async function request(path, { headers, ...options } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...headers },
  });

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const data = await res.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map((d) => `${d.loc.slice(1).join(" ")}: ${d.msg}`)
          .join(". ");
      }
    } catch {
      /* keep the default message */
    }
    throw new Error(message);
  }
  return res.status === 204 ? null : res.json();
}

export function listItems({ q, status, category, includeResolved }, signal) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (status && status !== "all") params.set("status", status);
  if (category) params.set("category", category);
  if (includeResolved) params.set("include_resolved", "true");
  return request(`/items?${params}`, { signal });
}

export const getItem = (id) => request(`/items/${id}`);

export const createItem = (data) =>
  request("/items", { method: "POST", body: JSON.stringify(data) });

export const markReturned = (id, pin) =>
  request(`/items/${id}/resolve`, { method: "PATCH", headers: { "X-Item-PIN": pin } });

export const deleteItem = (id, pin) =>
  request(`/items/${id}`, { method: "DELETE", headers: { "X-Item-PIN": pin } });
