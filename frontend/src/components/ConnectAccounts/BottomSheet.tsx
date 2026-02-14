import { useState } from "react";
import { styles, COLORS, SURFACE } from "./styles";

interface BottomSheetProps {
  serviceName: string;
  brandColor: string;
  onClose: () => void;
  onSubmit: (value: string) => void;
}

export function BottomSheet({ serviceName, brandColor, onClose, onSubmit }: BottomSheetProps) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    if (!value.trim()) return;
    onSubmit(value.trim());
  };

  return (
    <div className="overlay-enter" style={styles.overlay} onClick={onClose}>
      <div
        className="sheet-enter"
        style={styles.sheet}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={styles.sheetTitle}>Connect {serviceName}</h3>
        <p style={styles.sheetSubtitle}>Enter your {serviceName} username</p>

        <input
          type="text"
          placeholder={`@username`}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          style={styles.input}
          autoFocus
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />

        <button
          onClick={handleSubmit}
          disabled={!value.trim()}
          style={{
            ...styles.sheetButton,
            background: value.trim() ? brandColor : SURFACE.elevated,
            color: value.trim() ? "#fff" : SURFACE.textTertiary,
            opacity: value.trim() ? 1 : 0.6,
          }}
        >
          Connect
        </button>

        <button
          onClick={onClose}
          style={{
            ...styles.sheetButton,
            background: "transparent",
            color: COLORS.hotFuchsia,
            marginTop: 8,
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
