import { useState, useCallback, type CSSProperties } from "react";
import "../ConnectAccounts/connectAccounts.css";
import { COLORS, SURFACE, FONT_FAMILY, FONT_MONO } from "../ConnectAccounts/styles";
import { SwipeCard, HeartIcon, XMarkIcon, StarIcon } from "./SwipeCard";

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
    name: "James",
    age: 27,
    photo: "/profile_photos/james-person-1.jpg",
    bio: "Film nerd. Coffee snob. Weekend hiker. Looking for someone to debate Wong Kar-wai over ramen.",
    tags: ["Khruangbin", "A24 Films", "Python", "Rock Climbing"],
    distance: "3 miles away",
  },
  {
    name: "Sofia",
    age: 25,
    photo: "/profile_photos/james-person-1.jpg",
    bio: "Bookworm by day, vinyl collector by night. Will share my Spotify Wrapped if you share yours.",
    tags: ["Indie Music", "Letterboxd", "Cooking", "Yoga"],
    distance: "5 miles away",
  },
  {
    name: "Alex",
    age: 29,
    photo: "/profile_photos/james-person-1.jpg",
    bio: "Open source contributor. Sci-fi enthusiast. I make a mean espresso martini.",
    tags: ["TypeScript", "Dune", "Jazz", "Photography"],
    distance: "2 miles away",
  },
  {
    name: "Maya",
    age: 24,
    photo: "/profile_photos/james-person-1.jpg",
    bio: "Art history grad who can't stop rating films on Letterboxd. Let's explore a museum together.",
    tags: ["Art History", "Film", "Travel", "Matcha"],
    distance: "7 miles away",
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

export function SwipeScreen() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleSwipeLeft = useCallback(() => {
    setCurrentIndex((prev) => prev + 1);
  }, []);

  const handleSwipeRight = useCallback(() => {
    setCurrentIndex((prev) => prev + 1);
  }, []);

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
            style={{ width: 40, height: 40 }}
          />
        </div>

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

        {/* ── Match count ── */}
        {!noMoreCards && (
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
