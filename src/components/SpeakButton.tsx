import { Volume2, Loader2 } from "lucide-react";
import { useState } from "react";
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
  const [loading, setLoading] = useState(false);
  if (!ttsAvailable()) return null;
  const onClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);
    try {
      await speak(text);
    } finally {
      setLoading(false);
    }
  };
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center justify-center rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors",
        className,
      )}
      aria-label={`Posłuchaj: ${text}`}
      title="Posłuchaj wymowy"
    >
      {loading ? (
        <Loader2 style={{ width: size, height: size }} className="animate-spin" />
      ) : (
        <Volume2 style={{ width: size, height: size }} />
      )}
    </button>
  );
}
