# GraphGuard AI - Finale Presentation Draft

Use this outline to build the final slide deck.

## Slide 1: Title
**Title:** GraphGuard AI  
**Subtitle:** TigerGraph-powered fraud ring detection for linked identities and money movement

**On slide:**
- Team name
- TigerGraph logo
- One-line promise: "Find fraud rings, not just risky rows."

## Slide 2: The Problem
**Title:** Modern fraud is a network problem

**Talk track:**
- Fraud is coordinated across users, phones, devices, accounts, and transfers.
- Row-by-row rule engines miss the hidden relationships between those entities.
- By the time analysts manually connect the dots, the money is gone.

## Slide 3: Why TigerGraph
**Title:** Why TigerGraph instead of a normal database

**On slide:**
- Multi-hop link analysis in milliseconds
- Pattern detection inside the database with GSQL
- Graph-driven risk scoring based on connected entities

**Visual suggestion:**
- Left side: a messy SQL join tree
- Right side: a clean TigerGraph traversal or GSQL pattern query

## Slide 4: Architecture
**Title:** TigerGraph is the core intelligence layer

**On slide:**
- TigerGraph Community Edition in Docker
- FastAPI backend using `pyTigerGraph`
- React dashboard with Cytoscape network visualization
- Core graph model: `User`, `Phone`, `Device`, `BankAccount`, `SENT_TO`

## Slide 5: Demo Storyboard
**Title:** The 3-minute demo flow

**On slide:**
1. Click `Load Sample Data`
2. Show top stats cards
3. Search `+1-555-0101`
4. Explain the risk score and grouped reasons
5. Pivot to the graph and show the connected fraud ring
6. Close with money loops, shared devices, and phone reuse counts

## Slide 6: Explainability
**Title:** Every alert is explainable

**On slide:**
- Shared device footprint
- Phone reused across multiple accounts
- Circular transfer loop detection
- Exposure to flagged users

**Demo focus:**
- Show the risk meter legend
- Show grouped explanation cards with severity labels

## Slide 7: What TigerGraph Queries Are Running
**Title:** Native GSQL queries behind the dashboard

**On slide:**
- `check_user_risk`
- `find_connections`
- `detect_money_loops`
- `detect_shared_devices`
- `detect_phone_reuse`

**Key message:**
- The frontend is only visualizing signals computed in TigerGraph.

## Slide 8: Who Uses This Tomorrow
**Title:** Immediate users

**On slide:**
- Bank fraud analyst
- Fintech risk team
- Payment gateway compliance team

**Talk track:**
- This is not just a hackathon visualization.
- It is the start of an operational fraud-investigation workflow.

## Slide 9: If We Had 3 More Days
**Title:** Product roadmap

**On slide:**
- Real-time streaming ingest for new transactions
- ML model layered on top of TigerGraph features
- Case management for analysts to resolve alerts

## Slide 10: Closing
**Title:** GraphGuard AI

**Closing line:**
"TigerGraph lets us detect fraud rings in real time, explain exactly why they are risky, and show the whole network visually in one workflow."
