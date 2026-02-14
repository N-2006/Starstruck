import { useState, useCallback, useEffect, type CSSProperties } from "react";
import "../ConnectAccounts/connectAccounts.css";
import { COLORS, SURFACE, FONT_FAMILY, FONT_MONO } from "../ConnectAccounts/styles";
import { SwipeCard, HeartIcon, XMarkIcon, StarIcon } from "./SwipeCard";
import { StarstruckAPI } from "../../api";

type Tab = "swipe" | "matches" | "dates" | "profile";

function HeartOutlineIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  );
}

function FlameIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke="none">
      <path d="M12 23c-3.6 0-8-2.4-8-7.7 0-3.4 2-6.4 3.8-8.5.4-.5 1.2-.2 1.2.4 0 1.2.5 2.7 1.5 3.3.1-2 .8-4.8 3-7.2.3-.4.9-.3 1.1.1.8 1.8 2.4 3.3 3.5 4.4 1.6 1.6 3.9 4 3.9 7.5 0 5.3-4.4 7.7-8 7.7h-2z" />
    </svg>
  );
}

function LockOpenIcon({ size = 14, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 9.9-1" />
    </svg>
  );
}

function MatchProfileDetail({ match, onPlanDate, onBack }: { match: MatchProfile; onPlanDate: () => void; onBack: () => void }) {
  const pub = match.publicProfile;
  const priv = match.privateProfile;

  const sectionLabel = (text: string, icon?: React.ReactNode) => (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: 6,
      fontSize: 11,
      fontWeight: 700,
      color: SURFACE.textTertiary,
      textTransform: "uppercase" as const,
      fontFamily: FONT_MONO,
      letterSpacing: 1.5,
      marginBottom: 10,
      marginTop: 24,
    }}>
      {icon}
      {text}
    </div>
  );

  const pill = (text: string, color: string) => (
    <span key={text} style={{
      fontSize: 12,
      fontWeight: 600,
      color,
      background: `${color}1A`,
      padding: "5px 12px",
      borderRadius: 20,
      border: `1px solid ${color}30`,
    }}>
      {text}
    </span>
  );

  return (
    <div className="card-enter" style={{ flex: 1, overflowY: "auto", padding: "0 20px 24px" }}>
      <button
        onClick={onBack}
        style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0 16px", color: SURFACE.textSecondary, fontSize: 13, fontWeight: 600, fontFamily: FONT_FAMILY }}
      >
        \u2190 Back
      </button>

      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 8 }}>
        <img src={match.photo} alt={match.name} style={{ width: 64, height: 64, borderRadius: 32, objectFit: "cover" }} />
        <div>
          <div style={{ fontSize: 24, fontWeight: 800, color: SURFACE.textPrimary }}>{match.name}, {match.age}</div>
          <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: COLORS.limeCreem }}>{match.compatibility} match</div>
        </div>
      </div>

      {sectionLabel("Public Profile")}
      <div style={{
        background: "#5823A5",
        border: `1px solid ${SURFACE.border}`,
        borderRadius: 20,
        padding: 20,
      }}>
        <div style={{ fontSize: 15, color: SURFACE.textPrimary, fontStyle: "italic", lineHeight: 1.5, marginBottom: 16 }}>
          \"{pub.vibe}\"
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 14 }}>
          {pub.tags.map((t) => pill(t, COLORS.softPeriwinkle))}
        </div>
        <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: SURFACE.textSecondary }}>
          Schedule: <span style={{ color: COLORS.brightAmber, fontWeight: 600 }}>{pub.schedule}</span>
        </div>
      </div>

      {sectionLabel("Private Profile — unlocked", <LockOpenIcon size={12} color={COLORS.limeCreem} />)}
      <div style={{
        background: "#5823A5",
        border: `1px solid ${COLORS.limeCreem}20`,
        borderRadius: 20,
        padding: 20,
      }}>
        <div style={{ fontSize: 14, color: SURFACE.textSecondary, lineHeight: 1.6, marginBottom: 16 }}>
          {priv.summary}
        </div>

        <div style={{ fontSize: 11, fontFamily: FONT_MONO, color: SURFACE.textTertiary, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Traits</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
          {priv.traits.map((t) => pill(t, COLORS.limeCreem))}
        </div>

        <div style={{ fontSize: 11, fontFamily: FONT_MONO, color: SURFACE.textTertiary, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Interests</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 16 }}>
          {priv.interests.map((t) => pill(t, COLORS.brightAmber))}
        </div>

        <div style={{ fontSize: 11, fontFamily: FONT_MONO, color: SURFACE.textTertiary, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Deep Cuts</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
          {priv.deepCuts.map((cut) => (
            <div key={cut} style={{
              fontSize: 13,
              color: SURFACE.textSecondary,
              background: `${COLORS.softPeriwinkle}0D`,
              padding: "10px 14px",
              borderRadius: 12,
              lineHeight: 1.4,
            }}>
              {cut}
            </div>
          ))}
        </div>

        <div style={{ fontSize: 11, fontFamily: FONT_MONO, color: SURFACE.textTertiary, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Data Sources</div>
        <div style={{ display: "flex", gap: 8 }}>
          {priv.dataSources.map((src) => (
            <span key={src} style={{
              fontSize: 11,
              fontFamily: FONT_MONO,
              fontWeight: 600,
              color: COLORS.softPeriwinkle,
              background: `${COLORS.softPeriwinkle}15`,
              padding: "4px 12px",
              borderRadius: 10,
              textTransform: "uppercase",
              letterSpacing: 0.5,
            }}>
              {src}
            </span>
          ))}
        </div>
      </div>

      <button
        onClick={onPlanDate}
        style={{
          width: "100%",
          height: 52,
          borderRadius: 26,
          border: "none",
          background: COLORS.softPeriwinkle,
          color: "#fff",
          fontSize: 16,
          fontWeight: 700,
          fontFamily: FONT_FAMILY,
          textTransform: "uppercase",
          letterSpacing: 0.5,
          cursor: "pointer",
          marginTop: 24,
        }}
      >
        Plan a Date
      </button>
    </div>
  );
}

function CalendarIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function PersonIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

interface Profile {
  name: string;
  age: number;
  photo: string;
  bio: string;
  tags: string[];
  distance: string;
}

const MOCK_PROFILES: Profile[] = [
  {
    name: "Ava",
    age: 26,
    photo: "/profile_photos/1.png",
    bio: "Gallery hopper and pasta maker. I'll judge you lovingly by your Letterboxd ratings.",
    tags: ["Art", "Cooking", "A24 Films", "Wine"],
    distance: "2 miles away",
  },
  {
    name: "Mia",
    age: 25,
    photo: "/profile_photos/2.png",
    bio: "Runs a book club nobody asked for. Always training for a half marathon I'll never sign up for.",
    tags: ["Running", "Fiction", "Coffee", "Pilates"],
    distance: "4 miles away",
  },
  {
    name: "Luna",
    age: 27,
    photo: "/profile_photos/3.png",
    bio: "Jazz on vinyl, mezcal on ice. I photograph strangers on the subway and call it art.",
    tags: ["Jazz", "Photography", "Mezcal", "Film"],
    distance: "1 mile away",
  },
  {
    name: "Priya",
    age: 28,
    photo: "/profile_photos/4.png",
    bio: "Product designer who overthinks everything except brunch spots. My dog has more followers than me.",
    tags: ["Design", "Dogs", "Brunch", "Yoga"],
    distance: "3 miles away",
  },
  {
    name: "Sofia",
    age: 25,
    photo: "/profile_photos/5.png",
    bio: "Salsa dancer and spicy food enthusiast. Looking for someone who can keep up on both fronts.",
    tags: ["Dancing", "Latin Music", "Cooking", "Travel"],
    distance: "5 miles away",
  },
  {
    name: "Chloe",
    age: 26,
    photo: "/profile_photos/6.png",
    bio: "Writer by day, stand-up open mic-er by night. I will absolutely roast you on the first date.",
    tags: ["Comedy", "Writing", "Theater", "Karaoke"],
    distance: "2 miles away",
  },
  {
    name: "Naomi",
    age: 27,
    photo: "/profile_photos/7.png",
    bio: "Vintage shopping is my cardio. I have strong opinions about font pairings and cold brew ratios.",
    tags: ["Fashion", "Typography", "Coffee", "Thrifting"],
    distance: "6 miles away",
  },
  {
    name: "Zara",
    age: 25,
    photo: "/profile_photos/8.png",
    bio: "Climbing walls and binge-watching sci-fi. If you can quote Arrival we're already halfway there.",
    tags: ["Rock Climbing", "Sci-Fi", "Hiking", "Board Games"],
    distance: "3 miles away",
  },
  {
    name: "Ella",
    age: 28,
    photo: "/profile_photos/9.png",
    bio: "Ceramics class regular and farmer's market loyalist. My sourdough starter has a name.",
    tags: ["Ceramics", "Baking", "Gardening", "Indie Music"],
    distance: "4 miles away",
  },
  {
    name: "Iris",
    age: 26,
    photo: "/profile_photos/10.png",
    bio: "Tattoo collector and museum nerd. I'll make you a playlist before I learn your last name.",
    tags: ["Tattoos", "Museums", "Music", "Poetry"],
    distance: "1 mile away",
  },
  {
    name: "Camille",
    age: 27,
    photo: "/profile_photos/11.png",
    bio: "French expat who swapped croissants for bagels. Still healing from that decision honestly.",
    tags: ["French Cinema", "Baking", "Architecture", "Cycling"],
    distance: "5 miles away",
  },
  {
    name: "Jade",
    age: 25,
    photo: "/profile_photos/12.png",
    bio: "DJ on weekends, data analyst on weekdays. My playlists have better structure than my sleep schedule.",
    tags: ["DJing", "Electronic Music", "Data", "Nightlife"],
    distance: "2 miles away",
  },
];

const page: CSSProperties = {
  minHeight: "100vh",
  background: "#381F7D",
  fontFamily: FONT_FAMILY,
  display: "flex",
  justifyContent: "center",
  alignItems: "flex-start",
};

const frame: CSSProperties = {
  width: 390,
  maxWidth: "100vw",
  height: "100dvh",
  position: "relative",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
};

interface MatchProfile {
  name: string;
  age: number;
  photo: string;
  compatibility: string;
  sharedTags: string[];
  suggestion: { place: string; address: string; date: string; reason: string };
  publicProfile: {
    vibe: string;
    tags: string[];
    schedule: string;
  };
  privateProfile: {
    summary: string;
    traits: string[];
    interests: string[];
    deepCuts: string[];
    dataSources: string[];
  };
}

const MATCHES: MatchProfile[] = [
  {
    name: "Luna", age: 27, photo: "/profile_photos/3.png", compatibility: "94%",
    sharedTags: ["Jazz", "Film", "Vinyl"],
    suggestion: { place: "Blue Note Jazz Club", address: "131 W 3rd St, Greenwich Village", date: "Fri, Feb 20 · 8:00 PM", reason: "You both love jazz and live music — Blue Note is a perfect first vibe check." },
    publicProfile: { vibe: "A nocturnal creative who lives for jazz and quiet observation.", tags: ["jazz", "photography", "mezcal", "film noir", "vinyl", "subway portraits"], schedule: "night owl" },
    privateProfile: { summary: "A photographer with a deep love for jazz and analog culture. Her Letterboxd is full of moody European films and she gravitates toward artists who blend genres.", traits: ["visual storyteller", "analog purist", "jazz devotee", "night owl", "contemplative"], interests: ["Miles Davis", "Chet Baker", "Wong Kar-wai", "In the Mood for Love", "Stalker", "Paris Texas", "Kodak Portra", "Mezcal"], deepCuts: ["Photographs strangers on the L train", "Rated 'In the Mood for Love' 5 stars three times", "Has a vinyl-only listening rule on Sundays"], dataSources: ["spotify", "letterboxd", "instagram"] },
  },
  {
    name: "Priya", age: 28, photo: "/profile_photos/4.png", compatibility: "89%",
    sharedTags: ["Design", "Brunch", "Dogs"],
    suggestion: { place: "MoMA", address: "11 W 53rd St, Midtown", date: "Sat, Feb 21 · 2:00 PM", reason: "She's into design, you're into art — MoMA on a Saturday afternoon is a no-brainer." },
    publicProfile: { vibe: "A modern soul with a passion for building and a taste for the finer things.", tags: ["web dev", "hip hop", "film enthusiast", "coding interviews", "music lover", "fitness", "machine learning"], schedule: "mixed" },
    privateProfile: { summary: "This person is a developer with a strong interest in web technologies and machine learning. They enjoy critically acclaimed films and have a penchant for modern hip hop and R&B. They seem driven and ambitious, possibly preparing for job interviews in the tech industry.", traits: ["aspiring developer", "modern music aficionado", "film critic", "interview prep", "fitness enthusiast"], interests: ["HTML", "PHP", "JavaScript", "CSS", "Drake", "The Weeknd", "Travis Scott", "Kendrick Lamar", "Frank Ocean", "Interstellar", "The Social Network", "Oppenheimer", "Whiplash", "Parasite"], deepCuts: ["Starred repositories related to interview preparation", "Experimenting with SkinCancerCNN", "Listens to Frank Ocean", "Rated 'Interstellar' and 'Whiplash' a perfect 5 stars"], dataSources: ["github", "spotify", "letterboxd"] },
  },
  {
    name: "Chloe", age: 26, photo: "/profile_photos/6.png", compatibility: "87%",
    sharedTags: ["Comedy", "Writing", "Karaoke"],
    suggestion: { place: "Comedy Cellar", address: "117 MacDougal St, West Village", date: "Tue, Feb 25 · 9:30 PM", reason: "You both appreciate comedy — catch a show and see who laughs harder." },
    publicProfile: { vibe: "Sharp-tongued writer who finds humor in everything.", tags: ["comedy", "writing", "theater", "karaoke", "stand-up", "improv"], schedule: "night owl" },
    privateProfile: { summary: "A writer and comedian who spends most nights at open mics. Her taste in film leans toward dark comedies and she has a surprisingly deep Spotify history of 90s alt-rock.", traits: ["quick wit", "performer", "night owl", "empathetic writer", "karaoke queen"], interests: ["Fleabag", "Atlanta", "Bo Burnham", "Nora Ephron", "Radiohead", "Fiona Apple", "The Lobster", "Sorry to Bother You"], deepCuts: ["Has a draft folder with 47 unfinished essays", "Performs stand-up every Tuesday at Comedy Cellar", "Rated 'Fleabag' episodes individually on Letterboxd"], dataSources: ["spotify", "letterboxd", "instagram"] },
  },
  {
    name: "Iris", age: 26, photo: "/profile_photos/10.png", compatibility: "82%",
    sharedTags: ["Museums", "Music", "Poetry"],
    suggestion: { place: "Metrograph Cinema", address: "7 Ludlow St, Lower East Side", date: "Sun, Mar 1 · 4:00 PM", reason: "Film buffs unite — Metrograph always has something interesting playing." },
    publicProfile: { vibe: "Ink-stained museum wanderer with impeccable playlists.", tags: ["tattoos", "museums", "poetry", "music curation", "zines", "film"], schedule: "flexible" },
    privateProfile: { summary: "A creative who splits time between gallery visits and curating playlists. She reads poetry collections and makes zines about her neighborhood. Deeply into ambient and experimental music.", traits: ["curator", "poet", "visual thinker", "tattoo collector", "community builder"], interests: ["Björk", "FKA Twigs", "Aphex Twin", "Rothko", "Ocean Vuong", "Moonlight", "Portrait of a Lady on Fire", "Zine culture"], deepCuts: ["Made a 200-track playlist called 'for walking home alone'", "Has a tattoo of a Rothko painting", "Rated 'Moonlight' 5 stars twice"], dataSources: ["spotify", "letterboxd", "instagram"] },
  },
  {
    name: "Ella", age: 28, photo: "/profile_photos/9.png", compatibility: "78%",
    sharedTags: ["Baking", "Indie Music", "Gardening"],
    suggestion: { place: "Brooklyn Botanic Garden", address: "990 Washington Ave, Brooklyn", date: "Sat, Mar 8 · 11:00 AM", reason: "You both love nature and calm vibes — a garden stroll is the perfect low-key first date." },
    publicProfile: { vibe: "Gentle soul who finds joy in slow mornings and growing things.", tags: ["ceramics", "baking", "gardening", "indie music", "farmers market", "sourdough"], schedule: "early bird" },
    privateProfile: { summary: "A homebody creative who bakes sourdough, tends a rooftop garden, and listens to indie folk while doing ceramics. Her film taste is warm and nostalgic — lots of Ghibli and coming-of-age stories.", traits: ["nurturing", "patient creator", "nature lover", "morning person", "cozy minimalist"], interests: ["Bon Iver", "Phoebe Bridgers", "Big Thief", "Studio Ghibli", "Lady Bird", "Aftersun", "Ceramics", "Sourdough"], deepCuts: ["Named her sourdough starter 'Leonard'", "Has a rooftop garden with 14 plant species", "Cried at 'Aftersun' three separate times"], dataSources: ["spotify", "letterboxd"] },
  },
];

const ANALYSIS_MSGS = [
  "Cross-referencing music taste…",
  "Comparing film preferences…",
  "Finding shared interests…",
  "Scouting date spots in NYC…",
  "Picking the perfect time…",
];

type MatchPhase = "grid" | "confirm" | "analyzing" | "suggestion" | "sent";

function MatchesView({ initialPlanIdx, onClearInitial }: { initialPlanIdx?: number | null; onClearInitial?: () => void }) {
  const [phase, setPhase] = useState<MatchPhase>(initialPlanIdx != null ? "confirm" : "grid");
  const [selectedIdx, setSelectedIdx] = useState<number | null>(initialPlanIdx ?? null);

  const backToGrid = () => {
    setPhase("grid");
    setSelectedIdx(null);
    onClearInitial?.();
  };
  const [analysisStep, setAnalysisStep] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const selected = selectedIdx !== null ? MATCHES[selectedIdx] : null;

  const handleMatchClick = (idx: number) => {
    setSelectedIdx(idx);
    setPhase("confirm");
  };

  const startPlanning = async () => {
    setPhase("analyzing");
    setAnalysisStep(0);
    setAnalysisProgress(0);

    const stepDuration = 2000 / ANALYSIS_MSGS.length;
    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev >= ANALYSIS_MSGS.length - 1 ? prev : prev + 1));
    }, stepDuration);

    const progressInterval = setInterval(() => {
      setAnalysisProgress((prev) => (prev >= 100 ? 100 : prev + 5));
    }, 100);

    try {
      const request = {
        user_a: {
          spotify_username: "aditya",
          letterboxd_username: "aditya",
          location: "New York, NY"
        },
        user_b: {
          spotify_username: selected?.name.toLowerCase(),
          letterboxd_username: selected?.name.toLowerCase(),
          location: "New York, NY"
        },
        include_venue: true
      };

      const result = await StarstruckAPI.runPipeline(request);

      if (selected && result.venues.length > 0) {
        const topVenue = result.venues[0];
        selected.suggestion = {
          place: topVenue.name,
          address: topVenue.address || "Local area",
          date: "TBD",
          reason: topVenue.reason
        };
      }
    } catch (err) {
      console.error("Plumbing error:", err);
    } finally {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
      setAnalysisProgress(100);
      setPhase("suggestion");
    }
  };

  useEffect(() => {
    if (phase !== "analyzing") return;

    const stepDuration = 2500 / ANALYSIS_MSGS.length;
    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => {
        if (prev >= ANALYSIS_MSGS.length - 1) { clearInterval(stepInterval); return prev; }
        return prev + 1;
      });
    }, stepDuration);

    const progressInterval = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 100) { clearInterval(progressInterval); return 100; }
        return prev + 2;
      });
    }, 50);

    const timeout = setTimeout(() => setPhase("suggestion"), 2800);

    return () => { clearInterval(stepInterval); clearInterval(progressInterval); clearTimeout(timeout); };
  }, [phase]);

  if (phase === "confirm" && selected) {
    return (
      <div className="card-enter" style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px" }}>
        <img
          src={selected.photo}
          alt={selected.name}
          style={{ width: 96, height: 96, borderRadius: 48, objectFit: "cover", marginBottom: 20, border: `2px solid ${COLORS.softPeriwinkle}40` }}
        />
        <div style={{ fontSize: 22, fontWeight: 800, color: SURFACE.textPrimary, marginBottom: 6 }}>
          {selected.name}, {selected.age}
        </div>
        <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: COLORS.limeCreem, marginBottom: 24 }}>
          {selected.compatibility} match
        </div>
        <div style={{ fontSize: 16, color: SURFACE.textSecondary, marginBottom: 28, textAlign: "center" }}>
          Plan a date with {selected.name}?
        </div>
        <button
          onClick={startPlanning}
          style={{
            width: "100%",
            maxWidth: 260,
            height: 48,
            borderRadius: 24,
            border: "none",
            background: COLORS.softPeriwinkle,
            color: "#fff",
            fontSize: 15,
            fontWeight: 700,
            fontFamily: FONT_FAMILY,
            textTransform: "uppercase",
            letterSpacing: 0.5,
            cursor: "pointer",
            marginBottom: 12,
          }}
        >
          Plan Date
        </button>
        <button
          onClick={backToGrid}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: SURFACE.textTertiary,
            fontSize: 14,
            fontWeight: 600,
            fontFamily: FONT_FAMILY,
            padding: 8,
          }}
        >
          Cancel
        </button>
      </div>
    );
  }

  if (phase === "analyzing") {
    return (
      <div style={{ padding: "0 24px", flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <img
          src={selected!.photo}
          alt={selected!.name}
          style={{ width: 72, height: 72, borderRadius: 36, objectFit: "cover", marginBottom: 20, border: `2px solid ${COLORS.softPeriwinkle}40` }}
        />
        <div style={{ fontSize: 18, fontWeight: 700, color: SURFACE.textPrimary, marginBottom: 6 }}>
          Planning a date with {selected!.name}
        </div>
        <div style={{
          width: 64,
          height: 64,
          borderRadius: 32,
          background: `${COLORS.softPeriwinkle}1A`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "20px auto",
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
        <div style={{ fontSize: 14, fontWeight: 600, color: SURFACE.textSecondary, marginBottom: 12, textAlign: "center" }}>
          {ANALYSIS_MSGS[analysisStep]}
        </div>
        <div style={{ width: "100%", maxWidth: 200, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${analysisProgress}%`, borderRadius: 2, background: `linear-gradient(90deg, ${COLORS.softPeriwinkle}, ${COLORS.limeCreem})`, transition: "width 0.1s linear" }} />
        </div>
      </div>
    );
  }

  if (phase === "suggestion" && selected) {
    const s = selected.suggestion;
    return (
      <div className="card-enter" style={{ padding: "0 20px", flex: 1, overflowY: "auto" }}>
        <button
          onClick={backToGrid}
          style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0 16px", color: SURFACE.textSecondary, fontSize: 13, fontWeight: 600, fontFamily: FONT_FAMILY }}
        >
          ← Back to matches
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 20 }}>
          <img src={selected.photo} alt={selected.name} style={{ width: 56, height: 56, borderRadius: 28, objectFit: "cover" }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: SURFACE.textPrimary }}>{selected.name}, {selected.age}</div>
            <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: COLORS.limeCreem }}>{selected.compatibility} match</div>
          </div>
        </div>

        <div style={{
          fontSize: 13,
          fontWeight: 700,
          color: SURFACE.textSecondary,
          textTransform: "uppercase",
          fontFamily: FONT_MONO,
          letterSpacing: 1,
          marginBottom: 10,
        }}>
          Shared Interests
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>
          {selected.sharedTags.map((tag) => (
            <span key={tag} style={{
              fontSize: 12,
              fontWeight: 600,
              color: COLORS.softPeriwinkle,
              background: `${COLORS.softPeriwinkle}1A`,
              padding: "5px 12px",
              borderRadius: 20,
              border: `1px solid ${COLORS.softPeriwinkle}30`,
            }}>
              {tag}
            </span>
          ))}
        </div>

        <div style={{
          fontSize: 13,
          fontWeight: 700,
          color: SURFACE.textSecondary,
          textTransform: "uppercase",
          fontFamily: FONT_MONO,
          letterSpacing: 1,
          marginBottom: 10,
        }}>
          Date Suggestion
        </div>
        <div style={{
          background: "#5823A5",
          border: `1px solid ${SURFACE.border}`,
          borderRadius: 20,
          padding: 20,
          position: "relative",
          overflow: "hidden",
          marginBottom: 16,
        }}>
          <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: COLORS.limeCreem, borderRadius: "20px 0 0 20px" }} />
          <div style={{ fontSize: 17, fontWeight: 700, color: SURFACE.textPrimary, marginBottom: 4 }}>{s.place}</div>
          <div style={{ fontSize: 13, color: SURFACE.textSecondary, marginBottom: 6 }}>{s.address}</div>
          <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: COLORS.brightAmber, marginBottom: 12 }}>{s.date}</div>
          <div style={{ fontSize: 14, color: SURFACE.textSecondary, lineHeight: 1.5, fontStyle: "italic" }}>"{s.reason}"</div>
        </div>

        <button
          onClick={() => setPhase("sent")}
          style={{
            width: "100%",
            height: 48,
            borderRadius: 24,
            border: "none",
            background: COLORS.softPeriwinkle,
            color: "#fff",
            fontSize: 15,
            fontWeight: 700,
            fontFamily: FONT_FAMILY,
            textTransform: "uppercase",
            letterSpacing: 0.5,
            cursor: "pointer",
            marginBottom: 12,
          }}
        >
          Send Invite
        </button>
      </div>
    );
  }

  if (phase === "sent" && selected) {
    return (
      <div className="card-enter" style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px" }}>
        <div className="check-enter" style={{ fontSize: 48, marginBottom: 16 }}>✓</div>
        <div style={{ fontSize: 22, fontWeight: 800, color: SURFACE.textPrimary, marginBottom: 8 }}>Invite Sent!</div>
        <div style={{ fontSize: 14, color: SURFACE.textSecondary, textAlign: "center", maxWidth: 260, marginBottom: 28 }}>
          {selected.name} will get your date invite for {selected.suggestion.place}
        </div>
        <button
          onClick={backToGrid}
          style={{
            height: 44,
            padding: "0 32px",
            borderRadius: 22,
            border: `1px solid ${COLORS.softPeriwinkle}`,
            background: "transparent",
            color: COLORS.softPeriwinkle,
            fontSize: 14,
            fontWeight: 700,
            fontFamily: FONT_FAMILY,
            cursor: "pointer",
          }}
        >
          Back to Matches
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "0 16px", flex: 1, overflowY: "auto" }}>
      <h2 style={{ fontSize: 24, fontWeight: 800, color: SURFACE.textPrimary, margin: "0 0 20px 8px" }}>Matches</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {MATCHES.map((m, i) => (
          <div
            key={m.name}
            className="card-enter"
            onClick={() => handleMatchClick(i)}
            style={{
              borderRadius: 20,
              overflow: "hidden",
              position: "relative",
              cursor: "pointer",
              animationDelay: `${i * 0.06}s`,
            }}
          >
            <img
              src={m.photo}
              alt={m.name}
              style={{ width: "100%", aspectRatio: "3 / 4", objectFit: "cover", display: "block" }}
            />
            <div style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              padding: "32px 12px 12px",
              background: "linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%)",
            }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: "#fff" }}>
                {m.name}, {m.age}
              </div>
              <div style={{
                fontSize: 11,
                fontFamily: FONT_MONO,
                fontWeight: 600,
                color: COLORS.limeCreem,
                marginTop: 2,
              }}>
                {m.compatibility} match
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DatesView() {
  const dates = [
    { name: "Luna", photo: "/profile_photos/3.png", place: "Blue Note Jazz Club", date: "Fri, Feb 20 · 8:00 PM", status: "confirmed" as const },
    { name: "Priya", photo: "/profile_photos/4.png", place: "MoMA", date: "Sat, Feb 21 · 2:00 PM", status: "confirmed" as const },
    { name: "Chloe", photo: "/profile_photos/6.png", place: "Comedy Cellar", date: "Tue, Feb 25 · 9:30 PM", status: "pending" as const },
    { name: "Iris", photo: "/profile_photos/10.png", place: "Metrograph Cinema", date: "Sun, Mar 1 · 4:00 PM", status: "pending" as const },
  ];

  const statusColors = {
    confirmed: COLORS.limeCreem,
    pending: COLORS.brightAmber,
  };

  return (
    <div style={{ padding: "0 16px", flex: 1, overflowY: "auto" }}>
      <h2 style={{ fontSize: 24, fontWeight: 800, color: SURFACE.textPrimary, margin: "0 0 20px 8px" }}>Upcoming Dates</h2>
      {dates.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: SURFACE.textSecondary, fontSize: 15 }}>
          No dates planned yet
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {dates.map((d, i) => (
            <div
              key={d.name + d.date}
              className="card-enter"
              style={{
                background: "#5823A5",
                border: `1px solid ${SURFACE.border}`,
                borderRadius: 20,
                padding: 18,
                display: "flex",
                gap: 14,
                alignItems: "center",
                position: "relative",
                overflow: "hidden",
                cursor: "pointer",
                animationDelay: `${i * 0.06}s`,
              }}
            >
              <div style={{
                position: "absolute",
                left: 0,
                top: 0,
                bottom: 0,
                width: 3,
                background: statusColors[d.status],
                borderRadius: "20px 0 0 20px",
              }} />
              <img
                src={d.photo}
                alt={d.name}
                style={{ width: 52, height: 52, borderRadius: 26, objectFit: "cover", flexShrink: 0 }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: SURFACE.textPrimary, marginBottom: 3 }}>
                  Date with {d.name}
                </div>
                <div style={{ fontSize: 13, color: SURFACE.textSecondary, marginBottom: 4 }}>
                  {d.place}
                </div>
                <div style={{ fontSize: 12, fontFamily: FONT_MONO, color: SURFACE.textTertiary }}>
                  {d.date}
                </div>
              </div>
              <span style={{
                fontSize: 10,
                fontFamily: FONT_MONO,
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 1,
                color: statusColors[d.status],
                background: `${statusColors[d.status]}1A`,
                padding: "4px 10px",
                borderRadius: 10,
                flexShrink: 0,
              }}>
                {d.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProfileView() {
  return (
    <div style={{ padding: "0 24px", flex: 1, overflowY: "auto" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 28 }}>
        <div style={{
          width: 96,
          height: 96,
          borderRadius: 48,
          background: `${COLORS.softPeriwinkle}1A`,
          border: `2px solid ${COLORS.softPeriwinkle}40`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 14,
          overflow: "hidden",
        }}>
          <PersonIcon size={40} color={COLORS.softPeriwinkle} />
        </div>
        <span style={{ fontSize: 22, fontWeight: 800, color: SURFACE.textPrimary }}>Your Profile</span>
        <span style={{ fontSize: 13, color: SURFACE.textSecondary, marginTop: 4 }}>NYC · 26</span>
      </div>

      {[
        { label: "Edit Photos", value: "6 photos" },
        { label: "Edit Bio", value: "Tap to update" },
        { label: "Connected Accounts", value: "3 connected" },
        { label: "Vibe Tags", value: "8 tags" },
      ].map((item, i) => (
        <div
          key={item.label}
          className="card-enter"
          style={{
            background: "#5823A5",
            border: `1px solid ${SURFACE.border}`,
            borderRadius: 16,
            padding: "16px 20px",
            marginBottom: 10,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            cursor: "pointer",
            animationDelay: `${i * 0.05}s`,
          }}
        >
          <span style={{ fontSize: 15, fontWeight: 600, color: SURFACE.textPrimary }}>{item.label}</span>
          <span style={{ fontSize: 13, color: SURFACE.textSecondary }}>{item.value} ›</span>
        </div>
      ))}
    </div>
  );
}

const PRIYA_NAME = "Priya";

export function SwipeScreen({ userPhoto }: { userPhoto?: string | null }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<Tab>("swipe");
  const [matchOverlay, setMatchOverlay] = useState<MatchProfile | null>(null);
  const [matchShowText, setMatchShowText] = useState(false);
  const [matchShowButton, setMatchShowButton] = useState(false);
  const [viewingProfile, setViewingProfile] = useState<MatchProfile | null>(null);
  const [planDateIdx, setPlanDateIdx] = useState<number | null>(null);

  const handleSwipeLeft = useCallback(() => {
    setCurrentIndex((prev) => prev + 1);
  }, []);

  const handleSwipeRight = useCallback(() => {
    const swipedProfile = MOCK_PROFILES[currentIndex];
    setCurrentIndex((prev) => prev + 1);
    if (swipedProfile?.name === PRIYA_NAME) {
      const matchData = MATCHES.find((m) => m.name === PRIYA_NAME);
      if (matchData) {
        setMatchOverlay(matchData);
        setMatchShowText(false);
        setMatchShowButton(false);
        setTimeout(() => setMatchShowText(true), 800);
        setTimeout(() => setMatchShowButton(true), 1500);
      }
    }
  }, [currentIndex]);

  const handleSuperLike = useCallback(() => {
    setCurrentIndex((prev) => prev + 1);
  }, []);

  const remaining = MOCK_PROFILES.slice(currentIndex);
  const noMoreCards = remaining.length === 0;

  return (
    <div style={page}>
      <div style={frame}>
        {/* ── Top bar ── */}
        <div style={{
          padding: "16px 24px 0",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 5,
          position: "relative",
        }}>
          <img
            src="/Star (7).png"
            alt="Starstruck"
            style={{ width: 80, height: 80 }}
          />
        </div>

        {activeTab === "swipe" && (
          <>
            {/* ── Card stack ── */}
            <div style={{
              flex: 1,
              position: "relative",
              margin: "12px 16px",
              overflow: "hidden",
            }}>
              {noMoreCards ? (
                <div className="card-enter" style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  gap: 16,
                }}>
                  <StarIcon size={48} color={COLORS.softPeriwinkle} />
                  <span style={{
                    fontSize: 22,
                    fontWeight: 700,
                    color: SURFACE.textPrimary,
                  }}>
                    No more profiles
                  </span>
                  <span style={{
                    fontSize: 14,
                    color: SURFACE.textSecondary,
                    textAlign: "center",
                    maxWidth: 260,
                  }}>
                    Check back later for new matches in your area
                  </span>
                </div>
              ) : (
                remaining.slice(0, 2).reverse().map((profile, i, arr) => (
                  <SwipeCard
                    key={currentIndex + (arr.length - 1 - i)}
                    profile={profile}
                    isTop={i === arr.length - 1}
                    onSwipeLeft={handleSwipeLeft}
                    onSwipeRight={handleSwipeRight}
                  />
                ))
              )}
            </div>

            {/* ── Action buttons ── */}
            {!noMoreCards && (
              <div style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: 20,
                padding: "12px 0 28px",
                zIndex: 5,
              }}>
                <button
                  onClick={handleSwipeLeft}
                  style={actionBtn(COLORS.hotFuchsia)}
                >
                  <XMarkIcon size={26} color={COLORS.hotFuchsia} />
                </button>

                <button
                  onClick={handleSuperLike}
                  style={{
                    ...actionBtn(COLORS.brightAmber),
                    width: 48,
                    height: 48,
                  }}
                >
                  <StarIcon size={20} color={COLORS.brightAmber} />
                </button>

                <button
                  onClick={handleSwipeRight}
                  style={actionBtn(COLORS.limeCreem)}
                >
                  <HeartIcon size={26} color={COLORS.limeCreem} />
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === "matches" && !viewingProfile && (
          <MatchesView
            initialPlanIdx={planDateIdx}
            onClearInitial={() => setPlanDateIdx(null)}
          />
        )}
        {activeTab === "matches" && viewingProfile && (
          <MatchProfileDetail
            match={viewingProfile}
            onBack={() => setViewingProfile(null)}
            onPlanDate={() => {
              const idx = MATCHES.findIndex((m) => m.name === viewingProfile.name);
              setPlanDateIdx(idx >= 0 ? idx : null);
              setViewingProfile(null);
            }}
          />
        )}
        {activeTab === "dates" && <DatesView />}
        {activeTab === "profile" && <ProfileView />}

        {/* ── Match count ── */}
        {!noMoreCards && activeTab === "swipe" && (
          <div style={{
            textAlign: "center",
            paddingBottom: 16,
            fontSize: 11,
            fontFamily: FONT_MONO,
            color: SURFACE.textTertiary,
            letterSpacing: 1,
            textTransform: "uppercase",
          }}>
            {remaining.length} profile{remaining.length !== 1 ? "s" : ""} nearby
          </div>
        )}

        {/* ── Footer tab bar ── */}
        <div style={{
          display: "flex",
          justifyContent: "space-around",
          alignItems: "center",
          padding: "12px 0 20px",
          borderTop: `1px solid ${SURFACE.border}`,
          background: "#381F7D",
          zIndex: 10,
        }}>
          {([
            { id: "swipe" as Tab, icon: FlameIcon, label: "Discover" },
            { id: "matches" as Tab, icon: HeartOutlineIcon, label: "Matches" },
            { id: "dates" as Tab, icon: CalendarIcon, label: "Dates" },
            { id: "profile" as Tab, icon: PersonIcon, label: "Profile" },
          ]).map((tab) => {
            const isActive = activeTab === tab.id;
            const color = isActive ? COLORS.softPeriwinkle : SURFACE.textTertiary;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 4,
                  padding: "4px 16px",
                }}
              >
                <tab.icon size={22} color={color} />
                <span style={{
                  fontSize: 10,
                  fontWeight: 600,
                  fontFamily: FONT_MONO,
                  color,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}>
                  {tab.label}
                </span>
              </button>
            );
          })}
        </div>
        {matchOverlay && (
          <div className="overlay-enter" style={{
            position: "absolute",
            inset: 0,
            background: "#662288",
            zIndex: 100,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}>
            <img
              src="/Star (7).png"
              alt="Starstruck"
              className="match-logo-pulse"
              style={{ width: 80, height: 80, marginBottom: 24 }}
            />

            {matchShowText && (
              <div className="match-text-enter" style={{ textAlign: "center", marginBottom: 32 }}>
                <div style={{ fontSize: 32, fontWeight: 800, color: COLORS.hotFuchsia, marginBottom: 12, letterSpacing: -0.5 }}>
                  It's a Match!
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, marginBottom: 16 }}>
                  <div style={{ width: 72, height: 72, borderRadius: 36, overflow: "hidden", border: `2px solid ${COLORS.softPeriwinkle}` }}>
                    {userPhoto ? (
                      <img src={userPhoto} alt="You" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    ) : (
                      <div style={{ width: "100%", height: "100%", background: `${COLORS.softPeriwinkle}30`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <PersonIcon size={32} color={COLORS.softPeriwinkle} />
                      </div>
                    )}
                  </div>
                  <HeartIcon size={28} color={COLORS.hotFuchsia} />
                  <img src={matchOverlay.photo} alt={matchOverlay.name} style={{ width: 72, height: 72, borderRadius: 36, objectFit: "cover", border: `2px solid ${COLORS.hotFuchsia}` }} />
                </div>
                <div style={{ fontSize: 15, color: SURFACE.textSecondary }}>
                  You and {matchOverlay.name} liked each other
                </div>
              </div>
            )}

            {matchShowButton && (
              <div className="match-text-enter">
                <button
                  onClick={() => {
                    setViewingProfile(matchOverlay);
                    setActiveTab("matches");
                    setMatchOverlay(null);
                  }}
                  style={{
                    height: 52,
                    padding: "0 40px",
                    borderRadius: 26,
                    border: "none",
                    background: COLORS.hotFuchsia,
                    color: "#fff",
                    fontSize: 16,
                    fontWeight: 700,
                    fontFamily: FONT_FAMILY,
                    textTransform: "uppercase",
                    letterSpacing: 0.5,
                    cursor: "pointer",
                    marginBottom: 12,
                  }}
                >
                  View Match
                </button>
                <div style={{ textAlign: "center" }}>
                  <button
                    onClick={() => setMatchOverlay(null)}
                    style={{ background: "none", border: "none", color: SURFACE.textTertiary, fontSize: 14, cursor: "pointer", fontFamily: FONT_FAMILY, padding: 8 }}
                  >
                    Keep Swiping
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function actionBtn(color: string): CSSProperties {
  return {
    width: 56,
    height: 56,
    borderRadius: 28,
    background: `${color}15`,
    border: `2px solid ${color}40`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "transform 0.15s ease, background 0.15s ease",
    padding: 0,
  };
}
