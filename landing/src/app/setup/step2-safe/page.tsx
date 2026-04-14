"use client";

import { useEffect, useState } from "react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useAccount } from "wagmi";
import { useRouter } from "next/navigation";
import { useWizardStore } from "@/lib/store";
import { clsx } from "clsx";
import { ExternalLink, Shield } from "lucide-react";

function shortAddr(addr: string) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

export default function Step2Safe() {
  const router = useRouter();
  const { address: connectedAddress, isConnected } = useAccount();
  const {
    address,
    setAddress,
    agentPubKey,
    setAgentPubKey,
    safeAddress,
    setSafeAddress,
  } = useWizardStore();
  const [draftAgent, setDraftAgent] = useState(agentPubKey ?? "");
  const [draftSafe, setDraftSafe] = useState(safeAddress ?? "");

  useEffect(() => {
    if (isConnected && connectedAddress && connectedAddress !== address) {
      setAddress(connectedAddress);
    }
  }, [address, connectedAddress, isConnected, setAddress]);

  const firstSigner = connectedAddress ?? address;

  const safeUrl =
    firstSigner && draftAgent.trim().length > 0
      ? `https://app.safe.global/new-safe/create?owners=${firstSigner},${draftAgent.trim()}&threshold=2`
      : "https://app.safe.global/new-safe/create";

  const canSave = Boolean(firstSigner && draftAgent.trim().length > 0 && draftSafe.trim().length > 0);

  function saveAndContinue() {
    if (!canSave) return;
    setAgentPubKey(draftAgent.trim());
    setSafeAddress(draftSafe.trim());
    router.push("/setup/step3-telegram");
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Connect wallet and create multisig</h2>
        <p className="mt-1 text-sm lc-muted">Create a 2-of-2 Safe with your wallet + agent signer.</p>
      </div>

      <div className="lc-panel p-5">
        <p className="text-sm font-medium text-white">1) Connect wallet</p>
        <div className="mt-3 flex items-center justify-between rounded-xl border border-gray-800 bg-black px-4 py-3">
          <div>
            <p className="text-xs lc-muted">Detected wallet address</p>
            <p className="mt-1 font-mono text-sm text-white">
              {firstSigner ? shortAddr(firstSigner) : <span className="text-gray-600">Not connected</span>}
            </p>
          </div>
          <ConnectButton />
        </div>
      </div>

      <div className="lc-panel p-5 space-y-3">
        <p className="text-sm font-medium text-white">2) Paste agent public address</p>
        <p className="text-xs lc-muted">
          After the Docker container starts, copy the generated public key (agent signer) and paste it here.
        </p>
        <input
          value={draftAgent}
          onChange={(e) => setDraftAgent(e.target.value)}
          placeholder="0xAgentPublicAddress"
          className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
        />
      </div>

      <div className="lc-panel p-5 space-y-3">
        <p className="text-sm font-medium text-white">3) Create Safe multisig</p>
        <a
          href={safeUrl}
          target="_blank"
          rel="noreferrer"
          className={clsx(
            "inline-flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition",
            firstSigner && draftAgent.trim()
              ? "bg-[#ff9b1f] text-black hover:bg-[#ffb04a]"
              : "pointer-events-none bg-gray-800 text-gray-600"
          )}
        >
          Open Safe create flow
          <ExternalLink className="h-4 w-4" />
        </a>
        <p className="text-xs lc-muted">
          Use owner 1 = your wallet, owner 2 = agent signer, threshold = 2 of 2.
        </p>
      </div>

      <div className="lc-panel p-5 space-y-3">
        <p className="text-sm font-medium text-white">4) Register the Safe with your agent</p>
        <p className="text-xs lc-muted">
          Once the Safe is deployed, open Telegram and send{" "}
          <code className="rounded bg-black/60 px-1.5 py-0.5 font-mono text-[11px] text-gray-200">
            /connect_safe
          </code>{" "}
          to your bot. It will ask for the Safe address — paste it there. The bot persists it to
          settings and the watcher starts monitoring immediately.
        </p>
        <input
          value={draftSafe}
          onChange={(e) => setDraftSafe(e.target.value)}
          placeholder="0x6F4F4da5DD8546c625Ab3a3aF6B4797B66f56f14"
          className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
        />
        <button
          onClick={saveAndContinue}
          disabled={!canSave}
          className={clsx(
            "w-full rounded-xl py-3 text-sm font-semibold transition",
            canSave ? "bg-[#ff9b1f] text-black hover:bg-[#ffb04a]" : "cursor-not-allowed bg-gray-800 text-gray-600"
          )}
        >
          Register the Safe with your agent
        </button>
      </div>

      <div className="lc-panel p-4">
        <div className="flex items-center gap-2 text-xs lc-muted">
          <Shield className="h-4 w-4 text-[#ffb04a]" />
          LastCheck uses 2-of-2 signing: you + agent must both approve.
        </div>
      </div>
    </div>
  );
}
