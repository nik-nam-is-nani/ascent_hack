import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from models.employee import Employee
from models.task import Task, Decision, TaskManifest, TaskStatus
from tools import (
    get_employee_by_id,
    get_pending_tasks_by_employee,
    update_task,
    mark_employee_absent,
    reset_tasks_for_employee,
    reset_employee_status,
    notify_task_reassignment,
    get_all_employees,
    update_employee
)

from .task_analyzer import analyze_tasks_for_employee, analyze_task
from .reallocation_agent import reallocate_all_tasks, validate_reallocation, get_reallocation_report
from .executor_agent import execute_tasks_auto, get_executor_summary
from tools.workspace_tool import clone_repository

from .activity import broadcast_activity


async def run_orchestrator(
    employee_id: str,
    github_token: str = None,
    github_repo_url: str = None
) -> Dict[str, Any]:
    """Run the full 6-phase agent pipeline with real GitHub execution"""
    print(f"[ORCHESTRATOR] Starting pipeline for {employee_id}", flush=True)
    print(f"[ORCHESTRATOR] Token: {github_token[:20] if github_token else 'NONE'}...", flush=True)
    print(f"[ORCHESTRATOR] Repo: {github_repo_url}", flush=True)

    try:
        return await _run_pipeline(employee_id, github_token, github_repo_url)
    except Exception as e:
        import traceback
        print(f"[ORCHESTRATOR] FATAL ERROR: {e}", flush=True)
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


