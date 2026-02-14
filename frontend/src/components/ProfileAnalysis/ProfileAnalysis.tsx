import { useState, useEffect } from "react";
import "../ConnectAccounts/connectAccounts.css";
import { styles, COLORS, SURFACE, FONT_MONO, FONT_FAMILY } from "../ConnectAccounts/styles";
import { ChevronLeftIcon } from "../ConnectAccounts/icons";
import { StarstruckAPI } from "../../api";

interface ProfileAnalysisProps {
  onContinue: () => void;
}

const ANALYSIS_STEPS = [
  "Analyzing music taste…",
  "Reading film reviews…",
  "Scanning coding habits…",
  "Mapping your vibe…",
  "Generating bio…",
];

const SUGGESTED_BIO =
  "Indie music obsessive with a soft spot for A24 films and late-night coding sessions. Probably rating your favorite movie 3.5 stars on Letterboxd right now.";

const FINDINGS = [
  {
    label: "Music Personality",
    value: "Indie Explorer",
    detail: "You dig deep cuts and niche artists — your top genres span dream pop, shoegaze, and alt-R&B.",
    color: COLORS.limeCreem,
  },
  {
    label: "Film Taste",
    value: "Art-House Devotee",
    detail: "142 films logged · 3.9★ average · heavy on slow burns and foreign cinema.",
    color: COLORS.brightAmber,
  },
  {
    label: "Code Style",
    value: "Night Owl Builder",
    detail: "Peak commits between 10PM–2AM · mostly TypeScript · 23 repos.",
    color: COLORS.softPeriwinkle,
  },
];

const VIBE_TAGS = [
  "Night Owl",
  "Vinyl Collector",
  "Bookworm",
  "Coffee Snob",
  "Film Buff",
  "Indie Head",
  "Deep Thinker",
  "Creative Coder",
];

function RefreshIcon({ size = 18, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10" />
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
    </svg>
  );
}

