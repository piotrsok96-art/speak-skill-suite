import { createFileRoute } from "@tanstack/react-router";

// Proxy to Lovable AI Gateway text-to-speech (OpenAI-compatible).
// Returns MP3 audio bytes. Called from the browser via /api/public/tts.
export const Route = createFileRoute("/api/public/tts")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const apiKey = process.env.LOVABLE_API_KEY;
        if (!apiKey) {
          return new Response("LOVABLE_API_KEY missing", { status: 500 });
        }
        let body: { text?: string; voice?: string };
        try {
          body = await request.json();
        } catch {
          return new Response("Bad JSON", { status: 400 });
        }
        const text = (body.text ?? "").toString().slice(0, 800);
        if (!text.trim()) return new Response("Empty text", { status: 400 });
        const voice = body.voice || "alloy";

        const res = await fetch("https://ai.gateway.lovable.dev/v1/audio/speech", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "openai/gpt-4o-mini-tts",
            input: text,
            voice,
            response_format: "mp3",
          }),
        });
        if (!res.ok) {
          const t = await res.text().catch(() => "");
          return new Response(`TTS upstream ${res.status}: ${t}`, { status: res.status });
        }
        return new Response(res.body, {
          status: 200,
          headers: {
            "Content-Type": "audio/mpeg",
            "Cache-Control": "public, max-age=604800",
          },
        });
      },
    },
  },
});