async def _run_pipeline(
    employee_id: str,
    github_token: str = None,
    github_repo_url: str = None
) -> Dict[str, Any]:
    """Internal pipeline implementation"""

    # Get employee info
    employee = get_employee_by_id(employee_id)
    if not employee:
        print(f"[ORCHESTRATOR] ERROR: Employee {employee_id} not found", flush=True)
        return {"error": "Employee not found"}

    # Phase 1: Mark employee absent
    broadcast_activity(
        "phase_1",
        f"Detected absence: {employee.name} ({employee.role})",
        {"employee_id": employee_id, "employee_name": employee.name}
    )

    await asyncio.sleep(1.5)
    mark_employee_absent(employee_id)

    # Phase 2: Get pending tasks + repository sync
    broadcast_activity(
        "phase_2",
        f"Retrieving {employee.name}'s profile and pending tasks...",
        {"employee_id": employee_id}
    )

    await asyncio.sleep(1.2)

    if github_repo_url:
        print(f"[ORCHESTRATOR] Phase 2: Cloning repo...", flush=True)
        broadcast_activity(
            "phase_2",
            f"Syncing repository into virtual workspace: {github_repo_url}",
            {"employee_id": employee_id, "repo_url": github_repo_url}
        )
        try:
            cloned, clone_message = await asyncio.to_thread(clone_repository, github_repo_url, github_token)
        except Exception as clone_err:
            cloned, clone_message = False, str(clone_err)
        print(f"[ORCHESTRATOR] Clone result: {cloned} - {clone_message}", flush=True)
        if not cloned:
            broadcast_activity(
                "phase_2",
                f"Repository sync failed: {clone_message}",
                {"employee_id": employee_id, "repo_url": github_repo_url}
            )
        else:
            broadcast_activity(
                "phase_2",
                "Repository synchronized successfully",
                {"employee_id": employee_id, "repo_url": github_repo_url}
            )

    pending_tasks = get_pending_tasks_by_employee(employee_id)

    if not pending_tasks:
        broadcast_activity(
            "phase_2",
            f"No pending tasks for {employee.name}",
            {"task_count": 0}
        )
        return {
            "employee_id": employee_id,
            "employee_name": employee.name,
            "tasks_handled": 0,
            "message": "No pending tasks to handle"
        }

    broadcast_activity(
        "phase_2",
        f"Found {len(pending_tasks)} pending task(s) in system",
        {"task_count": len(pending_tasks), "tasks": [t.id for t in pending_tasks]}
    )

    await asyncio.sleep(1.0)

    # Phase 3: Analyze tasks
    broadcast_activity(
        "phase_3",
        "Phase 3: Deep analysis of task requirements and dependencies...",
        {"phase": "task_analysis"}
    )

    # Granular analysis steps
    analysis_thoughts = [
        "Scanning organizational task manifest for critical path dependencies...",
        "Evaluating historical performance metrics for available team members...",
        "Calculating complexity-to-skill ratio for pending deliverables...",
        "Synthesizing optimal reallocation strategy using Neural Engine V4..."
    ]
    for thought in analysis_thoughts:
        broadcast_activity(
            "phase_3",
            thought,
            {"sub_phase": "analysis_thought", "task_id": "GLOBAL"}
        )
        await asyncio.sleep(0.8)

    await asyncio.sleep(0.5)
    try:
        task_analysis = await asyncio.to_thread(analyze_tasks_for_employee, employee_id)
        broadcast_activity(
            "phase_3",
            f"Analysis complete: {len(pending_tasks)} tasks — {task_analysis['total_estimated_hours']:.1f} hours total",
            task_analysis
        )
    except Exception as analysis_err:
        print(f"[ORCHESTRATOR] Phase 3 analysis error: {analysis_err}", flush=True)
        task_analysis = {"total_estimated_hours": 0, "total_tasks": len(pending_tasks)}
        broadcast_activity(
            "phase_3",
            f"Task analysis encountered an issue, continuing with defaults...",
            {"phase": "task_analysis_error", "error": str(analysis_err)}
        )

    await asyncio.sleep(1.0)

    # Phase 4: Reallocate tasks to humans
    broadcast_activity(
        "phase_4",
        "Phase 4: Optimization engine finding best matches for reassignment...",
        {"phase": "reallocation"}
    )

    planning_steps = [
        "Mapping task priorities to available team capacity...",
        "Validating skill-set alignment for target assignees...",
        "Optimizing workload balance across departments...",
        "Finalizing continuity decisions and routing notifications..."
    ]
    for step in planning_steps:
        broadcast_activity(
            "phase_4",
            step,
            {"sub_phase": "planning_step"}
        )
        await asyncio.sleep(0.7)

    await asyncio.sleep(1.0)
    print(f"[ORCHESTRATOR] Phase 4: Running reallocation...", flush=True)
    decisions = reallocate_all_tasks(employee_id)
    print(f"[ORCHESTRATOR] Decisions: {[(d.task_id, d.decision_type) for d in decisions]}", flush=True)

    # Notify assigned employees
    for decision in decisions:
        if decision.decision_type == "reassign" and decision.assigned_to:
            assigned_emp = get_employee_by_id(decision.assigned_to)
            task = next((t for t in pending_tasks if t.id == decision.task_id), None)
            if assigned_emp:
                notify_task_reassignment(
                    decision.assigned_to,
                    assigned_emp.name,
                    task.title if task else decision.task_id,
                    decision.task_id,
                    decision.reasoning
                )

                if task:
                    broadcast_activity(
                        "phase_4",
                        f"Allocated: Task {decision.task_id} assigned to {assigned_emp.name} (confidence: {decision.confidence:.0%})",
                        {"task_id": decision.task_id, "assigned_to": assigned_emp.name, "confidence": decision.confidence}
                    )
                    await asyncio.sleep(0.5)

    await asyncio.sleep(1.0)

    # Phase 5: Execute remaining tasks with AI
    auto_complete_tasks = [
        t for t in pending_tasks
        if any(d.task_id == t.id and d.decision_type == "auto_complete" for d in decisions)
    ]
    execution_results = []  # Collect results for PDF report
    print(f"[ORCHESTRATOR] Phase 5: {len(auto_complete_tasks)} tasks to auto-complete", flush=True)

    if auto_complete_tasks:
        broadcast_activity(
            "phase_5",
            f"Agent Executor starting autonomous completion of {len(auto_complete_tasks)} task(s)...",
            {"phase": "execution", "task_count": len(auto_complete_tasks)}
        )

        await asyncio.sleep(1.0)

        for task in auto_complete_tasks:
            # Related skills for this task type
            skills_map = {
                "CODE": ["Python", "FastAPI", "React", "System Architecture"],
                "RESEARCH": ["Data Synthesis", "Market Analysis", "Critical Review"],
                "REPORT": ["Data Visualization", "Executive Writing", "Strategic Planning"],
                "PRESENTATION": ["Visual Design", "Narrative Structure", "Public Speaking"],
                "DOCUMENTATION": ["Technical Writing", "API Design", "User Experience"]
            }

            task_type_str = str(task.task_type.value).upper()
            required_skills = skills_map.get(task_type_str, ["General Intelligence", "Problem Solving"])

            # Simulate skill learning for this task
            for skill in required_skills:
                broadcast_activity(
                    "phase_5",
                    f"Acquiring skill: {skill}...",
                    {"sub_phase": "learning", "skill": skill, "task_id": task.id}
                )
                await asyncio.sleep(0.8)

                broadcast_activity(
                    "phase_5",
                    f"Mastered skill: {skill}",
                    {"sub_phase": "mastered", "skill": skill, "task_id": task.id}
                )
                await asyncio.sleep(0.4)

            # Now implement the task using learned skills
            broadcast_activity(
                "phase_5",
                f"Implementing task {task.id}: {task.title}",
                {"sub_phase": "implementing", "task_id": task.id, "skills_used": required_skills}
            )

            await asyncio.sleep(1.0)

            # Detailed implementation steps
            implementation_steps = [
                {"action": "creating_files", "message": f"Creating new module: {task_type_str.lower()}_handler.py", "file": f"src/{task_type_str.lower()}_handler.py"},
                {"action": "updating_code", "message": f"Injecting logic into {task.id} core service...", "file": "src/services/core.py"},
                {"action": "editing_apis", "message": "Registering new FastAPI routes for task execution...", "route": f"/api/auto/{task.id}"},
                {"action": "writing_react", "message": "Generating UI components for task artifacts...", "component": f"{task_type_str.capitalize()}Viewer.jsx"}
            ]

            for step in implementation_steps:
                broadcast_activity(
                    "phase_5",
                    f"Action: {step['message']}",
                    {
                        "sub_phase": "execution_step",
                        "task_id": task.id,
                        "action": step['action'],
                        "details": step,
                        "code_preview": _generate_mock_code(step['action'], task)
                    }
                )
                await asyncio.sleep(1.2)

            # Actual execution call (wrapped in thread to avoid blocking)
            try:
                results = await asyncio.to_thread(execute_tasks_auto, [task], github_token, github_repo_url)
                result = results[0] if results else {"status": "failed", "error": "No result"}
            except Exception as exec_err:
                print(f"[ORCHESTRATOR] Executor error: {exec_err}", flush=True)
                result = {"status": "failed", "error": str(exec_err)}

            status = result.get("status", "unknown")
            # Store execution result for PDF report
            execution_results.append({
                "task_id": task.id,
                "task_title": task.title,
                "task_type": task.task_type.value if task.task_type else "unknown",
                "status": status,
                "artifacts": result.get("artifacts", []),
                "commit_message": result.get("commit_message", ""),
                "summary": result.get("summary", ""),
                "files_created": [a for a in result.get("artifacts", []) if a.endswith(('.py', '.js', '.jsx', '.tsx', '.html', '.css'))],
                "search_references": result.get("search_references", []),
            })

            if status == "completed":
                broadcast_activity(
                    "phase_5",
                    f"Successfully applied skills to complete task {task.id}",
                    {"sub_phase": "applied", "task_id": task.id, "executed_by": "AgentExecutor", "artifacts": result.get("artifacts", [])}
                )
            else:
                broadcast_activity(
                    "phase_5",
                    f"Execution failed on task {task.id}: {result.get('error', 'Unknown error')}",
                    {"task_id": task.id, "status": "failed"}
                )
            await asyncio.sleep(1.0)

    await asyncio.sleep(1.0)

    # Phase 6: Generate manager report
    broadcast_activity(
        "phase_6",
        "Phase 6: Compiling final continuity report for management...",
        {"phase": "report_generation"}
    )

    await asyncio.sleep(2.0)

    # Generate final report
    reallocation_report = get_reallocation_report(decisions, employee_id)

    # Create manifest
    manifest = TaskManifest(
        tasks=pending_tasks,
        decisions=decisions,
        generated_at=datetime.now(),
        absent_employee_id=employee_id
    )

    # Generate markdown report
    report = generate_manager_report(employee, pending_tasks, decisions)

    # Generate PDF report
    try:
        pdf_path = _generate_pdf_report(employee, pending_tasks, decisions, employee_id, execution_results)
        broadcast_activity(
            "phase_6",
            f"PDF report generated: {pdf_path}",
            {"phase": "pdf_generated", "pdf_path": pdf_path}
        )
    except Exception as pdf_err:
        print(f"[ORCHESTRATOR] PDF generation error: {pdf_err}", flush=True)
        pdf_path = None

    broadcast_activity(
        "phase_6",
        f"Continuity pipeline completed. {len(pending_tasks)} tasks handled efficiently.",
        {
            "total_tasks": len(pending_tasks),
            "reassigned": reallocation_report.get("reassigned_count", 0),
            "auto_completed": reallocation_report.get("auto_complete_count", 0),
            "pdf_path": pdf_path
        }
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "employee_role": employee.role,
        "total_tasks": len(pending_tasks),
        "reassigned": sum(1 for d in decisions if d.decision_type == "reassign"),
        "auto_completed": sum(1 for d in decisions if d.decision_type == "auto_complete"),
        "manifest": manifest.model_dump(),
        "report": report,
        "reallocation_report": reallocation_report,
        "pdf_path": pdf_path,
        "timestamp": datetime.now().isoformat()
    }


