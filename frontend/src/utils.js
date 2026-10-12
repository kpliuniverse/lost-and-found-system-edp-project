export const CATEGORIES = [
  "Phones & electronics",
  "Wallets & cards",
  "Keys",
  "Bags",
  "Clothing",
  "Documents",
  "Jewelry",
  "Pets",
  "Other",
];

export function todayISO() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 10);
}

export function formatDate(iso) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export const statusLabel = (status) => (status === "lost" ? "Lost" : "Found");
