"""
GraphGuard AI — FastAPI Backend

Main application with all API endpoints for fraud detection,
graph visualization, and risk scoring.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models import (
    CheckNumberRequest, CheckUserRequest, RiskResult, RiskSignals,
    GraphData, GraphNode, GraphEdge, HealthResponse
)
from tigergraph_client import TigerGraphClient
from risk_scorer import calculate_risk_score
from data_loader import load_sample_data


# Global TigerGraph client
tg_client: TigerGraphClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize TigerGraph connection on startup."""
    global tg_client
    print("[GraphGuard] Starting up...")
    tg_client = TigerGraphClient()
    yield
    print("[GraphGuard] Shutting down...")


app = FastAPI(
    title="GraphGuard AI",
    description="Fraud Intelligence System powered by TigerGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    connected = tg_client.is_connected() if tg_client else False
    return HealthResponse(
        status="healthy" if connected else "degraded",
        tigergraph_connected=connected,
        graph_name="FraudGraph",
    )


@app.post("/check-number")
async def check_number(request: CheckNumberRequest):
    """
    Check a phone number for fraud risk.
    
    Finds all users connected to the phone number,
    then evaluates risk for each user.
    """
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")

    # Find all connections from this phone number
    connections = tg_client.find_connections(request.phone_number)

    if not connections["connected_users"]:
        return {
            "phone_number": request.phone_number,
            "status": "not_found",
            "message": "No users found linked to this phone number",
            "results": [],
        }

    # Evaluate risk for each connected user
    results = []
    for user_id in connections["connected_users"]:
        signals_raw = tg_client.check_user_risk(user_id)

        # Check if user is in money loop
        loops = tg_client.detect_money_loops()
        in_loop = False
        for loop in loops:
            if user_id in [loop.get("user_a"), loop.get("user_b"), loop.get("user_c")]:
                in_loop = True
                break

        signals = RiskSignals(
            shared_device_count=signals_raw.get("shared_device_count", 0),
            shared_phone_count=signals_raw.get("shared_phone_count", 0),
            sent_to_count=signals_raw.get("sent_to_count", 0),
            received_from_count=signals_raw.get("received_from_count", 0),
            total_sent=signals_raw.get("total_sent", 0.0),
            total_received=signals_raw.get("total_received", 0.0),
            connected_flagged_users=signals_raw.get("connected_flagged_users", []),
            is_in_money_loop=in_loop,
            is_flagged=signals_raw.get("is_flagged", False),
        )

        score, level, explanations = calculate_risk_score(signals)

        results.append(RiskResult(
            user_id=user_id,
            user_name=signals_raw.get("user_name", "Unknown"),
            risk_score=score,
            risk_level=level,
            signals=signals,
            explanation=explanations,
            connected_users=connections["connected_users"],
            connected_phones=connections["connected_phones"],
            connected_devices=connections["connected_devices"],
            connected_accounts=connections["connected_accounts"],
        ))

    # Sort by risk score descending
    results.sort(key=lambda r: r.risk_score, reverse=True)

    return {
        "phone_number": request.phone_number,
        "status": "found",
        "total_users": len(results),
        "highest_risk": results[0].risk_level if results else "UNKNOWN",
        "results": [r.model_dump() for r in results],
    }


@app.post("/check-user")
async def check_user(request: CheckUserRequest):
    """Check a specific user for fraud risk."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")

    signals_raw = tg_client.check_user_risk(request.user_id)

    if not signals_raw.get("user_name"):
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

    # Check money loops
    loops = tg_client.detect_money_loops()
    in_loop = any(
        request.user_id in [l.get("user_a"), l.get("user_b"), l.get("user_c")]
        for l in loops
    )

    signals = RiskSignals(
        shared_device_count=signals_raw.get("shared_device_count", 0),
        shared_phone_count=signals_raw.get("shared_phone_count", 0),
        sent_to_count=signals_raw.get("sent_to_count", 0),
        received_from_count=signals_raw.get("received_from_count", 0),
        total_sent=signals_raw.get("total_sent", 0.0),
        total_received=signals_raw.get("total_received", 0.0),
        connected_flagged_users=signals_raw.get("connected_flagged_users", []),
        is_in_money_loop=in_loop,
        is_flagged=signals_raw.get("is_flagged", False),
    )

    score, level, explanations = calculate_risk_score(signals)

    result = RiskResult(
        user_id=request.user_id,
        user_name=signals_raw.get("user_name", "Unknown"),
        risk_score=score,
        risk_level=level,
        signals=signals,
        explanation=explanations,
    )

    return result.model_dump()


@app.get("/graph-data")
async def get_graph_data():
    """Get full graph data for visualization."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")

    data = tg_client.get_graph_data()
    return data


@app.get("/fraud-clusters")
async def get_fraud_clusters():
    """Get detected fraud patterns and clusters."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")

    shared_devices = tg_client.detect_shared_devices()
    money_loops = tg_client.detect_money_loops()
    phone_reuse = tg_client.detect_phone_reuse()

    return {
        "shared_devices": shared_devices,
        "money_loops": money_loops,
        "phone_reuse": phone_reuse,
        "total_alerts": len(shared_devices) + len(money_loops) + len(phone_reuse),
    }


@app.get("/users")
async def get_users():
    """Get all users for the search dropdown."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")
    return tg_client.get_all_users()


@app.get("/phones")
async def get_phones():
    """Get all phone numbers for the search dropdown."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")
    return tg_client.get_all_phones()


@app.post("/load-data")
async def load_data():
    """Load or reset sample data into TigerGraph."""
    try:
        success = load_sample_data()
        if success:
            # Reconnect client to pick up new data
            global tg_client
            tg_client = TigerGraphClient()
            return {"status": "success", "message": "Sample data loaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to load data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get graph statistics."""
    if not tg_client or not tg_client.is_connected():
        raise HTTPException(status_code=503, detail="TigerGraph not connected")

    return {
        "users": tg_client.get_vertex_count("User"),
        "phones": tg_client.get_vertex_count("Phone"),
        "devices": tg_client.get_vertex_count("Device"),
        "accounts": tg_client.get_vertex_count("BankAccount"),
        "transactions": tg_client.get_vertex_count("Transaction"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
