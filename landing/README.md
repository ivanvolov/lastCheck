# LastCheck — site + onboarding

Next.js site with both marketing pages and the onboarding wizard.

## Local dev

```bash
npm install
npm run dev
# http://localhost:3001
# onboarding starts at /#/setup/step1-deploy
```

## GitHub Pages (static export)

The repo includes [`.github/workflows/deploy-landing.yml`](../.github/workflows/deploy-landing.yml). It builds with `output: 'export'` and deploys the `landing/out` folder to **GitHub Pages**.

### One-time GitHub configuration

1. **Repository → Settings → Pages**
2. Under **Build and deployment → Source**, choose **GitHub Actions** (not “Deploy from a branch”).
3. **Repository → Settings → Environments** — ensure the `github-pages` environment exists (GitHub creates it on first successful deploy). No secrets are required for the default `actions/deploy-pages` flow.

### Optional: change `BASE_PATH`

The workflow sets:

```text
BASE_PATH=/${{ github.event.repository.name }}
```

So for `github.com/you/lastCheck`, the site is served at `https://you.github.io/lastCheck/`. This must match the [GitHub Pages URL for a project site](https://docs.github.com/en/pages/getting-started-with-github-pages/types-of-github-pages-sites).

Marketing stays at the repo root, for example:

```text
https://you.github.io/lastCheck/
```

Onboarding deep links use hash routes so GitHub Pages can load them reliably:

```text
https://you.github.io/lastCheck/#/setup/step1-deploy
https://you.github.io/lastCheck/#/setup/step2-safe
https://you.github.io/lastCheck/#/setup/step3-telegram
```

If your repository name is not the path you want, fork the workflow and set `BASE_PATH` to the correct path (e.g. `/my-project`).

### Manual build (same as CI)

```bash
cd landing
export BASE_PATH=/YOUR_REPO_NAME
npm ci
npm run build
# Static files in ./out — upload or serve this folder
```

### Triggers

The workflow runs on pushes to `main` that touch `landing/**` or the workflow file, and can be run manually (**Actions → Deploy landing to GitHub Pages → Run workflow**).
