import { useState } from "react";
import { PhotoUpload } from "./components/PhotoUpload/PhotoUpload";
import { ConnectAccounts } from "./components/ConnectAccounts/ConnectAccounts";
import { SwipeScreen } from "./components/SwipeScreen/SwipeScreen";

export default function App() {
  const [step, setStep] = useState(1);

  if (step === 1) return <PhotoUpload onContinue={() => setStep(2)} />;
  if (step === 2) return <ConnectAccounts onContinue={() => setStep(3)} />;
  return <SwipeScreen />;
}