export function ProfileAnalysis({ onContinue }: ProfileAnalysisProps) {
  const [analyzing, setAnalyzing] = useState(true);
  const [progress, setProgress] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [bio, setBio] = useState(SUGGESTED_BIO);
  const [tags, setTags] = useState(VIBE_TAGS);
  const [findings, setFindings] = useState(FINDINGS);
  const [newTag, setNewTag] = useState("");

  useEffect(() => {
    if (!analyzing) return;

    const stepDuration = 2500 / ANALYSIS_STEPS.length;
    const stepInterval = setInterval(() => {
      setStepIndex((prev) => (prev >= ANALYSIS_STEPS.length - 1 ? prev : prev + 1));
    }, stepDuration);

    const progressInterval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 100 : prev + 2));
    }, 50);

    const fetchData = async () => {
      try {
        const result = await StarstruckAPI.getProfile({
          letterboxd_username: "aditya",
        });

        if (result && result.dossier) {
          const d = result.dossier;
          if (d.public) {
            setBio(d.public.vibe || SUGGESTED_BIO);
            setTags(d.public.tags || VIBE_TAGS);
          }
          if (d.private) {
            setFindings([
              {
                label: "Personality",
                value: d.private.traits ? d.private.traits[0] : "Unique Vibe",
                detail: d.private.summary,
                color: COLORS.limeCreem,
              },
              ...FINDINGS.slice(1)
            ]);
          }
        }
      } catch (err) {
        console.error("Profile analysis error:", err);
      } finally {
        setTimeout(() => setAnalyzing(false), 3000);
      }
    };

    fetchData();

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, [analyzing]);

  const handleRegenerate = () => {
    setAnalyzing(true);
    setProgress(0);
    setStepIndex(0);
    setBio(SUGGESTED_BIO);
  };

  return (
    <div style={styles.page}>
      <div style={styles.phoneFrame}>
        <div style={styles.scrollArea}>
          <header style={styles.header}>
            <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
              <button style={{ ...styles.backButton, marginBottom: 0 }}>
                <ChevronLeftIcon size={24} color="rgba(255,255,255,0.5)" />
              </button>
              <img
                src="/Star (7).png"
                alt="Starstruck"
                style={{ width: 80, height: 80, margin: "0 auto" }}
              />
              <div style={{ width: 24 }} />
            </div>

            <div style={styles.stepIndicator}>Step 3 of 4</div>
            <h1 style={styles.pageTitle}>Your vibe, decoded</h1>
            <p style={styles.subtitle}>
              We analyzed your connected accounts to craft your dating profile. Edit anything you'd like.
            </p>
          </header>

          {analyzing ? (
            <div className="card-enter" style={{ padding: "40px 24px", textAlign: "center" }}>
              <div style={{
                width: 64,
                height: 64,
                borderRadius: 32,
                background: `${COLORS.softPeriwinkle}1A`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 20px",
                animation: "pulseBorder 1.5s ease-in-out infinite",
              }}>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 16,
                  border: `3px solid ${COLORS.softPeriwinkle}`,
                  borderTopColor: "transparent",
                  animation: "spin 0.8s linear infinite",
                }} />
              </div>

              <div style={{
                fontSize: 15,
                fontWeight: 600,
                color: SURFACE.textPrimary,
                marginBottom: 8,
              }}>
                {ANALYSIS_STEPS[stepIndex]}
              </div>

              <div style={{
                width: "100%",
                height: 4,
                borderRadius: 2,
                background: "rgba(255,255,255,0.06)",
                overflow: "hidden",
                maxWidth: 200,
                margin: "0 auto",
              }}>
                <div style={{
                  height: "100%",
                  width: `${progress}%`,
                  borderRadius: 2,
                  background: `linear-gradient(90deg, ${COLORS.softPeriwinkle}, ${COLORS.limeCreem})`,
                  transition: "width 0.1s linear",
                }} />
              </div>
            </div>
          ) : (
            <>
              {/* ── Suggested bio ── */}
              <div className="card-enter" style={{ padding: "24px 24px 0" }}>
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 12,
                }}>
                  <span style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: SURFACE.textSecondary,
                    textTransform: "uppercase",
                    fontFamily: FONT_MONO,
                    letterSpacing: 1,
                  }}>
                    AI-Suggested Bio
                  </span>
                  <button
                    onClick={handleRegenerate}
                    style={{
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      padding: 0,
                      color: COLORS.softPeriwinkle,
                      fontSize: 12,
                      fontWeight: 600,
                      fontFamily: FONT_FAMILY,
                    }}
                  >
                    <RefreshIcon size={14} color={COLORS.softPeriwinkle} />
                    Regenerate
                  </button>
                </div>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={4}
                  style={{
                    width: "100%",
                    background: "#5823A5",
                    border: `1px solid ${SURFACE.border}`,
                    borderRadius: 16,
                    padding: "14px 16px",
                    fontSize: 15,
                    fontFamily: "inherit",
                    color: "rgba(255,255,255,0.9)",
                    lineHeight: 1.5,
                    resize: "none",
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              {/* ── Findings ── */}
              <div style={{ padding: "24px 24px 0" }}>
                <span style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: SURFACE.textSecondary,
                  textTransform: "uppercase",
                  fontFamily: FONT_MONO,
                  letterSpacing: 1,
                  display: "block",
                  marginBottom: 12,
                }}>
                  What We Found
                </span>

                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {findings.map((finding, i) => (
                    <div
                      key={finding.label}
                      className="card-enter"
                      style={{
                        background: "#5823A5",
                        border: `1px solid ${SURFACE.border}`,
                        borderRadius: 20,
                        padding: 20,
                        position: "relative",
                        overflow: "hidden",
                        animationDelay: `${i * 0.08}s`,
                      }}
                    >
                      <div style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: 3,
                        background: finding.color,
                        borderRadius: "20px 0 0 20px",
                      }} />
                      <div style={{
                        fontSize: 11,
                        fontFamily: FONT_MONO,
                        fontWeight: 500,
                        textTransform: "uppercase",
                        letterSpacing: 1.5,
                        color: finding.color,
                        marginBottom: 6,
                      }}>
                        {finding.label}
                      </div>
                      <div style={{
                        fontSize: 17,
                        fontWeight: 700,
                        color: SURFACE.textPrimary,
                        marginBottom: 4,
                      }}>
                        {finding.value}
                      </div>
                      <div style={{
                        fontSize: 13,
                        color: SURFACE.textSecondary,
                        lineHeight: 1.4,
                      }}>
                        {finding.detail}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ── Vibe tags ── */}
              <div className="card-enter" style={{ padding: "24px 24px 0" }}>
                <span style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: SURFACE.textSecondary,
                  textTransform: "uppercase",
                  fontFamily: FONT_MONO,
                  letterSpacing: 1,
                  display: "block",
                  marginBottom: 12,
                }}>
                  Your Vibe Tags
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      onClick={() => setTags((prev) => prev.filter((t) => t !== tag))}
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: COLORS.softPeriwinkle,
                        background: `${COLORS.softPeriwinkle}1A`,
                        padding: "6px 14px",
                        borderRadius: 20,
                        border: `1px solid ${COLORS.softPeriwinkle}30`,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                      }}
                    >
                      {tag}
                      <span style={{ fontSize: 15, lineHeight: 1, opacity: 0.5 }}>×</span>
                    </span>
                  ))}
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      const trimmed = newTag.trim();
                      if (trimmed && !tags.includes(trimmed)) {
                        setTags((prev) => [...prev, trimmed]);
                        setNewTag("");
                      }
                    }}
                    style={{ display: "flex" }}
                  >
                    <input
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="+ Add tag"
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: COLORS.softPeriwinkle,
                        background: "transparent",
                        padding: "6px 14px",
                        borderRadius: 20,
                        border: `1px dashed ${COLORS.softPeriwinkle}40`,
                        outline: "none",
                        width: 100,
                        fontFamily: "inherit",
                      }}
                    />
                  </form>
                </div>
              </div>
            </>
          )}
        </div>

        {/* ── Sticky CTA ── */}
        {!analyzing && (
          <div style={styles.stickyBottom}>
            <button
              onClick={onContinue}
              style={{
                ...styles.ctaButton,
                background: COLORS.softPeriwinkle,
                color: "#fff",
              }}
            >
              Continue
            </button>
            <div style={styles.ctaHint}>You can edit your bio anytime</div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
