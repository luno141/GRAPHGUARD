<p align="center">
  <img src="https://raw.githubusercontent.com/tigergraph/ecosystem/master/tigergraph_logo.png" alt="TigerGraph" width="150" />
</p>

# GraphGuard AI
Stop organized fraud rings with TigerGraph-powered link analysis, pattern detection, and explainable risk scoring.

## Quickstart for Judges
This project is easiest to evaluate in four steps:

1. Start TigerGraph locally:
```bash
docker run -d -p 9000:9000 -p 14240:14240 -p 14141:14141 --name tigergraph --ulimit nofile=1000000:1000000 tigergraph/tigergraph:latest
```

2. Install the schema and GSQL queries:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup_tigergraph_v2.py
```

3. Run the backend:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Run the frontend:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Expected startup times:
- TigerGraph boot: about 2 to 3 minutes
- Schema + query install: about 2 minutes
- UI refresh after clicking `Load Sample Data`: usually under 10 seconds

Tip for judges:
- Once the UI is open, click `Load Sample Data` to populate the full fraud-ring demo scenario used by the dashboard.

## What TigerGraph Is Doing That a Normal DB Does Not
- Multi-hop fraud ring detection: 3-hop and 4-hop relationships are traversed directly in TigerGraph instead of being rebuilt with deep SQL join trees.
- In-database pattern detection: `detect_money_loops`, `detect_shared_devices`, and `detect_phone_reuse` run as native GSQL queries inside TigerGraph.
- Real-time graph signals for scoring: risk is driven by connected entities, graph exposure, and suspicious transfer structure, not row-by-row rules alone.

## Demo Flow
Use this sequence for a clean 3-minute walkthrough:

1. Click `Load Sample Data` in the UI so the graph is populated live.
2. Point to the top stats cards showing users, phones, devices, accounts, transactions, and alerts.
3. Search for `+1-555-0101` and show the highest-risk linked user.
4. Walk through the risk meter and grouped explanation panel to explain why the alert fired.
5. Switch attention to the graph view and show the highlighted neighborhood around that suspicious identity.
6. Close with the TigerGraph pattern-query cards and the detected fraud pattern list.

## Why This Is a Graph Problem
Modern payment fraud is rarely isolated. It is coordinated across:
- shared phones
- shared devices
- mule accounts
- circular money transfers
- lightly connected "clean" accounts that hide the ring

Traditional relational systems struggle to answer questions like:
- Which users are 3 hops away from a flagged identity?
- Which devices are reused across multiple suspicious accounts?
- Which transfers form circular loops?

GraphGuard AI models those relationships natively so analysts can move from one suspicious identity to the surrounding fraud ring in seconds.

## Architecture
- Database: TigerGraph Community Edition running locally in Docker
- Backend API: FastAPI plus `pyTigerGraph`
- Frontend: React + Vite + Cytoscape
- Core entities: `User`, `Phone`, `Device`, `BankAccount`
- Core relationship: `SENT_TO` captures money movement between users

## Graph Schema
- Vertices: `User`, `Phone`, `BankAccount`, `Device`
- Edges:
  - `HAS_PHONE`
  - `USES_DEVICE`
  - `OWNS_ACCOUNT`
  - `SENT_TO`

## Main GSQL Queries
- `check_user_risk`
  - Computes graph-derived risk features around a user, including shared devices, shared phones, outgoing transfer fan-out, and flagged neighbors.
- `find_connections`
  - Traverses from a suspicious phone into the linked users, then out to related devices and bank accounts.
- `detect_money_loops`
  - Finds circular transfer patterns such as User A -> User B -> User C -> User A.
- `detect_shared_devices`
  - Flags device hubs reused by more than one user.
- `detect_phone_reuse`
  - Flags phone numbers linked to multiple accounts.
- `get_graph_data`
  - Returns the graph payload rendered by the Cytoscape dashboard.

## TigerGraph vs. SQL Slide Idea
For the finale deck, show one fraud question in two forms:

- SQL version: a large join-heavy query across users, phones, devices, and transfers
- TigerGraph version: one graph traversal or pattern query

That makes the value of the graph database obvious in under 10 seconds.

## Who Would Use This Tomorrow
- Bank fraud analysts investigating suspicious money movement
- Fintech risk teams screening linked identities in real time
- Payment gateway compliance teams reviewing mule-account behavior

## If We Had 3 More Days
- Stream TigerGraph features into a real-time event pipeline
- Add a lightweight supervised model on top of graph features
- Build case management for analyst review, resolution, and false-positive tracking

## Project Files Worth Opening
- `backend/tigergraph_client.py`
- `backend/main.py`
- `backend/risk_scorer.py`
- `queries_only.gsql`
- `frontend/src/App.jsx`
- `frontend/src/components/GraphView.jsx`

## License
MIT
