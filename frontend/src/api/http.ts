// fetch with errors that say what the server answered; no body (204) comes back as undefined
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) {
    throw new Error(await errorMessage(res));
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}

// FastAPI errors are {"detail": "..."}: show the detail, else the status line
async function errorMessage(res: Response): Promise<string> {
  const body = await res.text().catch(() => "");
  try {
    const detail = (JSON.parse(body) as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
  } catch {
    // not JSON
  }
  return `${res.status} ${res.statusText}${body ? `: ${body}` : ""}`;
}
