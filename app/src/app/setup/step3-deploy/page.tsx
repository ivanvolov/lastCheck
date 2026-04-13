"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useWizardStore, DeployTarget } from "@/lib/store";
import { clsx } from "clsx";
import { Server, Cloud, Lock, Copy, Check } from "lucide-react";

const TARGETS: { id: DeployTarget; label: string; icon: React.ReactNode; enabled: boolean }[] = [
  { id: "docker", label: "Docker", icon: <Server className="w-5 h-5" />, enabled: true },
  { id: "gcloud", label: "Google Cloud", icon: <Cloud className="w-5 h-5" />, enabled: false },
  { id: "aws", label: "AWS", icon: <Cloud className="w-5 h-5" />, enabled: false },
];

function DockerSnippet({
  telegramToken,
  telegramChatId,
  firstSigner,
}: {
  telegramToken: string;
  telegramChatId: string;
  firstSigner: string;
}) {
  const [copied, setCopied] = useState(false);
  const snippet = `docker run -d \\
  -e TELEGRAM_TOKEN="${telegramToken || "YOUR_BOT_TOKEN"}" \\
  -e TELEGRAM_CHAT_ID="${telegramChatId || "YOUR_CHAT_ID"}" \\
  -e FIRST_SIGNER="${firstSigner || "YOUR_WALLET_ADDRESS"}" \\
  -p 8501:8501 \\
  ghcr.io/lastcheck/engine:latest`;

  function copy() {
    navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="relative rounded-xl bg-black border border-gray-800 p-4 font-mono text-xs text-gray-300 leading-relaxed">
      <button
        onClick={copy}
        className="absolute top-3 right-3 text-gray-600 hover:text-white transition-colors"
      >
        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
      </button>
      <pre>{snippet}</pre>
    </div>
  );
}

export default function Step3Deploy() {
  const router = useRouter();
  const { deployTarget, setDeployTarget, telegramToken, telegramChatId, setTelegramToken, setTelegramChatId, address } =
    useWizardStore();
  const [waiting, setWaiting] = useState(false);

  function selectTarget(id: DeployTarget) {
    setDeployTarget(id);
  }

  function handleContinue() {
    setWaiting(true);
    // In a real app, poll for the agent's public key broadcast to Telegram.
    // For the prototype, simulate after 2s.
    setTimeout(() => {
      useWizardStore.getState().setAgentPubKey("0x" + "a".repeat(40));
      router.push("/setup/step4-safe");
    }, 2000);
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Deploy the agent</h2>
        <p className="text-gray-400 mt-1 text-sm">Choose where to run your engine.</p>
      </div>

      {/* Target selector */}
      <div className="grid grid-cols-3 gap-3">
        {TARGETS.map((t) => (
          <button
            key={t.id}
            disabled={!t.enabled}
            onClick={() => t.enabled && selectTarget(t.id)}
            title={t.enabled ? undefined : "Coming soon"}
            className={clsx(
              "flex flex-col items-center gap-2 rounded-xl border p-4 text-sm font-medium transition-all",
              t.enabled && deployTarget === t.id && "border-indigo-500 bg-indigo-950/40 text-white",
              t.enabled && deployTarget !== t.id && "border-gray-800 bg-gray-950 text-gray-300 hover:border-gray-600",
              !t.enabled && "border-gray-800 bg-gray-950 text-gray-700 opacity-40 cursor-not-allowed"
            )}
          >
            {t.icon}
            {t.label}
            {!t.enabled && <Lock className="w-3 h-3" />}
          </button>
        ))}
      </div>

      {/* Telegram config */}
      <div className="rounded-2xl border border-gray-800 bg-gray-950 p-5 space-y-4">
        <p className="text-sm font-medium text-gray-300">Telegram credentials</p>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Bot token</label>
            <input
              type="text"
              placeholder="123456:ABC-DEF..."
              value={telegramToken}
              onChange={(e) => setTelegramToken(e.target.value)}
              className="w-full rounded-lg bg-black border border-gray-800 text-white text-sm px-3 py-2 placeholder-gray-700 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Chat ID</label>
            <input
              type="text"
              placeholder="-100123456789"
              value={telegramChatId}
              onChange={(e) => setTelegramChatId(e.target.value)}
              className="w-full rounded-lg bg-black border border-gray-800 text-white text-sm px-3 py-2 placeholder-gray-700 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Docker snippet */}
      {deployTarget === "docker" && (
        <div className="space-y-2">
          <p className="text-xs text-gray-500">Run this on your server:</p>
          <DockerSnippet
            telegramToken={telegramToken}
            telegramChatId={telegramChatId}
            firstSigner={address ?? ""}
          />
        </div>
      )}

      {/* Continue */}
      <button
        onClick={handleContinue}
        disabled={!deployTarget || waiting}
        className={clsx(
          "w-full rounded-xl py-3 font-semibold text-sm transition-all",
          deployTarget && !waiting
            ? "bg-indigo-500 hover:bg-indigo-600 text-white"
            : "bg-gray-800 text-gray-600 cursor-not-allowed"
        )}
      >
        {waiting ? "Waiting for agent public key…" : "I've started the agent →"}
      </button>
    </div>
  );
}
