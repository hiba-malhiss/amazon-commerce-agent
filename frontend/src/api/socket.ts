// ws(s):// URL of a backend WebSocket path, on the page's own host (Vite proxies it in dev)
export function socketUrl(path: string): string {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${window.location.host}${path}`;
}

// How long to wait before reconnecting: 1s, 2s, 4s ... up to 10s
export function reconnectDelay(retry: number): number {
  return Math.min(1000 * 2 ** retry, 10_000);
}
