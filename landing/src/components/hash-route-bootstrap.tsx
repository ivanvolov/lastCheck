"use client";

import { useEffect } from "react";

const SETUP_HASH_PREFIX = "#/setup/";

function getSetupRedirectUrl() {
  if (typeof window === "undefined") return null;

  const { hash, pathname } = window.location;
  if (!hash.startsWith(SETUP_HASH_PREFIX)) return null;

  const target = hash.slice(1).replace(/\/+$/, "");
  if (!target.startsWith("/setup/")) return null;

  const normalizedPath = pathname.replace(/\/+$/, "");
  if (normalizedPath.includes("/setup/")) return null;

  return `${normalizedPath}${target}/`;
}

export function HashRouteBootstrap() {
  useEffect(() => {
    const redirectToSetupRoute = () => {
      const redirectUrl = getSetupRedirectUrl();
      if (!redirectUrl) return;

      window.location.replace(redirectUrl);
    };

    redirectToSetupRoute();
    window.addEventListener("hashchange", redirectToSetupRoute);

    return () => window.removeEventListener("hashchange", redirectToSetupRoute);
  }, []);

  return null;
}
