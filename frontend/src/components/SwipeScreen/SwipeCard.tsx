import { useState, useRef, type CSSProperties } from "react";
import { COLORS, FONT_FAMILY } from "../ConnectAccounts/styles";

interface Profile {
  name: string;
  age: number;
  photo: string;
  bio: string;
  tags: string[];
  distance: string;
}

interface SwipeCardProps {
  profile: Profile;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  isTop: boolean;
}

export function SwipeCard({ profile, onSwipeLeft, onSwipeRight, isTop }: SwipeCardProps) {
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [exiting, setExiting] = useState<"left" | "right" | null>(null);
  const startPos = useRef({ x: 0, y: 0 });

  const SWIPE_THRESHOLD = 100;

  const handleStart = (clientX: number, clientY: number) => {
    if (!isTop) return;
    setIsDragging(true);
    startPos.current = { x: clientX, y: clientY };
  };

  const handleMove = (clientX: number, clientY: number) => {
    if (!isDragging) return;
    setOffset({
      x: clientX - startPos.current.x,
      y: clientY - startPos.current.y,
    });
  };

  const handleEnd = () => {
    if (!isDragging) return;
    setIsDragging(false);

    if (offset.x > SWIPE_THRESHOLD) {
      triggerExit("right");
    } else if (offset.x < -SWIPE_THRESHOLD) {
      triggerExit("left");
    } else {
      setOffset({ x: 0, y: 0 });
    }
  };

  const triggerExit = (dir: "left" | "right") => {
    setExiting(dir);
    setOffset({ x: dir === "right" ? 500 : -500, y: -50 });
    setTimeout(() => {
      if (dir === "right") onSwipeRight();
      else onSwipeLeft();
    }, 300);
  };

  const rotation = offset.x * 0.08;
  const opacity = Math.max(0, 1 - Math.abs(offset.x) / 400);
  const likeOpacity = Math.min(1, offset.x / SWIPE_THRESHOLD);
  const nopeOpacity = Math.min(1, -offset.x / SWIPE_THRESHOLD);

  const card: CSSProperties = {
    position: "absolute",
    width: "100%",
    height: "100%",
    borderRadius: 20,
    overflow: "hidden",
    transform: isTop
      ? `translateX(${offset.x}px) translateY(${offset.y * 0.3}px) rotate(${rotation}deg)`
      : "scale(0.95) translateY(10px)",
    transition: isDragging ? "none" : "transform 0.3s ease, opacity 0.3s ease",
    opacity: exiting ? opacity : isTop ? 1 : 0.7,
    cursor: isTop ? "grab" : "default",
    touchAction: "none",
    zIndex: isTop ? 2 : 1,
    boxShadow: "0 8px 40px rgba(0,0,0,0.4)",
  };

  const stampBase: CSSProperties = {
    position: "absolute",
    top: 40,
    fontSize: 36,
    fontWeight: 800,
    fontFamily: FONT_FAMILY,
    padding: "6px 16px",
    borderRadius: 8,
    border: "3px solid",
    transform: "rotate(-15deg)",
    letterSpacing: 2,
    textTransform: "uppercase",
    zIndex: 5,
    pointerEvents: "none",
  };

  return (
    <div
      style={card}
      onMouseDown={(e) => handleStart(e.clientX, e.clientY)}
      onMouseMove={(e) => handleMove(e.clientX, e.clientY)}
      onMouseUp={handleEnd}
      onMouseLeave={() => isDragging && handleEnd()}
      onTouchStart={(e) => handleStart(e.touches[0].clientX, e.touches[0].clientY)}
      onTouchMove={(e) => handleMove(e.touches[0].clientX, e.touches[0].clientY)}
      onTouchEnd={handleEnd}
    >
      <img
        src={profile.photo}
        alt={profile.name}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          pointerEvents: "none",
          userSelect: "none",
        }}
        draggable={false}
      />

      {/* Gradient overlay */}
      <div style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: "50%",
        background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 100%)",
        pointerEvents: "none",
      }} />

      {/* LIKE stamp */}
      {isTop && likeOpacity > 0 && (
        <div style={{
          ...stampBase,
          left: 24,
          color: COLORS.limeCreem,
          borderColor: COLORS.limeCreem,
          opacity: likeOpacity,
        }}>
          Like
        </div>
      )}

      {/* NOPE stamp */}
      {isTop && nopeOpacity > 0 && (
        <div style={{
          ...stampBase,
          right: 24,
          color: COLORS.hotFuchsia,
          borderColor: COLORS.hotFuchsia,
          opacity: nopeOpacity,
          transform: "rotate(15deg)",
        }}>
          Nope
        </div>
      )}

      {/* Profile info */}
      <div style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        padding: "0 20px 20px",
        pointerEvents: "none",
      }}>
        <div style={{
          display: "flex",
          alignItems: "baseline",
          gap: 8,
          marginBottom: 4,
        }}>
          <span style={{
            fontSize: 28,
            fontWeight: 800,
            color: "#fff",
          }}>
            {profile.name}
          </span>
          <span style={{
            fontSize: 22,
            fontWeight: 400,
            color: "rgba(255,255,255,0.7)",
          }}>
            {profile.age}
          </span>
        </div>

        <div style={{
          fontSize: 13,
          color: "rgba(255,255,255,0.5)",
          marginBottom: 10,
        }}>
          {profile.distance}
        </div>

        <div style={{
          fontSize: 14,
          color: "rgba(255,255,255,0.75)",
          lineHeight: 1.4,
          marginBottom: 12,
        }}>
          {profile.bio}
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {profile.tags.map((tag) => (
            <span key={tag} style={{
              fontSize: 11,
              fontWeight: 600,
              color: COLORS.softPeriwinkle,
              background: `${COLORS.softPeriwinkle}1A`,
              padding: "4px 10px",
              borderRadius: 20,
              border: `1px solid ${COLORS.softPeriwinkle}30`,
            }}>
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Action button icons ──

export function HeartIcon({ size = 28, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke="none">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  );
}

export function XMarkIcon({ size = 28, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export function StarIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke="none">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );
}
