const ADMIN_CREDS_KEY = "admin_credentials";

interface AdminCredentials {
  username: string;
  password: string;
}

export function getAdminCredentials(): AdminCredentials | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(ADMIN_CREDS_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setAdminCredentials(username: string, password: string) {
  sessionStorage.setItem(
    ADMIN_CREDS_KEY,
    JSON.stringify({ username, password }),
  );
}

export function clearAdminCredentials() {
  sessionStorage.removeItem(ADMIN_CREDS_KEY);
}

export function isAdminAuthenticated(): boolean {
  return !!getAdminCredentials();
}

export function adminAuthHeaders(): Record<string, string> {
  const creds = getAdminCredentials();
  if (!creds) return {};
  const encoded = btoa(`${creds.username}:${creds.password}`);
  return { Authorization: `Basic ${encoded}` };
}
