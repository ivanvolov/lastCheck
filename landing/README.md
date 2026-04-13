# LastCheck — marketing site

Static Next.js site (product story, flow diagram). The onboarding wizard lives in `../app/`.

## Local dev

```bash
npm install
npm run dev
# http://localhost:3001
```

Links like **Start setup** use `NEXT_PUBLIC_APP_ORIGIN` (default `http://localhost:3000`) so the landing app can run beside the wizard.

Copy `/.env.example` to `.env.local` and adjust if needed.

## GitHub Pages (static export)

The repo includes [`.github/workflows/deploy-landing.yml`](../.github/workflows/deploy-landing.yml). It builds with `output: 'export'` and deploys the `landing/out` folder to **GitHub Pages**.

### One-time GitHub configuration

1. **Repository → Settings → Pages**
2. Under **Build and deployment → Source**, choose **GitHub Actions** (not “Deploy from a branch”).
3. **Repository → Settings → Environments** — ensure the `github-pages` environment exists (GitHub creates it on first successful deploy). No secrets are required for the default `actions/deploy-pages` flow.

### Required: `NEXT_PUBLIC_APP_ORIGIN` (Actions variable)

**Settings → Secrets and variables → Actions → Variables → New repository variable**

| Name | Example | Purpose |
|------|---------|--------|
| `NEXT_PUBLIC_APP_ORIGIN` | `https://app.yourdomain.com` | Base URL of the **onboarding app** (`app/`). Baked into “Start setup” / “Protect a wallet” at **build time**. |

Use the real URL where users run the wizard (Vercel, Fly, your VPS, etc.). If you omit it, those links fall back to `http://localhost:3000` in the built HTML — wrong for production.

### Optional: change `BASE_PATH`

The workflow sets:

```text
BASE_PATH=/${{ github.event.repository.name }}
```

So for `github.com/you/lastCheck`, the site is served at `https://you.github.io/lastCheck/`. This must match the [GitHub Pages URL for a project site](https://docs.github.com/en/pages/getting-started-with-github-pages/types-of-github-pages-sites).

If your repository name is not the path you want, fork the workflow and set `BASE_PATH` to the correct path (e.g. `/my-project`).

### Manual build (same as CI)

```bash
cd landing
export BASE_PATH=/YOUR_REPO_NAME
export NEXT_PUBLIC_APP_ORIGIN=https://your-app-host.example
npm ci
npm run build
# Static files in ./out — upload or serve this folder
```

### Triggers

The workflow runs on pushes to `main` that touch `landing/**` or the workflow file, and can be run manually (**Actions → Deploy landing to GitHub Pages → Run workflow**).
