import type { CSSProperties, ReactNode } from "react";
import { SURFACE, FONT_MONO, FONT_FAMILY, COLORS } from "./styles";
import { CheckCircleIcon } from "./icons";

interface ServiceCardProps {
  name: string;
  description: string;
  icon: ReactNode;
  brandColor: string;
  isRequired?: boolean;
  isConnected: boolean;
  isLoading: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  dataPreview?: string;
  index: number;
}

export function ServiceCard({
  name,
  description,
  icon,
  brandColor,
  isRequired,
  isConnected,
  isLoading,
  onConnect,
  onDisconnect,
  dataPreview,
  index,
}: ServiceCardProps) {
  const card: CSSProperties = {
    background: "#5823A5",
    border: isConnected
      ? `1px solid ${brandColor}40`
      : `1px solid ${SURFACE.border}`,
    borderRadius: 20,
    padding: "20px",
    position: "relative",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    gap: 14,
    transition: "border-color 0.3s ease",
    animationDelay: `${index * 0.05}s`,
  };

  const accentBar: CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    width: 3,
    background: brandColor,
    borderRadius: "20px 0 0 20px",
  };

  const connectBtn: CSSProperties = {
    height: 32,
    padding: "0 16px",
    borderRadius: 16,
    border: `1px solid ${COLORS.softPeriwinkle}`,
    background: "transparent",
    color: COLORS.softPeriwinkle,
    fontSize: 12,
    fontWeight: 600,
    fontFamily: FONT_FAMILY,
    cursor: "pointer",
    whiteSpace: "nowrap",
    flexShrink: 0,
  };

  const requiredBadge: CSSProperties = {
    fontSize: 11,
    fontFamily: FONT_MONO,
    fontWeight: 500,
    textTransform: "uppercase",
    letterSpacing: 1.5,
    color: COLORS.hotFuchsia,
    background: `${COLORS.hotFuchsia}1A`,
    padding: "2px 8px",
    borderRadius: 6,
    marginLeft: 8,
  };

  return (
    <div
      className={`card-enter ${isLoading ? "pulse-border" : ""}`}
      style={card}
      onClick={isConnected ? onDisconnect : undefined}
    >
      {/* Accent bar for connected state */}
      {isConnected && <div style={accentBar} />}

      {/* Service icon */}
      <div style={{ flexShrink: 0, display: "flex" }}>
        {icon}
      </div>

      {/* Text content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <span style={{
            fontSize: 17,
            fontWeight: 700,
            color: SURFACE.textPrimary,
          }}>
            {name}
          </span>
          {isRequired && <span style={requiredBadge}>Required</span>}
        </div>
        <div style={{
          fontSize: 13,
          fontWeight: 400,
          color: SURFACE.textSecondary,
          marginTop: 2,
        }}>
          {description}
        </div>
        {isConnected && dataPreview && (
          <div style={{
            fontSize: 12,
            color: `${brandColor}B3`,
            marginTop: 6,
          }}>
            {dataPreview}
          </div>
        )}
      </div>

      {/* Right action */}
      {isLoading ? (
        <div style={{
          fontSize: 12,
          color: SURFACE.textSecondary,
          fontFamily: FONT_MONO,
        }}>
          ...
        </div>
      ) : isConnected ? (
        <div className="check-enter" style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
          <CheckCircleIcon size={18} color={brandColor} />
          <span style={{
            fontSize: 12,
            fontWeight: 600,
            color: brandColor,
          }}>
            Connected
          </span>
        </div>
      ) : (
        <button style={connectBtn} onClick={onConnect}>
          Connect
        </button>
      )}
    </div>
  );
}
