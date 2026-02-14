import { useState } from "react";
import { PhotoUpload } from "./components/PhotoUpload/PhotoUpload";
import { ConnectAccounts } from "./components/ConnectAccounts/ConnectAccounts";
import { ProfileAnalysis } from "./components/ProfileAnalysis/ProfileAnalysis";
import { SwipeScreen } from "./components/SwipeScreen/SwipeScreen";

export default function App() {
  const [step, setStep] = useState(1);
  const [userPhoto, setUserPhoto] = useState<string | null>(null);
  const [identifiers, setIdentifiers] = useState<Record<string, string | null>>({});

  if (step === 1) return <PhotoUpload onContinue={(photos) => { setUserPhoto(photos[0] ?? null); setStep(2); }} />;
  if (step === 2) return <ConnectAccounts onContinue={(ids) => { setIdentifiers(ids); setStep(3); }} />;
  if (step === 3) return <ProfileAnalysis onContinue={() => setStep(4)} identifiers={identifiers} />;
  return <SwipeScreen userPhoto={userPhoto} />;
}
