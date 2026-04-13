# AI Layer — In Development

This container will provide the second layer of transaction analysis:

- **Nano Claw** simulation engine — re-executes transactions in a fork to detect unexpected state changes
- **Custom skills** — protocol-specific heuristics (MEV, phishing, drainer patterns)
- Runs isolated from the rule engine; can only _recommend_, never override hard rules

Status: not yet implemented. Hidden from the wizard UI.