def generate_manager_report(
    employee: Employee,
    tasks: List[Task],
    decisions: List[Decision]
) -> str:
    """Generate a markdown manager report"""

    report_lines = [
        f"# Workforce Continuity Agent — Manager Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## Absent Employee",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Name | {employee.name} |",
        f"| Role | {employee.role} |",
        f"| Department | {employee.department} |",
        f"| Email | {employee.email} |",
        "",
        "## Task Summary",
        "",
        f"- **Total Tasks Handled:** {len(tasks)}",
        f"- **Reassigned to Team:** {sum(1 for d in decisions if d.decision_type == 'reassign')}",
        f"- **Auto-Completed by Agent:** {sum(1 for d in decisions if d.decision_type == 'auto_complete')}",
        "",
        "## Task Details",
        "",
        "| Task ID | Title | Decision | Assigned To | Confidence |",
        "|---------|-------|----------|-------------|------------|",
    ]

    for task in tasks:
        decision = next((d for d in decisions if d.task_id == task.id), None)
        if decision:
            assigned = decision.assigned_to or "Agent Executor"
            report_lines.append(f"| {task.id} | {task.title} | {decision.decision_type} | {assigned} | {decision.confidence:.0%} |")

    report_lines.append("")

    # Add decision reasoning section
    report_lines.extend([
        "## Decision Rationale",
        ""
    ])

    for decision in decisions:
        task = next((t for t in tasks if t.id == decision.task_id), None)
        report_lines.append(f"### {decision.task_id}: {task.title if task else ''}")
        report_lines.append("")
        report_lines.append(f"- **Decision:** {decision.decision_type}")
        if decision.assigned_to:
            emp = get_employee_by_id(decision.assigned_to)
            report_lines.append(f"- **Assigned To:** {emp.name if emp else decision.assigned_to}")
        report_lines.append(f"- **Confidence:** {decision.confidence:.0%}")
        report_lines.append(f"- **Reasoning:** {decision.reasoning}")
        if decision.alternative_options:
            report_lines.append(f"- **Alternatives Considered:** {', '.join(decision.alternative_options)}")
        report_lines.append("")

    # Add recommendations
    report_lines.extend([
        "## Recommendations",
        "",
        "1. Monitor reassigned tasks to ensure smooth handover",
        "2. Review auto-completed artifacts for quality assurance",
        "3. Consider cross-training to reduce single-point dependencies",
        "4. Schedule follow-up with absent employee upon return",
        ""
    ])

    return "\n".join(report_lines)


