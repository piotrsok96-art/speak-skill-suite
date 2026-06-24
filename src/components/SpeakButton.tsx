import { Volume2 } from "lucide-react";
import { speak, ttsAvailable } from "@/lib/tts";
import { cn } from "@/lib/utils";

export function SpeakButton({
  text,
  className,
  size = 14,
}: {
  text: string;
  className?: string;
  size?: number;
}) {
  if (!ttsAvailable()) return null;
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        speak(text);
      }}
      className={cn(
        "inline-flex items-center justify-center rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors",
        className,
      )}
      aria-label={`Posłuchaj: ${text}`}
      title="Posłuchaj wymowy"
    >
      <Volume2 style={{ width: size, height: size }} />
    </button>
  );
}
