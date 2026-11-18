import { reconnectDelay, socketUrl } from "./socket";
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
    this.handlers.onStatus("connecting");
    const ws = new WebSocket(socketUrl("/ws/chat"));
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
      this.timer = window.setTimeout(() => this.connect(), reconnectDelay(this.retry));
      this.retry += 1;
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
