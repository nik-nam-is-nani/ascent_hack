# Workforce Continuity Agent

A multi-agent autonomous system that monitors employee absence and automatically handles all their pending tasks by reassigning to available employees or autonomously completing work using AI agents.

## Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: React 18 with Vite, Tailwind CSS
- **Database**: In-memory (SQLite for demo)
- **AI**: OpenRouter API (Claude Sonnet 4)
- **Real-time**: WebSockets for live agent activity feed

## Features

- **Real-time Agent Pipeline**: Watch the AI agents work through the absence handling pipeline live via WebSocket
- **Skill-based Task Reallocation**: Automatically matches tasks to available employees based on skill proficiency
- **Autonomous Task Completion**: AI agents autonomously complete tasks that can't be reallocated
- **GitHub Integration**: Clone repositories and create branches/PRs for completed work
- **Workspace Explorer**: Visual file browser for the AI-generated workspace
- **Manager Reports**: Comprehensive reports of all reallocation and completion decisions

## Quickstart

### 1. Configure Environment

```bash
cd workforce-continuity-agent/backend

# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenRouter API key for AI features
# OPENROUTER_API_KEY=your_key_here

# Optional: Add GitHub token for real repository sync
# GITHUB_TOKEN=your_github_token
# GITHUB_REPO_URL=https://github.com/username/repo
```

### 2. Start the Backend

```bash
pip install -r requirements.txt
python main.py
```

The backend will run at `http://localhost:8000`

### 3. Start the Frontend

```bash
cd workforce-continuity-agent/frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. You'll see the Employee Dashboard with 10 employees
3. (Optional) Add GitHub PAT + repository URL in the header for real sync/push
4. Click any employee card to view all their currently allocated tasks
5. Click **"Mark Absent"** on that employee card
6. Watch the agent pipeline run in real-time via WebSocket:

   - **Phase 1**: Detect absence and identify affected tasks
   - **Phase 2**: Clone/sync repository (if configured)
   - **Phase 3**: Analyze task requirements using AI
   - **Phase 4**: Find best skill matches & reassign tasks
   - **Phase 5**: Auto-complete remaining tasks with AI
   - **Phase 6**: Generate comprehensive manager report

7. Open the **Neural Workspace** tab to see synced repository, terminal activity, and generated files
8. View the final **Manager Report** showing all reallocation decisions

## Project Structure

```
workforce-continuity-agent/
├── backend/
│   ├── main.py                    # FastAPI app, API endpoints, WebSocket
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment configuration template
│   │
│   ├── agents/                    # Multi-agent AI system
│   │   ├── orchestrator.py        # Main coordination agent
│   │   ├── task_analyzer.py       # Analyzes task requirements
│   │   ├── availability_agent.py   # Skill matching & availability
│   │   ├── reallocation_agent.py  # Task assignment decisions
│   │   ├── executor_agent.py      # Autonomous task completion
│   │   ├── llm_client.py          # OpenRouter API client
│   │   └── activity.py            # Real-time activity tracking
│   │
│   ├── tools/                     # Business logic & integrations
│   │   ├── employee_db.py         # Employee data management
│   │   ├── task_manager.py        # Task CRUD operations
│   │   ├── calendar_tool.py       # Availability checking
│   │   ├── notification_tool.py    # Mock Slack/email notifications
│   │   ├── github_tool.py         # GitHub API integration
│   │   └── workspace_tool.py      # File system & workspace management
│   │
│   ├── models/                    # Data models
│   │   ├── employee.py             # Employee model with skills
│   │   └── task.py                # Task model with status/priority
│   │
│   └── database/                  # Data initialization
│       ├── seed.py                # Basic seed data
│       └── simulation_seeder.py   # E-commerce project simulation
│
└── frontend/
    ├── package.json               # Node dependencies
    ├── vite.config.js             # Vite configuration
    ├── tailwind.config.js         # Tailwind CSS config
    ├── index.html                 # Entry HTML
    └── src/
        ├── main.jsx               # React entry point
        ├── App.jsx                # Main application component
        └── components/
            ├── EmployeeDashboard.jsx   # Main dashboard view
            ├── EmployeeCard.jsx         # Employee detail card
            ├── AgentActivityFeed.jsx    # Real-time activity stream
            ├── AgentVisualizer.jsx      # Agent pipeline visualization
            ├── TaskManifest.jsx        # Task list component
            ├── ManagerReport.jsx       # Decision report viewer
            └── WorkspaceExplorer.jsx   # File browser for workspace
```

## Demo Data

**10 Employees** with diverse roles and skill sets:

| ID | Name | Role | Department | Workload |
|----|------|------|------------|----------|
| EMP-001 | Riya Sharma | Backend Developer | Engineering | High |
| EMP-002 | Arjun Mehta | Senior Backend Developer | Engineering | Medium |
| EMP-003 | Priya Nair | Frontend Developer | Engineering | Low |
| EMP-004 | Karan Singh | Data Analyst | Analytics | Medium |
| EMP-005 | Meera Iyer | Product Manager | Product | High |
| EMP-006 | Rohan Das | DevOps Engineer | Engineering | Medium |
| EMP-007 | Anika Patel | UX Designer | Design | Low |
| EMP-008 | Vikram Rao | Engineering Manager | Engineering | Medium |
| EMP-009 | Sneha Kapoor | Marketing Analyst | Marketing | Medium |
| EMP-010 | Dev Sharma | Full Stack Developer | Engineering | High |

**20 Tasks** across various types (code, documentation, research, presentation) and priorities (critical, high, medium, low).

## API Endpoints

### Core Endpoints
- `GET /api/employees` - List all employees
- `GET /api/employees/{employee_id}` - Get employee details
- `GET /api/employees/{employee_id}/tasks` - Get tasks for employee
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{task_id}` - Get task details

### Absence Management
- `POST /api/absence/{employee_id}` - Mark absent & trigger pipeline
- `POST /api/absence/{employee_id}/reset` - Reset absence status

### Real-time Features
- `GET /api/activity` - Get agent activity feed
- `POST /api/activity/clear` - Clear activity feed
- `GET /ws/activity` - WebSocket for real-time updates

### Reports & Dashboard
- `GET /api/report/{employee_id}` - Get manager report
- `GET /api/dashboard/stats` - Get dashboard statistics

### Simulation & Workspace
- `POST /api/simulation/start` - Start full project simulation
- `POST /api/workspace/clone` - Clone repository to workspace
- `GET /api/workspace/files` - List workspace files
- `GET /api/workspace/status` - Get git repository status
- `GET /api/workspace/file/{file_path}` - Get file content

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

## Configuration

### Environment Variables (backend/.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for Claude Sonnet via OpenRouter | Yes (for AI features) |
| `GITHUB_TOKEN` | GitHub Personal Access Token | No |
| `GITHUB_REPO_URL` | Repository URL to clone | No |

### GitHub Token Permissions

If using real GitHub sync, your token needs:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Actions workflows)

## Development

### Running Tests
```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build
```

## License

MIT License