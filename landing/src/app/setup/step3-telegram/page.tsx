"use client";

import { useWizardStore } from "@/lib/store";
import { withBase } from "@/lib/routes";
import { CheckCircle2 } from "lucide-react";

export default function Step3Telegram() {
  const { safeAddress } = useWizardStore();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Finalize Telegram bot setup</h2>
        <p className="mt-1 text-sm lc-muted">
          Add your multisig to the bot so approvals and alerts route correctly.
        </p>
      </div>

      <div className="lc-panel p-5">
        <p className="text-sm font-medium text-white">Telegram setup instructions</p>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm lc-muted">
          <li>Open your LastCheck Telegram bot (configured via TELEGRAM_TOKEN).</li>
          <li>Run the command: <span className="font-mono text-white/90">/start</span>.</li>
          <li>
            Set your protected Safe with:
            <span className="ml-2 rounded bg-black px-2 py-1 font-mono text-xs text-white/90">
              /set_safe {safeAddress || "0xYourSafeAddress"}
            </span>
          </li>
          <li>Send a test transaction and confirm you receive an approval prompt.</li>
        </ol>
      </div>

      <div className="lc-panel p-5">
        <p className="text-sm font-medium text-white">What happens next</p>
        <ul className="mt-3 space-y-2 text-sm lc-muted">
          <li>Clean transactions co-sign silently.</li>
          <li>Suspicious flows trigger Telegram approval before execution.</li>
          <li>Your Safe remains 2-of-2: you and the LastCheck agent signer.</li>
        </ul>
      </div>

      <div className="lc-panel-strong p-5 text-center">
        <div className="inline-flex items-center gap-2 text-[#ffb04a]">
          <CheckCircle2 className="h-5 w-5" />
          <span className="font-semibold">Congratulations — setup complete.</span>
        </div>
        <p className="mt-2 text-xs lc-muted">
          Your wallet is now protected by LastCheck co-signing with Telegram escalation.
        </p>
        <a
          href={withBase("/")}
          className="mt-4 inline-flex items-center justify-center rounded-xl bg-[#ff9b1f] px-4 py-2 text-sm font-semibold text-black transition hover:bg-[#ffb04a]"
        >
          Return to main page
        </a>
      </div>
    </div>
  );
}
