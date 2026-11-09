import type { ChatEvent, ChatRequest } from "./types";

export type SocketStatus = "connecting" | "open" | "closed";

interface Handlers {
  onEvent: (event: ChatEvent) => void;
  onStatus: (status: SocketStatus) => void;
}

export class ChatSocket {
  private ws: WebSocket | null = null;
  private retry = 0;
  private timer: number | undefined;
  private stopped = false;

  constructor(private readonly handlers: Handlers) {}

  connect(): void {
    this.stopped = false;
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    this.handlers.onStatus("connecting");
    const ws = new WebSocket(`${scheme}://${window.location.host}/ws/chat`);
    this.ws = ws;

    ws.onopen = () => {
      this.retry = 0;
      this.handlers.onStatus("open");
    };
    ws.onmessage = (msg) => {
      try {
        this.handlers.onEvent(JSON.parse(msg.data) as ChatEvent);
      } catch {
        this.handlers.onEvent({ type: "error", message: "Unreadable message from server" });
      }
    };
    ws.onclose = () => {
      this.handlers.onStatus("closed");
      if (this.stopped) return;
      const delay = Math.min(1000 * 2 ** this.retry, 10_000);
      this.retry += 1;
      this.timer = window.setTimeout(() => this.connect(), delay);
    };
  }

  send(request: ChatRequest): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) return false;
    this.ws.send(JSON.stringify(request));
    return true;
  }

  close(): void {
    this.stopped = true;
    window.clearTimeout(this.timer);
    this.ws?.close();
  }
}
