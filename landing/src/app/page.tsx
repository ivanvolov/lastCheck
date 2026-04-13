import {
  ArrowRight,
  Bot,
  ChevronRight,
  Github,
  LockKeyhole,
  MessageSquareWarning,
  Server,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import { SectionHeading } from "@/components/section-heading";

const GITHUB_REPO = "https://github.com/ivanvolov/lastCheck";

/** Prefix for static assets under GitHub Pages project sites (`BASE_PATH=/repo-name`). */
function withBase(path: string): string {
  const base = process.env.BASE_PATH || "";
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`;
}

function appOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_APP_ORIGIN;
  if (typeof raw === "string" && raw.length > 0) {
    return raw.replace(/\/$/, "");
  }
  return "http://localhost:3000";
}

const setupUrl = `${appOrigin()}/setup/step1-connect`;

const PAIN_POINTS = [
  {
    title: "Hardware wallets",
    copy: "They can flag known bad transactions, but the screen is tiny and the rules are not configurable.",
  },
  {
    title: "Browser wallets",
    copy: "Better warnings than a ledger display, but you cannot encode “allow Uniswap up to $5k, block everything else.”",
  },
  {
    title: "On-chain modules",
    copy: "Zodiac and Safe guards are powerful, but raising a limit for an afternoon still feels like editing infrastructure.",
  },
  {
    title: "Enterprise firewalls",
    copy: "Strong for DAO treasuries, but priced and operated like enterprise software — not for individuals at home.",
  },
];

const FLOW = [
  {
    title: "Hard rules first",
    copy: "You define limits in plain English. LastCheck compiles them into deterministic rules the agent cannot override.",
    icon: LockKeyhole,
  },
  {
    title: "AI reviews what remains",
    copy: "Transactions that pass the rules are simulated and checked for unusual behavior before the agent signs.",
    icon: Bot,
  },
  {
    title: "You decide when it looks off",
    copy: "Suspicious flows trigger an alert — Telegram, Signal, or hardware — so you approve or reject in context.",
    icon: MessageSquareWarning,
  },
];

const BENEFITS = [
  "Invisible when things look normal — no extra co-signing UI on every click.",
  "Configurable like a spending limit: dashboard slider or a voice note to your Telegram bot.",
  "Self-hosted: your transaction history and rules never leave your infrastructure.",
];

const PREVIEW_STEPS = [
  "Connect the wallet you already use.",
  "Choose the protection tier you want to start with.",
  "Deploy the engine and receive the agent signer.",
  "Create the Safe and route every transaction through LastCheck.",
];

export default function Home() {
  return (
    <main className="lc-shell">
      <section className="lc-container relative pt-8 pb-16 sm:pt-10 sm:pb-24">
        <div className="lc-panel flex items-center justify-between gap-6 px-5 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
              <ShieldCheck className="h-5 w-5 text-[#9ef0d0]" />
            </div>
            <div>
              <p className="font-semibold text-white">LastCheck</p>
              <p className="text-sm lc-muted">Self-hosted AI co-signer</p>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <a
              href={GITHUB_REPO}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl px-2 py-2 text-sm lc-muted transition hover:bg-white/5 hover:text-white sm:px-0"
              aria-label="LastCheck on GitHub"
            >
              <Github className="h-4 w-4 shrink-0" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
            <a href={setupUrl} className="lc-button-secondary whitespace-nowrap text-sm sm:text-base">
              Start setup
            </a>
          </div>
        </div>

        <div className="grid gap-10 pt-14 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div className="space-y-8">
            <div className="space-y-5">
              <span className="lc-badge">
                <span className="h-2 w-2 rounded-full bg-[#9ef0d0]" />
                Last line of defense before execution
              </span>
              <h1 className="max-w-4xl text-balance text-5xl font-semibold leading-[0.95] text-white sm:text-6xl lg:text-7xl">
                Stop blind signing before it becomes a loss.
              </h1>
              <p className="max-w-2xl text-lg leading-8 lc-muted sm:text-xl">
                A self-hosted agent acts as a mandatory co-signer on your wallet:{" "}
                <strong className="font-semibold text-white/90">hard rules</strong> you define in
                plain English, then <strong className="font-semibold text-white/90">AI review</strong>{" "}
                for everything that passes. Nothing overrides your YAML. When it looks off, you
                decide — in Telegram, Signal, or on a hardware device.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <a href={setupUrl} className="lc-button-primary">
                Protect a wallet
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
              <a href="#how-it-works" className="lc-button-secondary">
                See how it works
              </a>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                ["Invisible by default", "No extra UI when everything looks normal."],
                ["Configurable in minutes", "Tune limits like spending controls, not security code."],
                ["Self-hosted", "Your data and your transaction review stay on your own infra."],
              ].map(([title, copy]) => (
                <div key={title} className="lc-list-item">
                  <div>
                    <p className="text-sm font-semibold text-white">{title}</p>
                    <p className="mt-2 text-sm leading-6 lc-muted">{copy}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lc-panel-strong relative overflow-hidden p-6 sm:p-8">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#9ef0d0]/50 to-transparent" />
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">Live policy preview</p>
                  <p className="mt-1 text-sm lc-muted">The kind of control normal wallets never offer.</p>
                </div>
                <span className="rounded-full border border-[#9ef0d0]/20 bg-[#9ef0d0]/10 px-3 py-1 text-xs font-semibold text-[#9ef0d0]">
                  Active
                </span>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-black/20 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-white">Swap allowance</p>
                    <p className="mt-2 text-sm leading-6 lc-muted">
                      Allow trusted DEX usage up to a daily threshold. Escalate anything above it.
                    </p>
                  </div>
                  <SlidersHorizontal className="h-5 w-5 text-[#f5c97a]" />
                </div>
                <div className="mt-5 space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="lc-muted">Trusted protocols</span>
                    <span className="font-medium text-white">Uniswap, CowSwap</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="lc-muted">Daily cap</span>
                    <span className="font-medium text-white">$5,000</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/5">
                    <div className="h-full w-[58%] rounded-full bg-gradient-to-r from-[#9ef0d0] to-[#72d8b7]" />
                  </div>
                </div>
              </div>

              <div className="grid gap-3">
                {[
                  ["Incoming transaction", "Approve Uniswap swap for 0.85 ETH"],
                  ["Rule verdict", "Allowed by hard rules"],
                  ["AI verdict", "No unusual execution pattern detected"],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3"
                  >
                    <span className="text-sm lc-muted">{label}</span>
                    <span className="text-sm font-medium text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="lc-container py-16 sm:py-24">
        <SectionHeading
          eyebrow="How it works"
          title="Hard rules first, then AI — two layers before the agent signs."
          description="Generic warnings optimize for the average user. LastCheck enforces your stated limits and asks you when behavior diverges from what you actually do."
        />

        <div className="mt-10 grid gap-4 lg:grid-cols-3">
          {FLOW.map(({ title, copy, icon: Icon }, index) => (
            <div key={title} className="lc-panel p-6">
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                  <Icon className="h-5 w-5 text-[#9ef0d0]" />
                </div>
                <span className="text-sm lc-muted">0{index + 1}</span>
              </div>
              <h3 className="mt-6 text-2xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-7 lc-muted">{copy}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="lc-container py-16 sm:py-24">
        <div className="lc-panel-strong overflow-hidden p-6 sm:p-8">
          <SectionHeading
            eyebrow="Transaction flow"
            title="From proposal to execution — with a reject path at every step."
            description="Rules block what you already said no to. AI escalates novel risk. You stay one message away from a wrong signature."
          />
          <figure className="mt-8">
            <img
              src={withBase("/flow-diagram.svg")}
              alt="Flow: transaction proposed, hard rules may reject, AI review may alert via Telegram Signal or hardware, then agent co-signs and execution proceeds"
              className="mx-auto w-full max-w-3xl rounded-2xl border border-white/10 bg-[#061015]/40"
              width={720}
              height={420}
              loading="lazy"
            />
            <figcaption className="mt-4 text-center text-sm lc-muted">
              Self-hosted — your policies and history stay on your infrastructure.{" "}
              <a href={GITHUB_REPO} target="_blank" rel="noreferrer" className="text-[#9ef0d0] underline-offset-4 hover:underline">
                Source on GitHub
              </a>
            </figcaption>
          </figure>
        </div>
      </section>

      <section className="lc-container py-16 sm:py-24">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="lc-panel p-7 sm:p-8">
            <SectionHeading
              eyebrow="Reality"
              title="Existing defenses protect the average user — not your specific usage."
              description="Phishing, malicious approvals, and spoofed frontends succeed because warnings are easy to dismiss and not calibrated to you. LastCheck shifts the model: your limits, your patterns, your veto."
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {PAIN_POINTS.map((item) => (
              <div key={item.title} className="lc-list-item">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                  <ChevronRight className="h-4 w-4 text-[#f5c97a]" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">{item.title}</p>
                  <p className="mt-2 text-sm leading-7 lc-muted">{item.copy}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="lc-container py-16 sm:py-24">
        <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="lc-panel-strong p-7 sm:p-8">
            <SectionHeading
              eyebrow="Benefits"
              title="Security that behaves more like a product than a policy engine."
              description="You should be able to raise your risk limits for a trading day and lower them again without touching multisig internals."
            />
            <div className="mt-8 space-y-3">
              {BENEFITS.map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <ShieldCheck className="mt-0.5 h-4 w-4 text-[#9ef0d0]" />
                  <p className="text-sm leading-7 text-white/88">{item}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="lc-panel p-7 sm:p-8">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                <Server className="h-5 w-5 text-[#9ef0d0]" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">Simple self-hosted rollout</p>
                <p className="mt-1 text-sm lc-muted">The setup flow gets you from wallet to Safe in four steps.</p>
              </div>
            </div>
            <div className="mt-8 space-y-3">
              {PREVIEW_STEPS.map((step, index) => (
                <div
                  key={step}
                  className="flex items-center gap-4 rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4"
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#9ef0d0]/20 bg-[#9ef0d0]/10 text-sm font-semibold text-[#9ef0d0]">
                    {index + 1}
                  </div>
                  <p className="text-sm text-white/88">{step}</p>
                </div>
              ))}
            </div>
            <a href={setupUrl} className="mt-8 inline-flex items-center text-sm font-semibold text-[#9ef0d0]">
              Open onboarding
              <ArrowRight className="ml-2 h-4 w-4" />
            </a>
          </div>
        </div>
      </section>

      <section className="lc-container pb-20 sm:pb-28">
        <div className="lc-panel-strong overflow-hidden px-6 py-8 sm:px-10 sm:py-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="lc-eyebrow">Start with one wallet</p>
              <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
                Get a transaction firewall in front of your next signature.
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 lc-muted sm:text-lg">
                Connect a wallet, deploy the agent, and create the Safe that makes LastCheck your
                final checkpoint before execution.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              <a href={setupUrl} className="lc-button-primary">
                Start setup
              </a>
              <a href={GITHUB_REPO} target="_blank" rel="noreferrer" className="lc-button-secondary">
                <span className="inline-flex items-center justify-center gap-2">
                  <Github className="h-4 w-4" />
                  View on GitHub
                </span>
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
