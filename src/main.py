from fastapi import FastAPI

from src.api import (
    routes_company,
    routes_config,
    routes_dashboard,
    routes_decisions,
    routes_escalations,
    routes_events,
)

app = FastAPI(title="ASCT")
app.include_router(routes_events.router)
app.include_router(routes_decisions.router)
app.include_router(routes_escalations.router)
app.include_router(routes_dashboard.router)
app.include_router(routes_company.router)
app.include_router(routes_config.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
