"use client";

import { useWizardStore } from "@/lib/store";
import { ExternalLink, Lock, Shield } from "lucide-react";

function shortAddr(addr: string) {
  return addr.slice(0, 6) + "…" + addr.slice(-4);
}

export default function Step4Safe() {
  const { address, agentPubKey } = useWizardStore();

  const safeUrl =
    address && agentPubKey
      ? `https://app.safe.global/new-safe/create?owners=${address},${agentPubKey}&threshold=2`
      : "https://app.safe.global/new-safe/create";

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Set up Gnosis Safe</h2>
        <p className="text-gray-400 mt-1 text-sm">
          Create a 2-of-2 multisig — you and the agent are both required signers.
        </p>
      </div>

      {/* Signers */}
      <div className="rounded-2xl border border-gray-800 bg-gray-950 p-5 space-y-3">
        <p className="text-xs text-gray-500 uppercase tracking-wide">Signers (threshold: 2 of 2)</p>
        {[
          { label: "You (first signer)", addr: address, color: "indigo" },
          { label: "Agent (second signer)", addr: agentPubKey, color: "purple" },
        ].map(({ label, addr, color }) => (
          <div
            key={label}
            className="flex items-center justify-between rounded-xl bg-black border border-gray-800 px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center bg-${color}-950`}
              >
                <Shield className={`w-4 h-4 text-${color}-400`} />
              </div>
              <div>
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-sm text-white font-mono">
                  {addr ? shortAddr(addr) : <span className="text-gray-700">waiting…</span>}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Safe button */}
      <a
        href={safeUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-2 w-full rounded-xl py-3 bg-indigo-500 hover:bg-indigo-600 text-white font-semibold text-sm transition-all"
      >
        Create Safe on app.safe.global
        <ExternalLink className="w-4 h-4" />
      </a>

      {/* Auto-create stub */}
      <div className="flex items-center justify-between rounded-xl border border-gray-800 bg-gray-950 px-4 py-3 opacity-40">
        <div>
          <p className="text-sm text-gray-300 font-medium">Auto-create Safe</p>
          <p className="text-xs text-gray-600">Deploy Safe directly from this app</p>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-600">
          <Lock className="w-3 h-3" />
          Soon
        </div>
      </div>

      {/* Done */}
      <div className="rounded-2xl border border-green-900 bg-green-950/20 p-5 text-center">
        <p className="text-green-400 font-semibold text-sm">Setup complete</p>
        <p className="text-gray-400 text-xs mt-1">
          Once your Safe is live, every tx will flow through LastCheck automatically.
        </p>
      </div>
    </div>
  );
}
