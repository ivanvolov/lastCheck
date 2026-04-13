"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useAccount } from "wagmi";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useWizardStore } from "@/lib/store";
import { Shield } from "lucide-react";

export default function Step1Connect() {
  const { address, isConnected } = useAccount();
  const router = useRouter();
  const setAddress = useWizardStore((s) => s.setAddress);

  useEffect(() => {
    if (isConnected && address) {
      setAddress(address);
      router.push("/setup/step2-tier");
    }
  }, [isConnected, address, setAddress, router]);

  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-950 p-8 text-center space-y-6">
      <div className="flex justify-center">
        <div className="w-16 h-16 rounded-full bg-indigo-950 flex items-center justify-center">
          <Shield className="w-8 h-8 text-indigo-400" />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-white">Connect your wallet</h2>
        <p className="text-gray-400 mt-2 text-sm leading-relaxed">
          LastCheck will wrap it into a Gnosis Safe where the agent becomes a mandatory
          co-signer. Your keys stay yours.
        </p>
      </div>

      <div className="flex justify-center">
        <ConnectButton />
      </div>

      {/* Hardware wallet stubs */}
      <div className="border-t border-gray-800 pt-4">
        <p className="text-xs text-gray-600 mb-3">Or connect a hardware wallet</p>
        <div className="flex gap-3 justify-center">
          {["Ledger", "Trezor"].map((hw) => (
            <button
              key={hw}
              disabled
              title="Coming soon"
              className="flex items-center gap-2 rounded-lg border border-gray-800 px-4 py-2 text-sm text-gray-700 cursor-not-allowed opacity-50"
            >
              {hw}
              <span className="text-xs bg-gray-800 text-gray-500 rounded px-1">soon</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
