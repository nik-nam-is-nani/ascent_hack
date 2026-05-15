# Workforce Continuity Agent

A multi-agent autonomous system that monitors employee absence and automatically handles all their pending tasks by reassigning to available employees or autonomously completing work using AI agents.

## Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: React with Tailwind CSS
- **Database**: In-memory (for demo)
- **AI**: OpenRouter API (Claude Sonnet)
- **Real-time**: WebSockets for live agent activity feed

## Quickstart

### 1. Start the Backend

```bash
cd workforce-continuity-agent/backend
pip install -r requirements.txt
python main.py
```

The backend will run at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd workforce-continuity-agent/frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. You'll see the Employee Dashboard with 10 employees
3. Click **"Mark Absent"** on any employee card
4. Watch the agent pipeline run in real-time via WebSocket:
   - Phase 1: Detect absence
   - Phase 2: Retrieve pending tasks
   - Phase 3: Analyze tasks
   - Phase 4: Find best skill matches & reassign
   - Phase 5: Auto-complete remaining tasks with AI
   - Phase 6: Generate manager report
5. View the final **Manager Report** showing all decisions

## Project Structure

```
workforce-continuity-agent/
├── backend/
│   ├── main.py              # FastAPI app, API endpoints, WebSocket
│   ├── agents/
│   │   ├── orchestrator.py  # Main coordination agent
│   │   ├── task_analyzer.py # Analyzes task requirements
│   │   ├── availability_agent.py # Skill matching
│   │   ├── reallocation_agent.py # Task assignment decisions
│   │   ├── executor_agent.py # Autonomous task completion
│   │   └── llm_client.py    # OpenRouter API client
│   ├── tools/
│   │   ├── employee_db.py   # Employee data management
│   │   ├── task_manager.py # Task CRUD
│   │   ├── calendar_tool.py # Availability checking
│   │   ├── notification_tool.py # Mock Slack/email
│   │   └── github_tool.py   # Mock PR creation
│   ├── models/
│   │   ├── employee.py      # Employee models
│   │   └── task.py         # Task models
│   └── database/
│       └── seed.py         # Demo data (10 employees, 20 tasks)
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       ├── EmployeeDashboard.jsx
    │       ├── EmployeeCard.jsx
    │       ├── AgentActivityFeed.jsx
    │       ├── TaskManifest.jsx
    │       └── ManagerReport.jsx
    └── package.json
```

## Demo Data

**10 Employees**:
- Riya Sharma — Backend Developer
- Arjun Mehta — Senior Backend Developer
- Priya Nair — Frontend Developer
- Karan Singh — Data Analyst
- Meera Iyer — Product Manager
- Rohan Das — DevOps Engineer
- Anika Patel — UX Designer
- Vikram Rao — Engineering Manager
- Sneha Kapoor — Marketing Analyst
- Dev Sharma — Full Stack Developer

**20 Tasks** across various types and priorities.

## API Endpoints

- `GET /api/employees` - List all employees
- `GET /api/tasks` - List all tasks
- `POST /api/absence/{employee_id}` - Mark absent & trigger pipeline
- `POST /api/absence/{employee_id}/reset` - Reset absence
- `GET /api/activity` - Get agent activity feed
- `GET /ws/activity` - WebSocket for real-time updates
- `GET /api/report/{employee_id}` - Get manager report