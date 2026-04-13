"use client";

import { useRouter } from "next/navigation";
import { useWizardStore, Tier } from "@/lib/store";
import { Check, Lock } from "lucide-react";
import { clsx } from "clsx";

const BASIC_FEATURES = [
  "MCP agent scans every tx",
  "YAML rule engine (hard enforcement)",
  "Telegram approval flow",
  "Web dashboard to edit rules",
  "Voice-to-rule via Telegram",
];

const AI_FEATURES = [
  "Everything in Basic",
  "AI simulation layer",
  "Nano Claw custom skills",
  "Separate isolated container",
];

const NOTIFICATION_TARGETS = [
  { label: "Telegram", enabled: true },
  { label: "Signal", enabled: false },
];

export default function Step2Tier() {
  const router = useRouter();
  const { tier, setTier } = useWizardStore((s) => ({ tier: s.tier, setTier: s.setTier }));

  function choose(t: Tier) {
    setTier(t);
    router.push("/setup/step3-deploy");
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Choose your protection tier</h2>
        <p className="text-gray-400 mt-1 text-sm">You can upgrade later.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Basic */}
        <button
          onClick={() => choose("basic")}
          className={clsx(
            "relative text-left rounded-2xl border p-6 transition-all hover:border-indigo-500",
            tier === "basic" ? "border-indigo-500 bg-indigo-950/40" : "border-gray-800 bg-gray-950"
          )}
        >
          <div className="text-indigo-400 font-semibold text-sm uppercase tracking-wide mb-1">Basic</div>
          <div className="text-white font-bold text-lg mb-4">Rule-based</div>
          <ul className="space-y-2">
            {BASIC_FEATURES.map((f) => (
              <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                <Check className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        </button>

        {/* AI — disabled */}
        <div
          title="In development"
          className="relative text-left rounded-2xl border border-gray-800 bg-gray-950 p-6 opacity-40 cursor-not-allowed"
        >
          <div className="absolute top-3 right-3">
            <span className="text-xs bg-gray-800 text-gray-400 rounded px-2 py-0.5 flex items-center gap-1">
              <Lock className="w-3 h-3" /> Soon
            </span>
          </div>
          <div className="text-purple-400 font-semibold text-sm uppercase tracking-wide mb-1">AI Layer</div>
          <div className="text-white font-bold text-lg mb-4">AI + Rules</div>
          <ul className="space-y-2">
            {AI_FEATURES.map((f) => (
              <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                <Check className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Notification targets */}
      <div className="rounded-2xl border border-gray-800 bg-gray-950 p-5">
        <p className="text-sm text-gray-400 mb-3 font-medium">Alert destination</p>
        <div className="flex gap-3">
          {NOTIFICATION_TARGETS.map(({ label, enabled }) => (
            <div
              key={label}
              className={clsx(
                "flex items-center gap-2 rounded-lg border px-4 py-2 text-sm",
                enabled
                  ? "border-indigo-600 bg-indigo-950 text-white"
                  : "border-gray-800 text-gray-600 opacity-50 cursor-not-allowed"
              )}
            >
              {enabled && <Check className="w-3.5 h-3.5 text-indigo-400" />}
              {!enabled && <Lock className="w-3.5 h-3.5" />}
              {label}
              {!enabled && <span className="text-xs text-gray-600">soon</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
