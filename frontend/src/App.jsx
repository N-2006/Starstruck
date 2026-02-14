import { useState, useEffect } from "react";

const PALETTE = {
  bg: "#07070d",
  surface: "#0d0d17",
  surfaceHover: "#111122",
  border: "#ffffff09",
  dim: "#4a4a68",
  mid: "#8888a8",
  bright: "#e8e8f4",
  pink: "#ff3d6e",
  violet: "#8b5cf6",
  teal: "#0dd1a1",
  amber: "#f5a623",
  blue: "#3b82f6",
  cyan: "#06b6d4",
};

const FONTS = {
  display: "'Playfair Display', Georgia, serif",
  body: "'DM Sans', system-ui, sans-serif",
  mono: "'JetBrains Mono', 'SF Mono', monospace",
};

const DATA_SOURCES = [
  {
    id: "spotify",
    label: "Spotify",
    icon: "♫",
    color: "#1DB954",
    auth: "OAuth 2.0 PKCE",
    endpoints: [
      "/me/top/artists — genres, popularity",
      "/me/top/tracks — song preferences",
      "/me/player/recently-played — listening schedule",
      "/me/playlists — mood contexts",
    ],
    signals: ["Music taste & subculture", "Energy level & mood", "Night owl detection", "Emotional landscape"],
  },
  {
    id: "letterboxd",
    label: "Letterboxd",
    icon: "◔",
    color: "#00e054",
    auth: "Public RSS + Scrape",
    endpoints: [
      "/{user}/rss/ — diary entries + ratings",
      "/{user}/films/ratings/ — all rated films",
      "/{user}/likes/films/ — aspirational taste",
      "/{user}/lists/ — curated collections",
    ],
    signals: ["Emotional intelligence", "Aesthetic sensibility", "How critical they are", "Relationship to storytelling"],
  },
  {
    id: "github",
    label: "GitHub",
    icon: "⊚",
    color: "#8b949e",
    auth: "Public (no auth)",
    endpoints: [
      "/users/{u}/repos — languages, projects",
      "/users/{u}/events — commit timestamps",
      "/users/{u}/starred — aspirational interests",
    ],
    signals: ["Work ethic & schedule", "Technical curiosity", "Ambition type", "Collaboration style"],
  },
  {
    id: "books",
    label: "Open Library",
    icon: "◉",
    color: "#e8a87c",
    auth: "No auth needed",
    endpoints: [
      "/search.json?q={title} — book metadata",
      "Google Books /volumes — categories, pages",
    ],
    signals: ["Intellectual depth", "Fiction vs nonfiction ratio", "Preferred topics", "Commitment level"],
  },
  {
    id: "instagram",
    label: "Instagram",
    icon: "◐",
    color: "#e1306c",
    auth: "Claude Vision on screenshots",
    endpoints: [
      "Vision API — bio, post themes, aesthetic",
      "GDPR export JSON — full activity data",
    ],
    signals: ["Visual identity", "Humor style", "Social energy", "Authenticity score"],
  },
  {
    id: "places",
    label: "Google Places",
    icon: "◈",
    color: "#4285f4",
    auth: "API Key",
    endpoints: [
      "/places:searchNearby — venues + ratings",
      "/places/{id} — reviews, photos, hours",
    ],
    signals: ["Venue matching", "Conversation hooks from reviews", "Outfit calibration", "Logistical intel"],
  },
];

