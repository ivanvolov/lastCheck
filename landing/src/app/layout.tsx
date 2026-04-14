import "./globals.css";
import type { Metadata } from "next";
import { Providers } from "@/components/providers";

const basePath = process.env.BASE_PATH || "";
const tabIcon = `${basePath}/iconLC.png`;

export const metadata: Metadata = {
  title: "LastCheck",
  description:
    "Self-hosted AI co-signer for your transactions — hard rules plus AI review. Your last line of defense before a malicious tx executes.",
  icons: {
    icon: [{ url: tabIcon, type: "image/png" }],
    apple: tabIcon,
    shortcut: tabIcon,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
