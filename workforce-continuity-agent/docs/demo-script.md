# Demo Video Script (5 minutes)

## Opening (0:00 - 0:30)
**[Show the dashboard with all employees at work]**

"Hi, I'm going to demo the Workforce Continuity Agent — an AI system that automatically handles task reassignment when an employee is absent. Let's see it in action."

## Trigger Absence (0:30 - 1:00)
**[Click "Trigger Absence" on employee P5]**

"I'm marking P5 — a Frontend Developer — as absent. Watch the agent visualizer. The 6-phase pipeline kicks off immediately."

**[Show the progress bar moving through phases]**

"Phase 1: Detection. The system knows P5 is out. Phase 2: It's pulling all of P5's pending tasks and syncing the GitHub repository."

## Watch the Agent Think (1:00 - 2:00)
**[Show the activity feed and Neural Brain visualization]**

"Phase 3: Deep analysis. The agent is evaluating each task — extracting required skills, estimating complexity, deciding what can be handled by AI vs. reassigned to teammates."

**[Show the live execution panel]**

"Phase 4: Reallocation. Look at the activity feed — the agent is scoring team members against each task. P1 has 90% React skill match for the cart task, so it's being reassigned there. But the API integration task? No frontend dev has backend skills, so the agent will handle it autonomously."

## Autonomous Execution (2:00 - 3:30)
**[Show the workspace explorer and code being generated]**

"Phase 5: Execution. The agent is now actually doing the work. It searched the web for best practices, generated the code, and you can see it writing files to the workspace."

**[Switch to the workspace tab, show the file explorer]**

"Here's the workspace — the agent created real files. And if we check GitHub..."

**[Show git log or GitHub PR]**

"Real commits pushed. Real code. Not mocks."

## Manager Report (3:30 - 4:15)
**[Show the report tab]**

"Phase 6: The manager report. Every decision is documented — which tasks were reassigned to whom, with confidence scores and reasoning. Which tasks the AI completed autonomously. Full transparency."

**[Scroll through the report]**

"A manager can review this in 30 seconds instead of spending hours doing it manually."

## Webhook Demo (4:15 - 4:45)
**[Show a curl command or Postman hitting the webhook endpoint]**

"The system also supports webhooks. An HR system or calendar can trigger this automatically — no manual button needed."

```bash
curl -X POST http://localhost:8000/webhook/absence \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "P5", "source": "hr-system"}'
```

## Closing (4:45 - 5:00)
**[Show the dashboard with all phases complete]**

"The entire process took about 2 minutes. 10 tasks triaged, reassigned, and executed. Zero manual intervention. The Workforce Continuity Agent — keeping work moving when people can't."

---

## Key Points to Hit
- 6-phase pipeline with real-time visualization
- Hybrid human/AI decision making (threshold-based)
- Real side effects (git commits, database updates)
- Webhook integration for external triggers
- Manager report with full transparency
- Graceful fallback when LLM is unavailable