const PIPELINE_NODES = [
  {
    id: "ingest",
    label: "Parallel Data Ingest",
    time: "~3s",
    color: PALETTE.teal,
    icon: "⟡",
    desc: "Simultaneous API calls to all connected services. Raw responses normalized into unified UserDataBundle per person.",
  },
  {
    id: "analyze",
    label: "Profile Analyzer",
    time: "~4s",
    color: PALETTE.violet,
    icon: "◈",
    desc: "Claude Sonnet synthesizes raw data into structured personality dossiers — traits, humor style, love language signals, vibe archetype.",
  },
  {
    id: "crossref",
    label: "Cross-Reference Engine",
    time: "~3s",
    color: PALETTE.pink,
    icon: "✦",
    desc: "The core node. Finds shared artists, overlapping films, complementary traits, tension points. Cites specific data points, not generic vibes.",
  },
  {
    id: "venue",
    label: "Venue Intelligence",
    time: "~2s",
    color: PALETTE.blue,
    icon: "◉",
    desc: "Google Places search ranked by match context — not just 'good restaurant' but 'this place connects to something in both your profiles.'",
  },
  {
    id: "coach",
    label: "Date Coach",
    time: "~5s",
    color: PALETTE.amber,
    icon: "◎",
    desc: "Final synthesis of ALL data into a personalized briefing card stack. Each user gets asymmetric advice tailored to their date.",
  },
];

const COACHING_OUTPUT = [
  { label: "Match Intel", icon: "🎯", desc: "Why you matched — with specific data citations", color: PALETTE.pink },
  { label: "Conversation Playbook", icon: "💬", desc: "5 ranked openers from cross-referenced interests", color: PALETTE.violet },
  { label: "Minefield Map", icon: "🚫", desc: "Topics to avoid, inferred from social signals", color: "#ef4444" },
  { label: "Venue Cheat Sheet", icon: "📍", desc: "What to order, where to sit, insider hooks", color: PALETTE.teal },
  { label: "Vibe Calibration", icon: "👔", desc: "Outfit direction, energy advice, key date insight", color: PALETTE.amber },
];

function Glow({ color, x, y, size = 300, opacity = 0.06 }) {
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: size,
        height: size,
        background: `radial-gradient(circle, ${color}${Math.round(opacity * 255).toString(16).padStart(2, "0")} 0%, transparent 70%)`,
        pointerEvents: "none",
        transform: "translate(-50%, -50%)",
      }}
    />
  );
}

function SourceCard({ source, index, isActive, onClick }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: isActive ? source.color + "10" : hovered ? PALETTE.surfaceHover : PALETTE.surface,
        border: `1px solid ${isActive ? source.color + "40" : PALETTE.border}`,
        borderRadius: 12,
        padding: "14px 16px",
        cursor: "pointer",
        transition: "all 0.25s ease",
        animation: `fadeSlideUp 0.5s ease ${index * 0.06}s both`,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {isActive && (
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${source.color}, transparent)` }} />
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: isActive ? 12 : 0 }}>
        <span style={{ fontSize: 18, color: source.color, lineHeight: 1 }}>{source.icon}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: isActive ? PALETTE.bright : PALETTE.mid, fontFamily: FONTS.body }}>{source.label}</span>
        <span style={{ fontSize: 9, fontFamily: FONTS.mono, color: PALETTE.dim, marginLeft: "auto", letterSpacing: 0.5 }}>{source.auth}</span>
      </div>
      {isActive && (
        <div style={{ animation: "fadeIn 0.3s ease" }}>
          <div style={{ marginBottom: 10 }}>
            {source.endpoints.map((ep, i) => (
              <div key={i} style={{ fontSize: 10.5, fontFamily: FONTS.mono, color: PALETTE.dim, lineHeight: 1.8, paddingLeft: 28 }}>
                <span style={{ color: source.color + "90" }}>→</span> {ep}
              </div>
            ))}
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 5, paddingLeft: 28 }}>
            {source.signals.map((s) => (
              <span key={s} style={{ fontSize: 9.5, fontFamily: FONTS.mono, padding: "2px 8px", borderRadius: 4, background: source.color + "12", color: source.color, border: `1px solid ${source.color}20`, letterSpacing: 0.3 }}>
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PipelineNode({ node, index, isActive, onClick }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        animation: `fadeSlideRight 0.5s ease ${0.3 + index * 0.08}s both`,
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: "50%",
          background: isActive ? node.color + "18" : PALETTE.surface,
          border: `2px solid ${isActive || hovered ? node.color + "80" : PALETTE.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 18,
          cursor: "pointer",
          transition: "all 0.25s ease",
          flexShrink: 0,
          boxShadow: isActive ? `0 0 20px ${node.color}15` : "none",
        }}
      >
        {node.icon}
      </div>

      <div style={{ flex: 1, cursor: "pointer" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: isActive ? node.color : PALETTE.bright, fontFamily: FONTS.body }}>
            {node.label}
          </span>
          <span style={{ fontSize: 9, fontFamily: FONTS.mono, color: PALETTE.dim, padding: "1px 6px", borderRadius: 3, background: PALETTE.surface, border: `1px solid ${PALETTE.border}` }}>
            {node.time}
          </span>
        </div>
        <div style={{ fontSize: 11.5, color: PALETTE.dim, lineHeight: 1.55, fontFamily: FONTS.body, maxHeight: isActive ? 60 : 0, overflow: "hidden", transition: "max-height 0.3s ease", opacity: isActive ? 1 : 0 }}>
          {node.desc}
        </div>
      </div>

      {index < PIPELINE_NODES.length - 1 && (
        <div style={{ position: "absolute", left: 23, top: 54, width: 2, height: isActive ? 56 : 28, background: `linear-gradient(to bottom, ${node.color}30, transparent)`, transition: "height 0.3s" }} />
      )}
    </div>
  );
}

