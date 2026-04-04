import { authHeaders, getAccessToken, clearTokens } from "./auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

/** Close code used by the backend to signal an auth failure. */
export const WS_CLOSE_AUTH_FAILURE = 4001;

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
};

async function request<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, headers = {} } = options;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.detail ?? response.statusText);
  }

  const json = await response.json();

  // Unwrap StandardResponse envelope if present
  if (json && typeof json === "object" && !Array.isArray(json) && "data" in json && "success" in json) {
    return json.data as T;
  }

  return json as T;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const api = {
  get: <T>(endpoint: string, headers?: Record<string, string>) =>
    request<T>(endpoint, { method: "GET", headers }),

  post: <T>(
    endpoint: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) => request<T>(endpoint, { method: "POST", body, headers }),

  put: <T>(
    endpoint: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) => request<T>(endpoint, { method: "PUT", body, headers }),

  delete: <T>(endpoint: string, headers?: Record<string, string>) =>
    request<T>(endpoint, { method: "DELETE", headers }),
};

export function createWebSocket(path: string): WebSocket {
  const token = getAccessToken();
  if (!token) {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("No access token — redirecting to login");
  }

  const separator = path.includes("?") ? "&" : "?";
  const authenticatedPath = `${path}${separator}token=${encodeURIComponent(token)}`;

  if (typeof window !== "undefined") {
    // If API_BASE_URL is a relative path starting with / or empty, use window.location
    if (!API_BASE_URL || API_BASE_URL.startsWith("/")) {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host;
      // Combine API_BASE_URL with path if it exists
      const fullPath = `${API_BASE_URL}${authenticatedPath}`;
      return new WebSocket(`${protocol}//${host}${fullPath}`);
    }

    // If API_BASE_URL is a full URL, replace protocol
    const wsUrl = API_BASE_URL.replace(/^http/, "ws");
    return new WebSocket(`${wsUrl}${authenticatedPath}`);
  }

  throw new Error("createWebSocket called outside of browser context");
}
