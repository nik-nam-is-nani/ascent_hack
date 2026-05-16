from fpdf import FPDF

class WriteupPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(15, 52, 96)
        self.cell(0, 8, 'Workforce Continuity Agent', align='L')
        self.cell(0, 8, 'Ascent Hack 2026', align='R', new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(15, 52, 96)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def sub_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(22, 33, 62)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(26, 26, 46)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(26, 26, 46)
        self.cell(8, 5.5, '-')
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def table_row(self, cols, widths, bold=False):
        style = 'B' if bold else ''
        self.set_font('Helvetica', style, 9)
        for i, (col, w) in enumerate(zip(cols, widths)):
            self.cell(w, 7, col, border=1)
        self.ln()

pdf = WriteupPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# PAGE 1: Cover + Problem
pdf.add_page()
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(15, 52, 96)
pdf.ln(30)
pdf.cell(0, 15, 'Workforce Continuity Agent', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 14)
pdf.set_text_color(100)
pdf.cell(0, 10, 'AI-Powered Automatic Task Reassignment', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(80)
pdf.cell(0, 7, 'Team: Ascent Hack', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, 'Date: May 2026', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(20)

pdf.section_title('The Problem')
pdf.body_text('When an employee is absent unexpectedly, their pending tasks stall. Managers must manually triage each task: find a replacement, check skills, rebalance workloads. This process is slow, error-prone, and creates bottlenecks that ripple across teams.')
pdf.body_text('Current solutions are reactive and manual. There is no intelligent system that automatically evaluates task complexity, matches skills across the team, and either reassigns tasks to the best available person or completes them autonomously using AI.')

pdf.section_title('Our Solution')
pdf.body_text('The Workforce Continuity Agent is a multi-agent AI system that detects employee absence and automatically handles all pending tasks through a 6-phase pipeline. It analyzes tasks, evaluates team capacity, makes reallocation decisions, and can even complete tasks autonomously using AI code generation and web search.')

pdf.sub_title('6-Phase Pipeline')
phases = [
    'Phase 1 - Detection: Absence detected via webhook or manual trigger',
    'Phase 2 - Retrieval: Pending tasks retrieved, GitHub repo synced',
    'Phase 3 - Analysis: Tasks analyzed for skills, complexity, estimated hours',
    'Phase 4 - Reallocation: Team scored, tasks reassigned or marked for AI',
    'Phase 5 - Execution: AI completes tasks (web search, code gen, git push)',
    'Phase 6 - Reporting: Manager report with decision rationale generated'
]
for p in phases:
    pdf.bullet(p)

# PAGE 2: Architecture
pdf.add_page()
pdf.section_title('Agent Architecture')
pdf.body_text('The system uses 5 specialized agents coordinated by a central orchestrator. Each agent has a distinct responsibility and they communicate through a shared activity bus with WebSocket broadcasting.')

agents = [
    ('Orchestrator', 'Central pipeline controller driving all 6 phases'),
    ('Task Analyzer', 'LLM analysis: skills, complexity, task splitting'),
    ('Availability Agent', 'Skill matching and workload scoring'),
    ('Reallocation Agent', 'Threshold decisions: reassign or auto-complete'),
    ('Executor Agent', 'Code gen, web search, file write, git push'),
]
w = [50, 140]
pdf.table_row(['Agent', 'Responsibility'], w, bold=True)
for name, desc in agents:
    pdf.table_row([name, desc], w)

pdf.ln(5)
pdf.sub_title('Technology Stack')
tech = [
    ('Backend', 'FastAPI (Python)'),
    ('Frontend', 'React + Vite + Tailwind CSS'),
    ('AI Engine', 'OpenRouter (Gemini 2.0 Flash)'),
    ('Database', 'SQLite (file-based)'),
    ('Version Control', 'GitHub API + Git CLI'),
    ('Web Search', 'DuckDuckGo API'),
]
pdf.table_row(['Component', 'Technology'], w, bold=True)
for name, desc in tech:
    pdf.table_row([name, desc], w)

pdf.ln(5)
pdf.sub_title('Key Design Decisions')
pdf.bullet('Hybrid autonomy: reassign when confidence > 0.6, otherwise AI completes')
pdf.bullet('Graceful degradation: LLM failures fall back to heuristics')
pdf.bullet('Real side effects: actual git commits, DB updates, notifications')
pdf.bullet('Async pipeline: HTTP returns immediately, pipeline runs in background')

# PAGE 3: Impact
pdf.add_page()
pdf.section_title('Autonomy in Practice')
pdf.body_text('The system operates on a spectrum of autonomy. For each task, the agent evaluates whether a human teammate can handle it better or if AI should complete it autonomously.')

pdf.sub_title('Real-World Scenario')
pdf.body_text('A frontend developer (P5) is absent with 3 pending tasks:')
pdf.bullet('Cart System (CODE, 6h): P1 has 90% React match, score 0.78. Reassigned.')
pdf.bullet('API Integration (CODE, 4h): No frontend dev has backend skills. Auto-completed by AI.')
pdf.bullet('Design Review (REVIEW, 2h): P6 has relevant skills, score 0.82. Reassigned.')

pdf.ln(3)
pdf.sub_title('Verifiable Side Effects')
pdf.bullet('Database: Task statuses updated, assignments changed')
pdf.bullet('GitHub: Real commits pushed with descriptive messages')
pdf.bullet('Notifications: Team members notified of assignments')
pdf.bullet('Reports: Manager reports with full decision rationale')
pdf.bullet('WebSocket: Complete activity log of every agent action')

pdf.ln(3)
pdf.sub_title('Impact Metrics')
w2 = [50, 60, 60]
pdf.table_row(['Metric', 'Manual', 'With Agent'], w2, bold=True)
pdf.table_row(['Triage 10 tasks', '2-4 hours', 'Under 2 minutes'], w2)
pdf.table_row(['Skill matching', 'Judgment', 'Data-driven'], w2)
pdf.table_row(['Tasks missed', 'Common', 'Zero'], w2)
pdf.table_row(['After-hours', 'None', '24/7 autonomous'], w2)

pdf.ln(5)
pdf.sub_title('Conclusion')
pdf.body_text('The Workforce Continuity Agent demonstrates that multi-agent AI systems can meaningfully reduce organizational friction caused by employee absence. By combining intelligent task analysis, skill-based reallocation, and autonomous execution, it ensures work continues regardless of team disruptions.')

import os
output_path = os.path.join(os.path.dirname(__file__), 'writeup.pdf')
pdf.output(output_path)
print(f'PDF generated: {output_path}')
