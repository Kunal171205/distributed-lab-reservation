# Distributed Lab and Equipment Reservation System

This is a complete implementation of a fault-tolerant distributed system that coordinates shared resource reservations (laboratories, projectors, equipment) across multiple independent nodes.

This project demonstrates core distributed systems concepts including synchronous/asynchronous communication, logical event ordering, distributed mutual exclusion, and leader election.

## Architecture & Features

The system simulates a distributed college network where multiple servers handle reservation requests. It ensures that students cannot double-book a lab or piece of equipment by coordinating access using distributed algorithms.

- **Frontend:** React + Vite SPA with modern white UI (Separated Admin & Student Portals)
- **API Gateway:** FastAPI reverse proxy that acts as a load balancer, routing traffic randomly to available backend nodes (Running on Port 8000)
- **Node Services:** Three independent FastAPI backend instances (`node-a`, `node-b`, `node-c`) executing the actual logic on ports 8001, 8002, and 8003.
- **Database:** Shared local SQLite file representing distributed persistence layer.
- **Message Broker:** Integration-ready with RabbitMQ for AMQP messaging (gracefully degrades to local mock queues if RabbitMQ is unavailable).

For a deep dive into the system's architecture, including UML Class/Component and Sequence Diagrams, view the [`architecture_diagrams.md`](architecture_diagrams.md) file included in this repository.

## Distributed Algorithms Implemented
1. **Lamport Logical Clocks:** Ensures events are causally ordered across the distributed nodes.
2. **Lamport's Mutual Exclusion:** Coordinates concurrent reservation requests through `REQUEST`, `REPLY`, and `RELEASE` messages. Each request carries a Lamport logical timestamp; the request with the lower timestamp is ordered first, with node ID breaking ties. After entering the critical section, the node checks for an overlapping confirmed reservation before saving.
3. **Bully Leader Election:** Nodes have an ordered priority. If the coordinator crashes or starts up, the nodes automatically exchange priority packets and elect the highest-priority active node as the leader.

### Simultaneous reservation requests

If two students request the same resource and time slot concurrently, Lamport timestamps and node IDs determine the request order. The first request to complete the reservation check and save is confirmed; the later request sees the overlapping reservation and is rejected. A Lamport timestamp is a logical ordering counter, not a wall-clock time or a measure of elapsed seconds.

The current mutex implementation has a 10-second wait timeout and can enter the critical section with incomplete replies. If a node is unreachable, this fallback means distributed mutual exclusion is not guaranteed, so concurrent requests could still race; the database overlap check is an additional safeguard, not a replacement for reliable coordination.

---

## Running with Docker (Recommended for New PC / Clean Setup)

You only need **Docker Desktop** installed on your new PC (no Python or Node.js required on the host system).

### 1. Clone the Repository
```bash
git clone <YOUR_REPOSITORY_URL>
cd distributed-lab-reservation
```

### 2. Start all Services
Run Docker Compose in detached mode with build:
```bash
docker compose up -d --build
```
This builds and launches:
- `db` (PostgreSQL 15 on port 5432)
- `rabbitmq` (RabbitMQ broker on port 5672, management UI on 15672)
- `node-a`, `node-b`, `node-c` (FastAPI backend nodes on ports 8001, 8002, 8003)
- `gateway` (FastAPI API Gateway on port 8000)
- `frontend` (React + Vite SPA on port 3000)

### 3. Seed Database
Once all containers are running (wait ~10-15 seconds for PostgreSQL and nodes to be ready), run:
```bash
docker compose exec node-a python seed_data.py
```

### 4. Access the Application
Open your browser and visit:
👉 **http://localhost:3000**

---

## Running Locally (Without Docker)

To run this project locally on Windows WITHOUT Docker, ensure you have:
* **Python 3.10+**
* **Node.js & npm**

### 1. Install Dependencies
Open your terminal and navigate to the project root:
```bash
# Install backend requirements
pip install -r node_service/requirements.txt
pip install -r gateway/requirements.txt

# Install frontend requirements
cd frontend
npm install
cd ..
```

### 2. Seed the Database
Generate the dummy data, test resources, and user accounts:
```bash
python seed_data.py
# Note: Ensure the generated `reservations.db` is located inside `node_service/app/`.
```

### 3. Start the Cluster
Run the orchestration script to launch all 3 Nodes, the API Gateway, and the React frontend simultaneously:
```bash
python start_local.py
```

### 4. Access the Application
Once the terminal reads *All services started!*, open your web browser and navigate to:
👉 **http://localhost:3000**

---

## Demo Accounts

You can log in and test the application using the following seeded credentials.

**Admin Portal:**
* Email: `admin@labreserve.test`
* Password: `Demo@12345`

**Student Portal (Mock Users):**
* Email: `aarav.sharma@labreserve.test`
* Email: `priya.patil@labreserve.test`
* Email: `rohan.deshmukh@labreserve.test`
* Password for all students: `Demo@12345`

---

## Stopping the Application
To shut down the cluster and clean up the running processes, simply press `Ctrl + C` in the terminal where `start_local.py` is running.
