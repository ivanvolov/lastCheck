import {
  ArrowRight,
  Bot,
  Github,
  LockKeyhole,
  MessageSquareWarning,
  Server,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import { SectionHeading } from "@/components/section-heading";
import { getSetupHashUrl, withBase } from "@/lib/routes";

const GITHUB_REPO = "https://github.com/ivanvolov/lastCheck";
const setupUrl = getSetupHashUrl("/setup/step1-deploy");

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
  "Most wallets only warn. LastCheck blocks unsafe paths before signing.",
  "Change limits quickly without editing Safe modules or policy code.",
  "Self-hosted by design: your policy logic and transaction context stay under your control.",
];

const PREVIEW_STEPS = [
  "Deploy the engine and pair the Telegram bot to receive the agent signer.",
  "Connect your wallet and create a 2-of-2 Safe with the agent as the second signer.",
  "Set the Safe in Telegram and verify that approval prompts reach you before execution.",
];

export default function Home() {
  return (
    <main className="lc-shell">
      <section className="lc-container relative pt-8 pb-16 sm:pt-10 sm:pb-24">
        <div className="grid gap-10 pt-14 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div className="space-y-8">
            <div className="space-y-5">
              <span className="lc-badge">
                <span className="h-2 w-2 rounded-full bg-[#ff9b1f]" />
                The final checkpoint before execution
              </span>
              <h1 className="max-w-4xl text-balance text-5xl font-semibold leading-[0.95] text-white sm:text-6xl lg:text-7xl">
                LastCheck is the checkpoint before you sign.
              </h1>
              <p className="max-w-2xl text-lg leading-8 lc-muted sm:text-xl">
                A self-hosted co-signer that blocks risky transactions and only interrupts you when
                a signature needs attention.
              </p>
              <p className="max-w-2xl text-lg leading-8 lc-muted sm:text-xl">
                Built for calm signing: most transactions pass silently, and LastCheck steps in only
                when a signature looks outside your policy.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <a href={setupUrl} className="lc-button-primary">
                Start app
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
              <a href={GITHUB_REPO} target="_blank" rel="noreferrer" className="lc-button-secondary">
                GitHub
              </a>
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

      <section id="how-it-works" className="lc-container pt-16 pb-8 sm:pt-24 sm:pb-10">
        <SectionHeading
          eyebrow="How it works"
          title="Three decisions before funds move."
          description="Enforce rules, run AI checks, escalate only when needed."
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

      <section className="lc-container pt-8 pb-8 sm:pt-10 sm:pb-12">
        <div className="lc-panel-strong overflow-hidden p-6 sm:p-8">
          <SectionHeading
            eyebrow="Transaction flow"
            title=""
            description=""
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
            </figcaption>
          </figure>
        </div>
      </section>

      <section className="lc-container pt-8 pb-16 sm:pt-12 sm:pb-24">
        <div className="space-y-6">
        <div className="lc-panel p-7 sm:p-8">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                <Server className="h-5 w-5 text-[#ffb04a]" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">Simple self-hosted rollout</p>
                <p className="mt-1 text-sm lc-muted">The setup wizard gets you from deploy to protected Safe in three steps.</p>
              </div>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              {PREVIEW_STEPS.map((step, index) => (
                <div key={step} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full border border-[#ffb04a]/30 bg-[#ff9b1f]/10 text-sm font-semibold text-[#ffb04a]">
                    {index + 1}
                  </div>
                  <p className="mt-3 text-sm text-white/88">{step}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="lc-panel-strong p-7 sm:p-8">
            <SectionHeading
              eyebrow="Benefits"
              title="Security controls that stay usable."
              description="LastCheck keeps policy control understandable and operationally light."
            />
            <div className="mt-8 grid gap-3 md:grid-cols-3">
              {BENEFITS.map((item) => (
                <div key={item} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <ShieldCheck className="h-4 w-4 text-[#ffb04a]" />
                  <p className="mt-3 text-sm leading-7 text-white/88">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="lc-container pb-20 sm:pb-28">
        <div className="lc-panel-strong overflow-hidden px-6 py-8 sm:px-10 sm:py-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="lc-eyebrow">Start with one wallet</p>
              <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
                Put a co-signer checkpoint before your next signature.
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 lc-muted sm:text-lg">
                Connect a wallet, deploy the agent, and activate a two-layer signing flow that blocks
                unsafe transactions before funds move.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              <a href={setupUrl} className="lc-button-primary">
                Start app
              </a>
              <a href={GITHUB_REPO} target="_blank" rel="noreferrer" className="lc-button-secondary">
                <span className="inline-flex items-center justify-center gap-2">
                  <Github className="h-4 w-4" />
                  GitHub
                </span>
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
