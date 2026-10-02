import { useEffect, useRef, useState } from "react";
import { safeExit } from "../api/client";

/**
 * Feature 2.23 — Safe Exit: press Escape twice within 2s to instantly wipe
 * local data and leave to a neutral page (unsafe-device protection).
 */
export function useSafeExit() {
  const [arming, setArming] = useState(false);
  const lastRef = useRef(0);

  useEffect(() => {
    const handler = (e) => {
      if (e.key !== "Escape") return;
      const now = Date.now();
      if (now - lastRef.current < 2000) {
        safeExit();
        return;
      }
      lastRef.current = now;
      setArming(true);
      setTimeout(() => setArming(false), 2000);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return { arming, exitNow: safeExit };
}
