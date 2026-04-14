"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

const SETUP_HASH_PREFIX = "#/setup/";

export function HashRouteBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (pathname !== "/") return;

    const { hash } = window.location;
    if (!hash.startsWith(SETUP_HASH_PREFIX)) return;

    const target = hash.slice(1);
    if (!target.startsWith("/setup/")) return;

    router.replace(target);
  }, [pathname, router]);

  return null;
}
