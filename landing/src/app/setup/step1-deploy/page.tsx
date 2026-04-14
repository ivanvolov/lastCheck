"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useWizardStore, DeployTarget } from "@/lib/store";
import { clsx } from "clsx";
import { Check, Cloud, Copy, Lock, Server } from "lucide-react";

const IMAGE = "ghcr.io/ivanvolov/lastcheck-engine:latest";

const TARGETS: { id: DeployTarget; label: string; enabled: boolean; icon: React.ReactNode }[] = [
  { id: "docker", label: "Docker", enabled: true, icon: <Server className="h-5 w-5" /> },
  { id: "gcloud", label: "Google Cloud", enabled: false, icon: <Cloud className="h-5 w-5" /> },
  { id: "aws", label: "AWS", enabled: false, icon: <Cloud className="h-5 w-5" /> },
  { id: "tee", label: "TEE", enabled: false, icon: <Cloud className="h-5 w-5" /> },
];

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="inline-flex items-center gap-2 rounded-lg border border-gray-700 px-3 py-1.5 text-xs text-gray-300 hover:border-gray-500 hover:text-white"
    >
      {copied ? <Check className="h-3.5 w-3.5 text-green-400" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export default function Step1Deploy() {
  const router = useRouter();
  const [showTenderly, setShowTenderly] = useState(false);
  const {
    deployTarget,
    setDeployTarget,
    rpcUrl,
    setRpcUrl,
    openAiApiKey,
    setOpenAiApiKey,
    tenderlyAccessKey,
    setTenderlyAccessKey,
    tenderlyAccountSlug,
    setTenderlyAccountSlug,
    tenderlyProjectSlug,
    setTenderlyProjectSlug,
    tenderlyNetworkId,
    setTenderlyNetworkId,
    dashboardPort,
    setDashboardPort,
    telegramToken,
    setTelegramToken,
  } = useWizardStore();

  const dockerCommand = useMemo(() => {
    const lines = [
      "docker run -d \\",
      "  --name lastcheck-engine \\",
      `  -e TELEGRAM_TOKEN="${telegramToken || "YOUR_TELEGRAM_TOKEN"}" \\`,
      `  -e ETH_RPC_URL="${rpcUrl || "YOUR_ETH_RPC_URL"}" \\`,
      `  -e OPENAI_API_KEY="${openAiApiKey || "YOUR_OPENAI_API_KEY"}" \\`,
    ];

    if (tenderlyAccessKey.trim()) {
      lines.push(`  -e TENDERLY_ACCESS_KEY="${tenderlyAccessKey}" \\`);
    }
    if (tenderlyAccountSlug.trim()) {
      lines.push(`  -e TENDERLY_ACCOUNT_SLUG="${tenderlyAccountSlug}" \\`);
    }
    if (tenderlyProjectSlug.trim()) {
      lines.push(`  -e TENDERLY_PROJECT_SLUG="${tenderlyProjectSlug}" \\`);
    }
    if (tenderlyNetworkId.trim()) {
      lines.push(`  -e TENDERLY_NETWORK_ID="${tenderlyNetworkId}" \\`);
    }

    lines.push(
      `  -e DASHBOARD_PORT="${dashboardPort || "8501"}" \\`,
      `  -p ${dashboardPort || "8501"}:${dashboardPort || "8501"} \\`,
      `  ${IMAGE}`
    );

    return lines.join("\n");
  }, [
    dashboardPort,
    openAiApiKey,
    rpcUrl,
    telegramToken,
    tenderlyAccessKey,
    tenderlyAccountSlug,
    tenderlyNetworkId,
    tenderlyProjectSlug,
  ]);

  const isReady =
    deployTarget === "docker" &&
    rpcUrl.trim().length > 0 &&
    openAiApiKey.trim().length > 0 &&
    telegramToken.trim().length > 0;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Choose deployment type</h2>
        <p className="mt-1 text-sm lc-muted">Docker is available now. Cloud options are coming soon.</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {TARGETS.map((target) => (
          <button
            key={target.id}
            disabled={!target.enabled}
            onClick={() => target.enabled && setDeployTarget(target.id)}
            className={clsx(
              "flex items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition",
              target.enabled && deployTarget === target.id && "border-[#ff9b1f] bg-[#ff9b1f]/10 text-white",
              target.enabled && deployTarget !== target.id && "border-gray-800 bg-black/40 text-gray-200 hover:border-gray-600",
              !target.enabled && "cursor-not-allowed border-gray-800 bg-gray-950 text-gray-600 opacity-50"
            )}
          >
            <span className="inline-flex items-center gap-2">
              {target.icon}
              {target.label}
            </span>
            {!target.enabled && <Lock className="h-3.5 w-3.5" />}
          </button>
        ))}
      </div>

      {deployTarget === "docker" && (
        <>
          <div className="lc-panel p-5 space-y-4">
            <p className="text-sm font-medium text-white/90">Docker environment values</p>
            <div className="space-y-3">
              <label className="block">
                <span className="mb-1 block text-xs lc-muted">ETH_RPC_URL</span>
                <input
                  value={rpcUrl}
                  onChange={(e) => setRpcUrl(e.target.value)}
                  placeholder="https://eth-mainnet.g.alchemy.com/v2/..."
                  className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs lc-muted">OPENAI_API_KEY</span>
                <input
                  value={openAiApiKey}
                  onChange={(e) => setOpenAiApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs lc-muted">TELEGRAM_TOKEN</span>
                <input
                  value={telegramToken}
                  onChange={(e) => setTelegramToken(e.target.value)}
                  placeholder="123456:ABC-DEF..."
                  className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                />
              </label>
              <div className="rounded-xl border border-gray-800 bg-black/30">
                <button
                  type="button"
                  onClick={() => setShowTenderly((prev) => !prev)}
                  className="flex w-full items-center justify-between px-3 py-2 text-left text-xs text-white/90"
                >
                  <span>Tenderly (optional)</span>
                  <span className="text-[#ffb04a]">{showTenderly ? "Hide" : "Show"}</span>
                </button>
                {showTenderly && (
                  <div className="space-y-3 border-t border-gray-800 px-3 py-3">
                    <label className="block">
                      <span className="mb-1 block text-xs lc-muted">TENDERLY_ACCESS_KEY</span>
                      <input
                        value={tenderlyAccessKey}
                        onChange={(e) => setTenderlyAccessKey(e.target.value)}
                        placeholder="tly_..."
                        className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-1 block text-xs lc-muted">TENDERLY_ACCOUNT_SLUG</span>
                      <input
                        value={tenderlyAccountSlug}
                        onChange={(e) => setTenderlyAccountSlug(e.target.value)}
                        placeholder="your-account"
                        className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-1 block text-xs lc-muted">TENDERLY_PROJECT_SLUG</span>
                      <input
                        value={tenderlyProjectSlug}
                        onChange={(e) => setTenderlyProjectSlug(e.target.value)}
                        placeholder="your-project"
                        className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-1 block text-xs lc-muted">TENDERLY_NETWORK_ID</span>
                      <input
                        value={tenderlyNetworkId}
                        onChange={(e) => setTenderlyNetworkId(e.target.value)}
                        placeholder="42161"
                        className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                      />
                    </label>
                  </div>
                )}
              </div>
              <label className="block">
                <span className="mb-1 block text-xs lc-muted">DASHBOARD_PORT</span>
                <input
                  value={dashboardPort}
                  onChange={(e) => setDashboardPort(e.target.value)}
                  placeholder="8501"
                  className="w-full rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm text-white placeholder-gray-700 focus:border-[#ff9b1f] focus:outline-none"
                />
              </label>
            </div>
          </div>

          <div className="lc-panel p-5 space-y-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-white/90">Docker image</p>
              <CopyButton value={IMAGE} />
            </div>
            <pre className="overflow-x-auto rounded-xl border border-gray-800 bg-black p-3 font-mono text-xs text-gray-300">
              {IMAGE}
            </pre>

            <div className="flex items-center justify-between gap-3 pt-1">
              <p className="text-sm font-medium text-white/90">Docker run command</p>
              <CopyButton value={dockerCommand} />
            </div>
            <pre className="overflow-x-auto rounded-xl border border-gray-800 bg-black p-3 font-mono text-xs text-gray-300">
              {dockerCommand}
            </pre>
          </div>

          <div className="lc-panel p-5">
            <p className="text-sm font-medium text-white">Next actions after running Docker</p>
            <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm lc-muted">
              <li>Run the command on your server.</li>
              <li>
                Open the container logs and find the pairing line:
                <code className="mx-1 rounded bg-black/60 px-1.5 py-0.5 font-mono text-xs text-gray-200">
                  /start &lt;code&gt;
                </code>
              </li>
              <li>
                In Telegram, send that{" "}
                <code className="rounded bg-black/60 px-1.5 py-0.5 font-mono text-xs text-gray-200">
                  /start &lt;code&gt;
                </code>{" "}
                to your bot. It pairs with your chat and saves the chat id to settings automatically.
              </li>
              <li>
                The bot will then either generate a fresh agent key and show its address, or — if a key
                already exists — show two buttons: tap{" "}
                <span className="text-white/90">Get public key</span> to reveal it, or{" "}
                <span className="text-white/90">Regenerate</span> for a new one.
              </li>
              <li>
                Copy that agent address — you&apos;ll use it as the Safe&apos;s second signer in the next step.
              </li>
            </ol>
          </div>
        </>
      )}

      <button
        onClick={() => router.push("/setup/step2-safe")}
        disabled={!isReady}
        className={clsx(
          "w-full rounded-xl py-3 text-sm font-semibold transition",
          isReady ? "lc-button-primary" : "cursor-not-allowed bg-gray-800 text-gray-600"
        )}
      >
        Continue to wallet + multisig
      </button>
    </div>
  );
}
