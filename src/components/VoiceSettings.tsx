import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  isNaturalEnabled,
  setNaturalEnabled,
  getVoicePref,
  setVoicePref,
  VOICE_OPTIONS,
  speak,
  type NaturalVoice,
} from "@/lib/tts";
import { Volume2 } from "lucide-react";

export function VoiceSettings() {
  const [natural, setNatural] = useState(isNaturalEnabled());
  const [voice, setVoice] = useState<NaturalVoice>(getVoicePref());

  return (
    <div className="rounded-xl border bg-card p-5 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold inline-flex items-center gap-1">
            <Volume2 className="h-4 w-4" /> Głos lektora
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Naturalny głos (AI) vs systemowy (Web Speech).
          </p>
        </div>
        <label className="inline-flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={natural}
            onChange={(e) => {
              setNatural(e.target.checked);
              setNaturalEnabled(e.target.checked);
            }}
          />
          Naturalny
        </label>
      </div>
      {natural && (
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={voice}
            onChange={(e) => {
              const v = e.target.value as NaturalVoice;
              setVoice(v);
              setVoicePref(v);
            }}
            className="text-xs rounded-md border bg-background px-2 py-1"
          >
            {VOICE_OPTIONS.map((o) => (
              <option key={o.id} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
          <Button size="sm" variant="outline" onClick={() => speak("Hello! This is a preview of the voice.")}>
            Testuj
          </Button>
        </div>
      )}
    </div>
  );
}
