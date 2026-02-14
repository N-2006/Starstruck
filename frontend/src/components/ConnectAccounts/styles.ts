import type { CSSProperties } from "react";

// ── Color Palette ──
export const COLORS = {
  onyx: "#141414",
  limeCreem: "#D9FF82",
  hotFuchsia: "#FF4466",
  brightAmber: "#FFCF26",
  softPeriwinkle: "#BB97FF",
  indigoInk: "#381F7D",
  velvetOrchid: "#662288",
} as const;

// ── Surface Hierarchy ──
export const SURFACE = {
  page: "#141414",
  card: "#1E1E2A",
  elevated: "#262638",
  textPrimary: "rgba(255,255,255,0.9)",
  textSecondary: "rgba(255,255,255,0.45)",
  textTertiary: "rgba(255,255,255,0.25)",
  border: "rgba(255,255,255,0.06)",
} as const;

// ── Typography ──
export const FONT_FAMILY = "'DM Sans', system-ui, -apple-system, sans-serif";
export const FONT_MONO = "'JetBrains Mono', 'SF Mono', monospace";

// ── Shared Styles ──
export const styles = {
  page: {
    minHeight: "100vh",
    background: "#381F7D",
    fontFamily: FONT_FAMILY,
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
  } satisfies CSSProperties,

  phoneFrame: {
    width: 390,
    maxWidth: "100vw",
    minHeight: "100dvh",
    position: "relative",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  } satisfies CSSProperties,

  scrollArea: {
    flex: 1,
    overflowY: "auto",
    paddingBottom: 140,
  } satisfies CSSProperties,

  header: {
    padding: "16px 24px 0",
  } satisfies CSSProperties,

  backButton: {
    background: "none",
    border: "none",
    padding: 0,
    cursor: "pointer",
    marginBottom: 20,
  } satisfies CSSProperties,

  stepIndicator: {
    fontSize: 11,
    fontFamily: FONT_MONO,
    fontWeight: 500,
    letterSpacing: 1.5,
    textTransform: "uppercase" as const,
    color: COLORS.softPeriwinkle,
    marginBottom: 12,
  } satisfies CSSProperties,

  pageTitle: {
    fontSize: 32,
    fontWeight: 800,
    letterSpacing: -0.5,
    color: SURFACE.textPrimary,
    margin: 0,
    lineHeight: 1.15,
  } satisfies CSSProperties,

  subtitle: {
    fontSize: 15,
    fontWeight: 400,
    color: "rgba(255,255,255,0.55)",
    lineHeight: 1.5,
    margin: "10px 0 0",
    maxWidth: 340,
  } satisfies CSSProperties,

  cardList: {
    padding: "28px 24px 0",
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
  } satisfies CSSProperties,

  stickyBottom: {
    position: "fixed" as const,
    bottom: 0,
    left: "50%",
    transform: "translateX(-50%)",
    width: 390,
    maxWidth: "100vw",
    padding: "0 48px 34px",
    background: "linear-gradient(to top, #381F7D 60%, transparent)",
    zIndex: 10,
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    boxSizing: "border-box" as const,
  } satisfies CSSProperties,

  ctaButton: {
    width: "100%",
    height: 44,
    borderRadius: 22,
    border: "none",
    fontSize: 14,
    fontWeight: 700,
    fontFamily: FONT_FAMILY,
    textTransform: "uppercase" as const,
    letterSpacing: 0.5,
    cursor: "pointer",
    transition: "background 0.2s, color 0.2s",
  } satisfies CSSProperties,

  ctaHint: {
    fontSize: 12,
    color: "rgba(255,255,255,0.3)",
    textAlign: "center" as const,
    marginTop: 12,
  } satisfies CSSProperties,

  // ── BottomSheet ──
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    zIndex: 50,
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
  } satisfies CSSProperties,

  sheet: {
    width: 390,
    maxWidth: "100vw",
    background: "#381F7D",
    borderRadius: "20px 20px 0 0",
    padding: "24px 24px 40px",
  } satisfies CSSProperties,

  sheetTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: SURFACE.textPrimary,
    margin: "0 0 6px",
  } satisfies CSSProperties,

  sheetSubtitle: {
    fontSize: 13,
    color: SURFACE.textSecondary,
    margin: "0 0 20px",
  } satisfies CSSProperties,

  input: {
    width: "100%",
    height: 48,
    borderRadius: 12,
    border: `1px solid ${SURFACE.border}`,
    background: "#5823A5",
    color: SURFACE.textPrimary,
    fontSize: 15,
    fontFamily: FONT_FAMILY,
    padding: "0 16px",
    outline: "none",
    boxSizing: "border-box" as const,
  } satisfies CSSProperties,

  sheetButton: {
    width: "100%",
    height: 48,
    borderRadius: 24,
    border: "none",
    fontSize: 15,
    fontWeight: 700,
    fontFamily: FONT_FAMILY,
    cursor: "pointer",
    marginTop: 16,
    color: "#fff",
  } satisfies CSSProperties,
} as const;
