import streamlit as st

from src.database import SessionLocal
from src.models import CEODecision, EscalationRecord, EscalationStatus, Event, Inventory


def inventory_status(quantity: float) -> str:
    if quantity < 100:
        return "CRITICAL"
    if quantity > 1000:
        return "EXCESS"
    return "OK"


def main() -> None:
    st.set_page_config(page_title="ASCT Dashboard", layout="wide")
    st.title("ASCT Dashboard")
    with SessionLocal() as session:
        render_inventory(session)
        render_events(session)
        render_decisions(session)
        render_escalations(session)


def render_inventory(session) -> None:
    st.subheader("Inventory Health")
    rows = session.query(Inventory).limit(30).all()
    st.dataframe(
        [
            {
                "product": row.product.category,
                "location": row.location.name,
                "quantity": row.quantity,
                "status": inventory_status(row.quantity),
            }
            for row in rows
        ],
        use_container_width=True,
    )


def render_events(session) -> None:
    st.subheader("Active Events")
    rows = session.query(Event).order_by(Event.id.desc()).limit(10).all()
    st.dataframe(
        [{"type": row.event_type.value, "priority": row.priority.value} for row in rows],
        use_container_width=True,
    )


def render_decisions(session) -> None:
    st.subheader("Decision Explorer")
    for row in session.query(CEODecision).order_by(CEODecision.id.desc()).limit(10):
        with st.expander(f"Decision #{row.id}: {row.selected_action.get('type')}"):
            st.json({"score": row.score, "causal_chain": row.causal_chain})


def render_escalations(session) -> None:
    st.subheader("Pending Escalations")
    rows = session.query(EscalationRecord).filter_by(status=EscalationStatus.PENDING).all()
    for row in rows:
        st.warning(f"{row.trigger_type.value} for event #{row.event_id}")


if __name__ == "__main__":
    main()
