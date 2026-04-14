"use client";

import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const STEPS = [
  { label: "Deploy", href: "/setup/step1-deploy", num: 1 },
  { label: "Safe setup", href: "/setup/step2-safe", num: 2 },
  { label: "Telegram", href: "/setup/step3-telegram", num: 3 },
];

export default function SetupLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const currentStep = STEPS.findIndex((s) => pathname.startsWith(s.href)) + 1;

  return (
    <div className="lc-shell min-h-screen flex flex-col items-center px-4 py-12">
      <div className="mb-10 text-center">
        <h1 className="text-2xl font-bold tracking-tight text-white">LastCheck</h1>
        <p className="text-sm lc-muted mt-1">Self-hosted transaction co-signer</p>
      </div>

      <nav className="flex items-center gap-2 mb-10">
        {STEPS.map((step, i) => {
          const done = currentStep > step.num;
          const active = currentStep === step.num;
          return (
            <div key={step.href} className="flex items-center gap-2">
              <div
                className={clsx(
                  "flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium transition-all",
                  active && "bg-[#ff9b1f] text-black",
                  done && "bg-[#ff9b1f]/20 text-[#ffb04a]",
                  !active && !done && "text-gray-500"
                )}
              >
                <span
                  className={clsx(
                    "w-5 h-5 rounded-full flex items-center justify-center text-xs border",
                    active && "border-black/20 bg-black/10 text-black",
                    done && "border-[#ffb04a]/60 bg-[#ff9b1f]/20 text-[#ffb04a]",
                    !active && !done && "border-gray-700 text-gray-500"
                  )}
                >
                  {done ? "✓" : step.num}
                </span>
                {step.label}
              </div>
              {i < STEPS.length - 1 && (
                <div className={clsx("w-6 h-px", done ? "bg-[#ff9b1f]/50" : "bg-gray-800")} />
              )}
            </div>
          );
        })}
      </nav>

      <div className="w-full max-w-2xl">{children}</div>
    </div>
  );
}
