"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { clsx } from "clsx";

const STEPS = [
  { label: "Connect", href: "/setup/step1-connect", num: 1 },
  { label: "Choose tier", href: "/setup/step2-tier", num: 2 },
  { label: "Deploy", href: "/setup/step3-deploy", num: 3 },
  { label: "Safe setup", href: "/setup/step4-safe", num: 4 },
];

export default function SetupLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const currentStep = STEPS.findIndex((s) => pathname.startsWith(s.href)) + 1;

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12">
      {/* Logo */}
      <div className="mb-10 text-center">
        <h1 className="text-2xl font-bold tracking-tight text-white">LastCheck</h1>
        <p className="text-sm text-gray-500 mt-1">Self-hosted transaction co-signer</p>
      </div>

      {/* Step indicator */}
      <nav className="flex items-center gap-2 mb-10">
        {STEPS.map((step, i) => {
          const done = currentStep > step.num;
          const active = currentStep === step.num;
          return (
            <div key={step.href} className="flex items-center gap-2">
              <div
                className={clsx(
                  "flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium transition-all",
                  active && "bg-indigo-500 text-white",
                  done && "bg-indigo-900 text-indigo-300",
                  !active && !done && "text-gray-600"
                )}
              >
                <span
                  className={clsx(
                    "w-5 h-5 rounded-full flex items-center justify-center text-xs border",
                    active && "border-white bg-white text-indigo-600",
                    done && "border-indigo-400 bg-indigo-400 text-white",
                    !active && !done && "border-gray-700 text-gray-600"
                  )}
                >
                  {done ? "✓" : step.num}
                </span>
                {step.label}
              </div>
              {i < STEPS.length - 1 && (
                <div className={clsx("w-6 h-px", done ? "bg-indigo-700" : "bg-gray-800")} />
              )}
            </div>
          );
        })}
      </nav>

      {/* Step content */}
      <div className="w-full max-w-2xl">{children}</div>
    </div>
  );
}
