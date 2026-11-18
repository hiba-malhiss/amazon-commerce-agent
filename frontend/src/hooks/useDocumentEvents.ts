import { useEffect } from "react";
import { documentEventsPath } from "../api/knowledgeBases";
import { reconnectDelay, socketUrl } from "../api/socket";
import type { DocumentEvent } from "../api/types";

// The knowledge base's document changes, live, over a WebSocket that reconnects by itself.
// onReconnect runs when a lost connection comes back, to reload what was missed meanwhile.
export function useDocumentEvents(
  kbCode: string | null,
  onEvent: (event: DocumentEvent) => void,
  onReconnect: () => void,
) {
  useEffect(() => {
    if (!kbCode) return;
    let socket: WebSocket;
    let retry = 0;
    let opened = false;
    let stopped = false;
    let timer: number | undefined;

    const connect = () => {
      socket = new WebSocket(socketUrl(documentEventsPath(kbCode)));
      socket.onopen = () => {
        if (opened) onReconnect();
        opened = true;
        retry = 0;
      };
      socket.onmessage = (message) => onEvent(JSON.parse(message.data) as DocumentEvent);
      socket.onclose = () => {
        if (stopped) return;
        timer = window.setTimeout(connect, reconnectDelay(retry));
        retry += 1;
      };
    };

    connect();
    return () => {
      stopped = true;
      window.clearTimeout(timer);
      socket.close();
    };
  }, [kbCode, onEvent, onReconnect]);
}
