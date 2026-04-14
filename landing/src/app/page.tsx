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
    title: "Set non-negotiable rules",
    copy: "Define guardrails in plain English. LastCheck compiles them into deterministic rules the AI cannot override.",
    icon: LockKeyhole,
  },
  {
    title: "AI inspects what passes",
    copy: "Transactions that clear your rules are simulated and reviewed for anomalous behavior before co-signing.",
    icon: Bot,
  },
  {
    title: "You approve the edge cases",
    copy: "Suspicious activity triggers alerts in Telegram, Signal, or on hardware devices so you approve or reject in context.",
    icon: MessageSquareWarning,
  },
];

const BENEFITS = [
  "Runs quietly in the background when transactions match your normal behavior.",
  "Adapts fast when your risk appetite changes: slider or Telegram voice command.",
  "Self-hosted by design: your policy logic and transaction context stay under your control.",
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
              <ShieldCheck className="h-5 w-5 text-[#ffb04a]" />
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
                <span className="h-2 w-2 rounded-full bg-[#ff9b1f]" />
                The final checkpoint before execution
              </span>
              <h1 className="max-w-4xl text-balance text-5xl font-semibold leading-[0.95] text-white sm:text-6xl lg:text-7xl">
                Your AI co-signer for every high-stakes transaction.
              </h1>
              <p className="max-w-2xl text-lg leading-8 lc-muted sm:text-xl">
                LastCheck adds a mandatory, self-hosted co-signer between your wallet and execution.
                First, it enforces <strong className="font-semibold text-white/90">hard rules</strong>{" "}
                from your own policy. Then <strong className="font-semibold text-white/90">AI review</strong>{" "}
                checks what remains for unusual behavior. If something looks wrong, you get the final
                say in Telegram, Signal, or on hardware devices.
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
                ["Built for self-custody", "A mandatory co-signer that protects wallets without giving up control."],
                ["Policy + intelligence", "Deterministic rules plus AI simulation catches both known and novel risk."],
                ["Operationally simple", "Tune limits in minutes instead of managing multisig internals."],
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
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#ff9b1f]/60 to-transparent" />
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">Live policy preview</p>
                  <p className="mt-1 text-sm lc-muted">Control that feels like product UX, not security infrastructure.</p>
                </div>
                <span className="rounded-full border border-[#ffb04a]/30 bg-[#ff9b1f]/10 px-3 py-1 text-xs font-semibold text-[#ffb04a]">
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
                  <SlidersHorizontal className="h-5 w-5 text-[#ffb04a]" />
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
                    <div className="h-full w-[58%] rounded-full bg-gradient-to-r from-[#ffb04a] to-[#ff9b1f]" />
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
                  <Icon className="h-5 w-5 text-[#ffb04a]" />
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
              src={withBase("/diagram.png")}
              alt="Flow: transaction proposed, hard rules may reject, AI review may alert via Telegram Signal or hardware, then agent co-signs and execution proceeds"
              className="mx-auto w-full max-w-3xl rounded-2xl border border-white/10 bg-[#061015]/40"
              width={720}
              height={420}
              loading="lazy"
            />
            <figcaption className="mt-4 text-center text-sm lc-muted">
              Self-hosted — your policies and history stay on your infrastructure.{" "}
              <a href={GITHUB_REPO} target="_blank" rel="noreferrer" className="text-[#ffb04a] underline-offset-4 hover:underline">
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
              title="Most wallets warn. LastCheck enforces."
              description="Phishing, malicious approvals, and spoofed frontends keep winning because warnings are generic and easy to ignore. LastCheck applies your own limits and requires a co-signer checkpoint for anything unusual."
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {PAIN_POINTS.map((item) => (
              <div key={item.title} className="lc-list-item">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                  <ChevronRight className="h-4 w-4 text-[#ffb04a]" />
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
              title="Wallet security that works like a product."
              description="Change limits for a high-risk day and roll them back later without touching Safe modules or editing configs."
            />
            <div className="mt-8 space-y-3">
              {BENEFITS.map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <ShieldCheck className="mt-0.5 h-4 w-4 text-[#ffb04a]" />
                  <p className="text-sm leading-7 text-white/88">{item}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="lc-panel p-7 sm:p-8">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                <Server className="h-5 w-5 text-[#ffb04a]" />
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
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#ffb04a]/30 bg-[#ff9b1f]/10 text-sm font-semibold text-[#ffb04a]">
                    {index + 1}
                  </div>
                  <p className="text-sm text-white/88">{step}</p>
                </div>
              ))}
            </div>
            <a href={setupUrl} className="mt-8 inline-flex items-center text-sm font-semibold text-[#ffb04a]">
              Start onboarding
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
                Put a co-signer firewall in front of your next signature.
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 lc-muted sm:text-lg">
                Connect a wallet, deploy the agent, and activate a two-layer signing flow that blocks
                unsafe transactions before funds move.
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
