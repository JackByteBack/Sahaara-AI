import { useCallback, useEffect, useRef, useState } from "react";
import { WS_BASE, getToken } from "./client";

/**
 * useLiveAnalysis — WebSocket hook for the live session console.
 * Server messages: mode | transcript | ai_flag | profile_update |
 *                  status_update | summary | flag_decision | error
 * (build/frontend.md — useLiveAnalysis disconnects on unmount)
 */
export function useLiveAnalysis(caseId) {
  const [connected, setConnected] = useState(false);
  const [mode, setMode] = useState(null);
  const [modeNote, setModeNote] = useState("");
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);
  const retryRef = useRef(0);

  const send = useCallback((payload) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    if (!caseId) return;
    let closed = false;

    const connect = () => {
      if (closed) return;
      const ws = new WebSocket(`${WS_BASE}/api/v1/stream/${caseId}?token=${getToken()}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retryRef.current = 0;
      };
      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "mode") {
            setMode(msg.mode);
            setModeNote(msg.note || "");
          }
          setMessages((prev) => [...prev.slice(-200), msg]);
        } catch {
          /* ignore malformed */
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed && retryRef.current < 8) {
          retryRef.current += 1;
          setTimeout(connect, 800 * retryRef.current);
        }
      };
      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      closed = true;
      setConnected(false);
      if (wsRef.current) wsRef.current.close();
    };
  }, [caseId]);

  return { connected, mode, modeNote, messages, send };
}
