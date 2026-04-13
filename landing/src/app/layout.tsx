import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LastCheck",
  description:
    "Self-hosted AI co-signer for your transactions — hard rules plus AI review. Your last line of defense before a malicious tx executes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
