.PHONY: help app landing engine engine-local engine-down engine-logs setup-engine

help:
	@echo ""
	@echo "  make app            Install deps and start the onboarding wizard (localhost:3000)"
	@echo "  make landing        Install deps and start the marketing site (localhost:3001)"
	@echo "  make engine         Start the engine (dashboard :8501, bot, MCP server)"
	@echo "  make engine-local   Run engine locally without Docker (pip install + processes)"
	@echo "  make engine-down    Stop the engine containers"
	@echo "  make engine-logs    Tail engine logs"
	@echo "  make setup-engine   Copy .env.example → .env (edit before running make engine)"
	@echo ""

app:
	cd app && npm install && npm run dev

landing:
	cd landing && npm install && npm run dev

setup-engine:
	@if [ ! -f engine/.env ]; then \
		cp engine/.env.example engine/.env; \
		echo "Created engine/.env — fill in your tokens before running 'make engine'"; \
	else \
		echo "engine/.env already exists"; \
	fi

engine: setup-engine
	cd engine && docker compose up --build

engine-local: setup-engine
	cd engine && pip install -q -r requirements.txt && \
	set -a && . .env && set +a && \
	( streamlit run dashboard/app.py --server.port 8501 --server.address 127.0.0.1 & python bot/telegram_bot.py )

engine-down:
	cd engine && docker compose down

engine-logs:
	cd engine && docker compose logs -f
