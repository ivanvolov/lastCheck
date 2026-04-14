/** Prefix for static assets and root links under GitHub Pages project sites. */
export function withBase(path: string): string {
  const base = process.env.BASE_PATH || "";
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`;
}

export function getSetupHashUrl(path: `/setup/${string}`): string {
  return `${withBase("/")}#${path}`;
}
