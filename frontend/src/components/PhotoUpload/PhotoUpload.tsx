import { useState, useRef } from "react";
import "../ConnectAccounts/connectAccounts.css";
import { styles, COLORS, SURFACE, FONT_MONO } from "../ConnectAccounts/styles";
import { ChevronLeftIcon } from "../ConnectAccounts/icons";

const MAX_PHOTOS = 6;

interface PhotoUploadProps {
  onContinue: () => void;
}

function PlusIcon({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function XIcon({ size = 16, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export function PhotoUpload({ onContinue }: PhotoUploadProps) {
  const [photos, setPhotos] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const remaining = MAX_PHOTOS - photos.length;
    const toAdd = Array.from(files).slice(0, remaining);

    toAdd.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const result = ev.target?.result as string;
        setPhotos((prev) => {
          if (prev.length >= MAX_PHOTOS) return prev;
          return [...prev, result];
        });
      };
      reader.readAsDataURL(file);
    });

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removePhoto = (index: number) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const slots = Array.from({ length: MAX_PHOTOS }, (_, i) => photos[i] ?? null);

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

            <div style={styles.stepIndicator}>Step 1 of 4</div>
            <h1 style={styles.pageTitle}>Add your photos</h1>
            <p style={styles.subtitle}>
              Upload up to 6 photos to show off your personality. Your first photo will be your profile picture.
            </p>
          </header>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />

          {/* ── Photo grid ── */}
          <div style={{
            padding: "28px 24px 0",
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: 12,
          }}>
            {slots.map((photo, i) => (
              <div
                key={i}
                className="card-enter"
                onClick={() => !photo && photos.length < MAX_PHOTOS && fileInputRef.current?.click()}
                style={{
                  aspectRatio: "3 / 4",
                  borderRadius: 16,
                  background: photo ? "transparent" : "#5823A5",
                  border: photo ? "none" : `2px dashed ${COLORS.softPeriwinkle}40`,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: photo ? "default" : "pointer",
                  position: "relative",
                  overflow: "hidden",
                  animationDelay: `${i * 0.05}s`,
                }}
              >
                {photo ? (
                  <>
                    <img
                      src={photo}
                      alt={`Photo ${i + 1}`}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        borderRadius: 16,
                      }}
                    />
                    <button
                      onClick={(e) => { e.stopPropagation(); removePhoto(i); }}
                      style={{
                        position: "absolute",
                        top: 6,
                        right: 6,
                        width: 24,
                        height: 24,
                        borderRadius: 12,
                        background: "rgba(0,0,0,0.6)",
                        border: "none",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 0,
                      }}
                    >
                      <XIcon size={14} color="#fff" />
                    </button>
                    {i === 0 && (
                      <div style={{
                        position: "absolute",
                        bottom: 6,
                        left: 6,
                        fontSize: 9,
                        fontFamily: FONT_MONO,
                        fontWeight: 500,
                        textTransform: "uppercase",
                        letterSpacing: 1,
                        color: "#fff",
                        background: `${COLORS.softPeriwinkle}CC`,
                        padding: "2px 8px",
                        borderRadius: 6,
                      }}>
                        Profile
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <PlusIcon size={28} color={`${COLORS.softPeriwinkle}80`} />
                    <span style={{
                      fontSize: 11,
                      color: SURFACE.textTertiary,
                      marginTop: 4,
                    }}>
                      {i === 0 && photos.length === 0 ? "Main" : `${i + 1}`}
                    </span>
                  </>
                )}
              </div>
            ))}
          </div>

          {/* ── Photo count ── */}
          <div style={{
            padding: "20px 24px 0",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <span style={{ fontSize: 13, color: SURFACE.textSecondary }}>
              Photos uploaded
            </span>
            <span style={{
              fontSize: 13,
              fontWeight: 700,
              color: photos.length > 0 ? COLORS.softPeriwinkle : SURFACE.textTertiary,
            }}>
              {photos.length} / {MAX_PHOTOS}
            </span>
          </div>
          {photos.length === 0 && (
            <div style={{
              padding: "8px 24px 0",
              fontSize: 12,
              color: "rgba(255,255,255,0.3)",
            }}>
              Add at least 1 photo to continue
            </div>
          )}
        </div>

        {/* ── Sticky CTA ── */}
        <div style={styles.stickyBottom}>
          <button
            onClick={photos.length > 0 ? onContinue : undefined}
            style={{
              ...styles.ctaButton,
              background: photos.length > 0 ? COLORS.softPeriwinkle : `${COLORS.softPeriwinkle}4D`,
              color: photos.length > 0 ? "#fff" : "rgba(255,255,255,0.4)",
              pointerEvents: photos.length > 0 ? "auto" : "none",
            }}
          >
            Continue
          </button>
          <div style={styles.ctaHint}>You can always change these later</div>
        </div>
      </div>
    </div>
  );
}
