import { useCallback, useEffect, useRef, useState } from "react";

const LANG_TAGS = { en: "en-US", hi: "hi-IN", mr: "mr-IN", bn: "bn-IN", ta: "ta-IN", te: "te-IN" };

/**
 * Voice input (Feature 1.2): browser speech recognition for live transcription,
 * plus Web Audio volume measurement feeding the speech-indicator input (2.11).
 * Falls back to typed mode when the browser has no recognition support.
 */
export function useSpeech({ language = "en", onResult, onVolume, active }) {
  const [supported] = useState(() => typeof window !== "undefined" &&
    !!(window.SpeechRecognition || window.webkitSpeechRecognition));
  const [listening, setListening] = useState(false);
  const recRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const cbRef = useRef({ onResult, onVolume });
  cbRef.current = { onResult, onVolume };

  const stop = useCallback(() => {
    setListening(false);
    try {
      recRef.current?.stop();
    } catch {
      /* already stopped */
    }
    recRef.current = null;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const start = useCallback(async () => {
    if (!supported || listening) return false;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    rec.lang = LANG_TAGS[language] || "en-US";
    rec.continuous = true;
    rec.interimResults = false;
    rec.onresult = (event) => {
      const last = event.results[event.results.length - 1];
      if (last.isFinal) {
        const text = last[0].transcript.trim();
        if (text) cbRef.current.onResult?.(text);
      }
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch {
      return false;
    }

    // Volume capture → speech features (Features 2.4 / 2.11: supporting evidence only)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 512;
      src.connect(analyser);
      const buf = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteTimeDomainData(buf);
        let sum = 0;
        for (let i = 0; i < buf.length; i++) {
          const v = (buf[i] - 128) / 128;
          sum += v * v;
        }
        const rms = Math.sqrt(sum / buf.length);
        const db = Math.round(20 * Math.log10(Math.max(rms, 1e-5)) + 100); // 0..~100 scale
        cbRef.current.onVolume?.(Math.max(0, Math.min(100, db)));
        rafRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch {
      /* mic denied — text mode still works */
    }
    return true;
  }, [supported, listening, language]);

  useEffect(() => stop, [stop]);

  return { supported, listening, start, stop };
}