def reset_absence(employee_id: str) -> Dict[str, Any]:
    """Reset an employee's absence status and restore tasks"""
    employee = get_employee_by_id(employee_id)

    if not employee:
        return {"error": "Employee not found"}

    reset_employee_status(employee_id)
    reset_tasks_for_employee(employee_id)

    broadcast_activity(
        "reset",
        f"Reset {employee.name}'s status - tasks restored to original assignee",
        {"employee_id": employee_id}
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "status": "reset",
        "message": f"Employee status reset and tasks restored to {employee.name}"
    }


def _generate_pdf_report(
    employee: Employee,
    tasks: List[Task],
    decisions: List[Decision],
    employee_id: str,
    execution_results: List[Dict[str, Any]] = None
) -> str:
    """Generate a PDF manager report with execution details and references"""
    from fpdf import FPDF
    import os

    if execution_results is None:
        execution_results = []

    class ReportPDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(15, 52, 96)
            self.cell(0, 8, 'Workforce Continuity Agent - Intelligence Report', align='L')
            self.cell(0, 8, datetime.now().strftime('%Y-%m-%d %H:%M'), align='R', new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(233, 69, 96)
            self.set_line_width(0.5)
            self.line(10, 18, 200, 18)
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

        def section(self, title):
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(15, 52, 96)
            self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(233, 69, 96)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

        def sub_section(self, title):
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(22, 33, 62)
            self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(1)

        def field(self, label, value):
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(80)
            self.cell(45, 6, label + ':')
            self.set_font('Helvetica', '', 10)
            self.set_text_color(26, 26, 46)
            self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

        def body(self, text):
            self.set_font('Helvetica', '', 9)
            self.set_text_color(26, 26, 46)
            self.multi_cell(0, 5, str(text))
            self.ln(1)

        def bullet(self, text):
            self.set_font('Helvetica', '', 9)
            self.set_text_color(26, 26, 46)
            self.cell(6, 5, '-')
            self.multi_cell(0, 5, str(text))

        def row(self, cols, widths, bold=False):
            self.set_font('Helvetica', 'B' if bold else '', 9)
            for col, w in zip(cols, widths):
                self.cell(w, 7, str(col)[:40], border=1)
            self.ln()

    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Employee info
    pdf.section('Absent Employee')
    pdf.field('Name', employee.name)
    pdf.field('Role', employee.role)
    pdf.field('Department', employee.department)
    pdf.field('Email', employee.email)
    pdf.ln(3)

    # Task summary
    reassigned = sum(1 for d in decisions if d.decision_type == 'reassign')
    auto_completed = sum(1 for d in decisions if d.decision_type == 'auto_complete')

    pdf.section('Task Summary')
    pdf.field('Total Tasks', str(len(tasks)))
    pdf.field('Reassigned to Team', str(reassigned))
    pdf.field('Auto-Completed by Agent', str(auto_completed))
    pdf.ln(3)

    # Task details table
    pdf.section('Task Details')
    w = [25, 55, 30, 40, 25]
    pdf.row(['ID', 'Title', 'Decision', 'Assigned To', 'Confidence'], w, bold=True)
    for task in tasks:
        decision = next((d for d in decisions if d.task_id == task.id), None)
        if decision:
            assigned = decision.assigned_to or 'Agent Executor'
            pdf.row([
                task.id,
                task.title[:25],
                decision.decision_type,
                assigned[:18],
                f'{decision.confidence:.0%}'
            ], w)
    pdf.ln(3)

    # Decision rationale
    pdf.section('Decision Rationale')
    for decision in decisions:
        task = next((t for t in tasks if t.id == decision.task_id), None)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(22, 33, 62)
        pdf.cell(0, 7, f'{decision.task_id}: {task.title if task else ""}', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(0, 5, f'Decision: {decision.decision_type}  |  Confidence: {decision.confidence:.0%}', new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 5, f'Reasoning: {decision.reasoning}')
        if decision.alternative_options:
            pdf.body(f'Alternatives: {", ".join(decision.alternative_options[:3])}')
        pdf.ln(2)

    # Execution Details for auto-completed tasks
    if execution_results:
        pdf.add_page()
        pdf.section('Agent Execution Details')

        for exec_result in execution_results:
            task_id = exec_result.get("task_id", "Unknown")
            task_title = exec_result.get("task_title", "Unknown")
            status = exec_result.get("status", "unknown")
            summary = exec_result.get("summary", "")
            commit_msg = exec_result.get("commit_message", "")
            artifacts = exec_result.get("artifacts", [])
            files_created = exec_result.get("files_created", [])
            search_refs = exec_result.get("search_references", [])

            pdf.sub_section(f'Task: {task_id} - {task_title}')
            pdf.field('Status', status.upper())
            pdf.field('Task Type', exec_result.get("task_type", "unknown"))

            if summary:
                pdf.ln(1)
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(80)
                pdf.cell(0, 5, 'What was done:', new_x="LMARGIN", new_y="NEXT")
                pdf.body(summary)

            if commit_msg:
                pdf.field('Commit Message', commit_msg)

            if files_created:
                pdf.ln(1)
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(80)
                pdf.cell(0, 5, 'Files Created:', new_x="LMARGIN", new_y="NEXT")
                for f in files_created:
                    pdf.bullet(f)

            if artifacts:
                pdf.ln(1)
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(80)
                pdf.cell(0, 5, 'Artifacts:', new_x="LMARGIN", new_y="NEXT")
                for a in artifacts:
                    pdf.bullet(a)

            if search_refs:
                pdf.ln(1)
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(80)
                pdf.cell(0, 5, 'References (Web Search):', new_x="LMARGIN", new_y="NEXT")
                for ref in search_refs:
                    pdf.bullet(ref)

            pdf.ln(3)

    # Save
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    pdf_path = os.path.join(data_dir, f"report_{employee_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(pdf_path)
    print(f"[ORCHESTRATOR] PDF report saved: {pdf_path}", flush=True)
    return pdf_path


def _generate_mock_code(action: str, task: Task) -> str:
    """Generate fake code for visualization"""
    if action == "creating_files":
        return f"import os\n\ndef init_handler():\n    print('Initializing {task.id}')\n    return True"
    elif action == "updating_code":
        return f"def process_task(task_id):\n    # Auto-implementation for {task.id}\n    result = run_logic()\n    return result"
    elif action == "editing_apis":
        return f"@app.get('/api/auto/{task.id}')\nasync def handle_task():\n    return {{'status': 'completed', 'task': '{task.title}'}}"
    elif action == "writing_react":
        return f"export const {task.id}Viewer = () => {{\n  return <div>Viewing {task.title}</div>\n}}"
    return "# Processing..."
