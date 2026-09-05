# Agent / merge workflow

For this repo I will, by default:

1. Work on a `cursor/...` feature branch
2. Push commits
3. Open a PR into `main`
4. Wait until **CI** (`.github/workflows/ci.yml`) is green
5. **Squash-merge** the PR and delete the branch

Do not merge with red checks. Secrets stay in local `.env` only.

CI runs offline smoke tests (`pytest`) plus an import guard — no broker credentials needed.
