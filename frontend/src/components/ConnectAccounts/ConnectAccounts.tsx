import { useState, useCallback } from "react";
import "./connectAccounts.css";
import { styles, COLORS } from "./styles";
import { ServiceCard } from "./ServiceCard";
import { SignalStrength } from "./SignalStrength";
import { BottomSheet } from "./BottomSheet";
import { ChevronLeftIcon, MusicIcon, FilmIcon, CodeIcon, CameraIcon, LinkedInIcon } from "./icons";
import { connectService } from "../../services/api";

// ── Service definitions ──

type ServiceId = "spotify" | "letterboxd" | "github" | "instagram" | "linkedin";

interface ServiceDef {
  id: ServiceId;
  name: string;
  description: string;
  icon: React.ReactNode;
  brandColor: string;
  accentColor: string;
  required: boolean;
  signalWeight: number;
  mockPreview: string;
}

const SERVICES: ServiceDef[] = [
  {
    id: "spotify",
    name: "Spotify",
    description: "Music taste & listening habits",
    icon: <MusicIcon size={24} color="#BB97FF" />,
    brandColor: "#1DB954",
    accentColor: COLORS.limeCreem,
    required: false,
    signalWeight: 40,
    mockPreview: "Top artist: Khruangbin \u00b7 847 genres",
  },
  {
    id: "letterboxd",
    name: "Letterboxd",
    description: "Film taste & reviews",
    icon: <FilmIcon size={24} color="#BB97FF" />,
    brandColor: "#00E054",
    accentColor: "#00E054",
    required: false,
    signalWeight: 15,
    mockPreview: "142 films \u00b7 avg rating 3.8\u2605",
  },
  {
    id: "github",
    name: "GitHub",
    description: "Projects & coding schedule",
    icon: <CodeIcon size={24} color="#BB97FF" />,
    brandColor: "#8B949E",
    accentColor: COLORS.softPeriwinkle,
    required: false,
    signalWeight: 15,
    mockPreview: "23 repos \u00b7 mostly TypeScript",
  },
  {
    id: "instagram",
    name: "Instagram",
    description: "Your profile & visual identity",
    icon: <CameraIcon size={24} color="#BB97FF" />,
    brandColor: "#E1306C",
    accentColor: COLORS.hotFuchsia,
    required: false,
    signalWeight: 15,
    mockPreview: "@username \u00b7 aesthetic captured",
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    description: "Career & professional interests",
    icon: <LinkedInIcon size={24} color="#BB97FF" />,
    brandColor: "#0A66C2",
    accentColor: COLORS.brightAmber,
    required: false,
    signalWeight: 15,
    mockPreview: "Product Designer \u00b7 500+ connections",
  },
];

// ── Main screen ──

interface ConnectAccountsProps {
  onContinue?: (identifiers: Record<string, string | null>) => void;
}

export function ConnectAccounts({ onContinue }: ConnectAccountsProps) {
  const [connected, setConnected] = useState<Record<ServiceId, boolean>>({
    spotify: false,
    letterboxd: false,
    github: false,
    instagram: false,
    linkedin: false,
  });

  const [loading, setLoading] = useState<Record<ServiceId, boolean>>({
    spotify: false,
    letterboxd: false,
    github: false,
    instagram: false,
    linkedin: false,
  });

  const [previews, setPreviews] = useState<Record<ServiceId, string>>({
    spotify: "",
    letterboxd: "",
    github: "",
    instagram: "",
    linkedin: "",
  });

  const [usernames, setUsernames] = useState<Record<ServiceId, string | null>>({
    spotify: null,
    letterboxd: null,
    github: null,
    instagram: null,
    linkedin: null,
  });

  const [sheetService, setSheetService] = useState<ServiceDef | null>(null);

  const signalPercentage = SERVICES.reduce(
    (sum, s) => sum + (connected[s.id] ? s.signalWeight : 0),
    0,
  );

  const canContinue = Object.values(connected).some(Boolean);

  const realConnect = useCallback(async (id: ServiceId, username: string) => {
    setLoading((prev) => ({ ...prev, [id]: true }));
    setUsernames((prev) => ({ ...prev, [id]: username }));
    try {
      const result = await connectService(id, username);
      setPreviews((prev) => ({ ...prev, [id]: result.preview }));
      setConnected((prev) => ({ ...prev, [id]: true }));
    } catch {
      setPreviews((prev) => ({ ...prev, [id]: "Connected (limited data)" }));
      setConnected((prev) => ({ ...prev, [id]: true }));
    } finally {
      setLoading((prev) => ({ ...prev, [id]: false }));
    }
  }, []);

  const handleConnect = useCallback((service: ServiceDef) => {
    setSheetService(service);
  }, []);

  const handleSheetSubmit = useCallback((value: string) => {
    if (!sheetService) return;
    const id = sheetService.id;
    setSheetService(null);
    realConnect(id, value);
  }, [sheetService, realConnect]);

  const handleDisconnect = useCallback((id: ServiceId) => {
    setConnected((prev) => ({ ...prev, [id]: false }));
  }, []);

  return (
    <div style={styles.page}>
      <div style={styles.phoneFrame}>
        <div style={styles.scrollArea}>
          {/* ── Header ── */}
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

            <div style={styles.stepIndicator}>Step 2 of 4</div>
            <h1 style={styles.pageTitle}>Connect your world</h1>
            <p style={styles.subtitle}>
              We analyze your taste to find your perfect match. The more you connect, the better we get.
            </p>
          </header>

          {/* ── Service cards ── */}
          <div style={styles.cardList}>
            {SERVICES.map((service, i) => (
              <ServiceCard
                key={service.id}
                name={service.name}
                description={service.description}
                icon={service.icon}
                brandColor={service.accentColor}
                isRequired={service.required}
                isConnected={connected[service.id]}
                isLoading={loading[service.id]}
                onConnect={() => handleConnect(service)}
                onDisconnect={() => handleDisconnect(service.id)}
                dataPreview={previews[service.id] || service.mockPreview}
                index={i}
              />
            ))}
          </div>

          {/* ── Signal strength ── */}
          <SignalStrength percentage={signalPercentage} />
        </div>

        {/* ── Sticky CTA ── */}
        <div style={styles.stickyBottom}>
          <button
            onClick={canContinue ? () => onContinue?.(usernames) : undefined}
            style={{
              ...styles.ctaButton,
              background: canContinue ? COLORS.softPeriwinkle : `${COLORS.softPeriwinkle}4D`,
              color: canContinue ? "#fff" : "rgba(255,255,255,0.4)",
              pointerEvents: canContinue ? "auto" : "none",
            }}
          >
            Continue
          </button>
          <div style={styles.ctaHint}>You can always add more later</div>
        </div>

        {/* ── Bottom sheet ── */}
        {sheetService && (
          <BottomSheet
            serviceName={sheetService.name}
            serviceId={sheetService.id}
            brandColor={sheetService.accentColor}
            onClose={() => setSheetService(null)}
            onSubmit={handleSheetSubmit}
          />
        )}
      </div>
    </div>
  );
}
