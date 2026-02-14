import type { CSSProperties } from "react";
import { COLORS, SURFACE } from "./styles";

interface SignalStrengthProps {
  percentage: number;
}

export function SignalStrength({ percentage }: SignalStrengthProps) {
  const container: CSSProperties = {
    padding: "24px 24px 0",
  };

  const labelRow: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  };

  const track: CSSProperties = {
    width: "100%",
    height: 6,
    borderRadius: 3,
    background: "rgba(255,255,255,0.03)",
    overflow: "hidden",
  };

  const fill: CSSProperties = {
    height: "100%",
    width: `${percentage}%`,
    borderRadius: 3,
    background: `linear-gradient(90deg, ${COLORS.softPeriwinkle}, ${COLORS.limeCreem})`,
    transition: "width 0.4s ease-out",
  };

  return (
    <div style={container}>
      <div style={labelRow}>
        <span style={{ fontSize: 13, color: SURFACE.textSecondary }}>
          Profile signal strength
        </span>
        <span style={{
          fontSize: 13,
          fontWeight: 700,
          color: percentage >= 70 ? COLORS.limeCreem : COLORS.softPeriwinkle,
        }}>
          {percentage}%
        </span>
      </div>
      <div style={track}>
        <div className="progress-fill" style={fill} />
      </div>
      {percentage < 100 && (
        <div style={{
          fontSize: 12,
          color: "rgba(255,255,255,0.3)",
          marginTop: 8,
        }}>
          Connect more for better matches
        </div>
      )}
    </div>
  );
}