export default function App() {
  const [activeSource, setActiveSource] = useState(null);
  const [activeNode, setActiveNode] = useState("crossref");
  const [visible, setVisible] = useState(false);

  useEffect(() => { setVisible(true); }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: PALETTE.bg,
        fontFamily: FONTS.body,
        color: PALETTE.mid,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;800;900&family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #ffffff08; border-radius: 2px; }
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeSlideRight {
          from { opacity: 0; transform: translateX(-12px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes pulseGlow {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
        @keyframes flowDown {
          0% { background-position: 0 0; }
          100% { background-position: 0 20px; }
        }
      `}</style>

      <Glow color={PALETTE.pink} x="15%" y="20%" size={500} opacity={0.04} />
      <Glow color={PALETTE.violet} x="50%" y="50%" size={600} opacity={0.03} />
      <Glow color={PALETTE.teal} x="85%" y="75%" size={400} opacity={0.04} />

      <div style={{ position: "fixed", inset: 0, backgroundImage: "radial-gradient(circle at 1px 1px, #ffffff03 0.5px, transparent 0)", backgroundSize: "24px 24px", pointerEvents: "none" }} />

      <header style={{ padding: "40px 48px 0", position: "relative", zIndex: 2 }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginBottom: 6, animation: "fadeSlideUp 0.6s ease both" }}>
            <h1 style={{ fontSize: 38, fontWeight: 900, fontFamily: FONTS.display, color: PALETTE.bright, letterSpacing: "-0.5px", lineHeight: 1 }}>
              Starstruck
            </h1>
            <span style={{ fontSize: 11, fontFamily: FONTS.mono, color: PALETTE.dim, letterSpacing: 2, textTransform: "uppercase" }}>
              tech architecture
            </span>
          </div>
          <p style={{ fontSize: 15, color: PALETTE.dim, lineHeight: 1.6, maxWidth: 640, animation: "fadeSlideUp 0.6s ease 0.1s both", fontFamily: FONTS.body }}>
            Post-match coaching pipeline. Analyze both users' digital footprints, cross-reference their data, and generate hyper-personalized date advice.
          </p>

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 24, animation: "fadeSlideUp 0.6s ease 0.2s both", flexWrap: "wrap" }}>
            {["Match Confirmed", "Ingest Socials", "Build Dossiers", "Cross-Reference", "Find Venue", "Coach"].map((step, i) => (
              <div key={step} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ padding: "6px 14px", borderRadius: 6, background: PALETTE.surface, border: `1px solid ${PALETTE.border}`, fontSize: 11, fontWeight: 600, color: i === 0 ? PALETTE.pink : i === 5 ? PALETTE.amber : PALETTE.mid, fontFamily: FONTS.body }}>
                  {step}
                </div>
                {i < 5 && <span style={{ color: PALETTE.dim, fontSize: 11 }}>→</span>}
              </div>
            ))}
            <span style={{ fontSize: 10, fontFamily: FONTS.mono, color: PALETTE.dim, marginLeft: 8 }}>~17s total</span>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "48px 48px 60px", position: "relative", zIndex: 2 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px 1fr", gap: 32, alignItems: "start" }}>

          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 24 }}>
              {["User A", "User B"].map((user, i) => (
                <div
                  key={user}
                  style={{
                    background: PALETTE.surface,
                    border: `1px solid ${PALETTE.border}`,
                    borderRadius: 12,
                    padding: "16px 18px",
                    textAlign: "center",
                    animation: `fadeSlideUp 0.5s ease ${i * 0.08}s both`,
                  }}
                >
                  <div style={{ width: 36, height: 36, borderRadius: "50%", background: i === 0 ? PALETTE.pink + "15" : PALETTE.violet + "15", border: `2px solid ${i === 0 ? PALETTE.pink + "40" : PALETTE.violet + "40"}`, margin: "0 auto 10px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>
                    {i === 0 ? "♀" : "♂"}
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: PALETTE.bright, marginBottom: 3 }}>{user}</div>
                  <div style={{ fontSize: 10, fontFamily: FONTS.mono, color: PALETTE.dim }}>matched ✓</div>
                </div>
              ))}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, animation: "fadeSlideUp 0.5s ease 0.15s both" }}>
              <div style={{ width: 3, height: 14, background: PALETTE.teal, borderRadius: 2 }} />
              <span style={{ fontSize: 10, fontFamily: FONTS.mono, letterSpacing: 2.5, textTransform: "uppercase", color: PALETTE.teal, fontWeight: 600 }}>Data Sources & APIs</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {DATA_SOURCES.map((src, i) => (
                <SourceCard
                  key={src.id}
                  source={src}
                  index={i}
                  isActive={activeSource === src.id}
                  onClick={() => setActiveSource(activeSource === src.id ? null : src.id)}
                />
              ))}
            </div>
          </div>

          <div style={{ paddingTop: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20, animation: "fadeSlideUp 0.5s ease 0.25s both" }}>
              <div style={{ width: 3, height: 14, background: PALETTE.violet, borderRadius: 2 }} />
              <span style={{ fontSize: 10, fontFamily: FONTS.mono, letterSpacing: 2.5, textTransform: "uppercase", color: PALETTE.violet, fontWeight: 600 }}>LangGraph Pipeline</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 16, position: "relative" }}>
              <div style={{
                position: "absolute",
                left: 23,
                top: 48,
                bottom: 24,
                width: 2,
                background: `repeating-linear-gradient(to bottom, ${PALETTE.violet}20 0px, ${PALETTE.violet}20 4px, transparent 4px, transparent 8px)`,
                animation: "flowDown 0.8s linear infinite",
              }} />

              {PIPELINE_NODES.map((node, i) => (
                <div key={node.id} style={{ position: "relative" }}>
                  <PipelineNode
                    node={node}
                    index={i}
                    isActive={activeNode === node.id}
                    onClick={() => setActiveNode(activeNode === node.id ? null : node.id)}
                  />
                </div>
              ))}
            </div>

            <div style={{
              marginTop: 24,
              padding: "12px 16px",
              background: PALETTE.surface,
              border: `1px solid ${PALETTE.border}`,
              borderRadius: 10,
              animation: "fadeSlideUp 0.5s ease 0.5s both",
            }}>
              <div style={{ fontSize: 9, fontFamily: FONTS.mono, letterSpacing: 2, color: PALETTE.amber, marginBottom: 6, textTransform: "uppercase" }}>LLM Backbone</div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.6 }}>
                <span style={{ color: PALETTE.bright }}>Claude Sonnet 4</span> — profiling, cross-ref, coaching
              </div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.6 }}>
                <span style={{ color: PALETTE.bright }}>Claude Haiku 4.5</span> — venue ranking, parsing
              </div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.6 }}>
                <span style={{ color: PALETTE.bright }}>Claude Vision</span> — Instagram screenshot analysis
              </div>
            </div>
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20, animation: "fadeSlideUp 0.5s ease 0.35s both" }}>
              <div style={{ width: 3, height: 14, background: PALETTE.amber, borderRadius: 2 }} />
              <span style={{ fontSize: 10, fontFamily: FONTS.mono, letterSpacing: 2.5, textTransform: "uppercase", color: PALETTE.amber, fontWeight: 600 }}>Coaching Output</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {COACHING_OUTPUT.map((card, i) => (
                <div
                  key={card.label}
                  style={{
                    background: PALETTE.surface,
                    border: `1px solid ${PALETTE.border}`,
                    borderRadius: 12,
                    padding: "16px 18px",
                    borderLeft: `3px solid ${card.color}40`,
                    animation: `fadeSlideUp 0.5s ease ${0.4 + i * 0.06}s both`,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                    <span style={{ fontSize: 15 }}>{card.icon}</span>
                    <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.bright }}>{card.label}</span>
                  </div>
                  <div style={{ fontSize: 11.5, color: PALETTE.dim, lineHeight: 1.5, paddingLeft: 24 }}>
                    {card.desc}
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              marginTop: 16,
              padding: "16px 18px",
              background: PALETTE.surface,
              border: `1px solid ${PALETTE.border}`,
              borderRadius: 12,
              animation: "fadeSlideUp 0.5s ease 0.7s both",
            }}>
              <div style={{ fontSize: 9, fontFamily: FONTS.mono, letterSpacing: 2, color: PALETTE.cyan, marginBottom: 8, textTransform: "uppercase" }}>Delivery</div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.7 }}>
                Card stack pushed to each user <span style={{ color: PALETTE.bright }}>2hrs before date</span>
              </div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.7 }}>
                Asymmetric — <span style={{ color: PALETTE.bright }}>each gets different emphasis</span>
              </div>
              <div style={{ fontSize: 11, color: PALETTE.dim, lineHeight: 1.7 }}>
                Streamed via <span style={{ color: PALETTE.bright }}>SSE</span> as pipeline completes
              </div>
            </div>

            <div style={{
              marginTop: 16,
              padding: "18px 20px",
              background: PALETTE.pink + "08",
              border: `1px solid ${PALETTE.pink}15`,
              borderRadius: 12,
              animation: "fadeSlideUp 0.5s ease 0.8s both",
            }}>
              <div style={{ fontSize: 9, fontFamily: FONTS.mono, letterSpacing: 2, color: PALETTE.pink, marginBottom: 10, textTransform: "uppercase" }}>
                Example insight
              </div>
              <div style={{ fontSize: 12.5, color: PALETTE.mid, lineHeight: 1.7, fontStyle: "italic" }}>
                "You both rated <span style={{ color: PALETTE.bright }}>In the Mood for Love</span> five stars and have <span style={{ color: PALETTE.bright }}>Khruangbin</span> in your top 5 — you share a slow-burn romantic sensibility. Ask them about Wong Kar-wai over drinks."
              </div>
            </div>

            <div style={{
              marginTop: 16,
              padding: "16px 18px",
              background: PALETTE.surface,
              border: `1px solid ${PALETTE.border}`,
              borderRadius: 12,
              animation: "fadeSlideUp 0.5s ease 0.85s both",
            }}>
              <div style={{ fontSize: 9, fontFamily: FONTS.mono, letterSpacing: 2, color: PALETTE.blue, marginBottom: 10, textTransform: "uppercase" }}>Infra</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {["LangGraph", "FastAPI", "Redis", "Neon Postgres", "Vercel", "Clerk Auth"].map((t) => (
                  <span key={t} style={{ fontSize: 9.5, fontFamily: FONTS.mono, padding: "3px 8px", borderRadius: 4, background: "#ffffff06", border: `1px solid ${PALETTE.border}`, color: PALETTE.dim }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
