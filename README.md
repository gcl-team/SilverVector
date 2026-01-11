# 📦 SilverVector

> The "Day 0" Dashboard Prototyping Tool.

SilverVector is a strictly local, privacy-focused tool that acts as a **prototyping engine**. It takes your raw Database Schema (DDL) and instantly generates professional Grafana Dashboard JSON models. Designed for the "Solo Engineer" and freelancers, it bridges the gap between Raw Data and Insights without the manual click-work.

**Note:** This is an open-source personal hobby project. It is not affiliated with Grafana Labs or any commercial observability platform.

# 🎯 Why SilverVector?

**1. The "Freelancer's Burden"**
Small teams and solo engineers often need professional dashboards but lack the time for hours of manual UI configuration. SilverVector acts as an **accelerator**, taking you from "Zero" to "First Draft" in seconds.

**2. No-Lock-in Prototyping**
While tools like Terraform are great for maintenance, they require an existing resource. SilverVector handles the chaotic "Drafting Phase". The output is standard Grafana JSON, which you fully own and can eventually export into GitOps workflows later.

# ✨ Expected Features

## Phase 1: The Core
- [ ] Static DDL Parsing: 

  - Description: Paste a CREATE TABLE script and automatically extract table names, column types, and constraints.
  - Tech: simple-ddl-parser.

- [ ] Smart Column Classification:

  - Description: Automatically tag columns as Time-Series (e.g., created_at), Metrics (e.g., total_amount), or Dimensions (e.g., status, store_id).

- [ ] Basic JSON Generation:

  - Description: Export a valid Grafana Dashboard JSON containing a basic Time-Series graph and a Stat panel.

## Phase 2: Enhanced User Experience
- [ ] Auto-Join Suggestions:

  - Description: Detect Foreign Keys or matching column names (e.g., user_id) to suggest SQL JOIN queries for cross-table insights.

- [ ] Multi-Panel Layouts:
  - Description: Logic to arrange panels in a clean grid (24-column system) so the dashboard looks "Pro" out of the box.

- [ ] Variable Injection:

  - Description: Automatically add Grafana Variables (Dropdowns) for categorical columns like Region or Status.

## Phase 3: Accessibility & Ease of Use
- [ ] Local Portability:
  - Description: A single-file .exe build that runs on an SME manager's laptop without needing to install Python.

- [ ] SQL dialect support:
  - Description: Toggle between MySQL, PostgreSQL, and MS SQL (SSMS) output formats.

- [ ] "Quick-Look" Preview:
  - Description: A small UI list showing exactly what panels will be created before you hit "Export."

# 🛠 Tech Stack

- Orchestration: Poetry
- GUI: CustomTkinter (Modern Dark Mode)
- Parser: simple-ddl-parser
- Data Models: Pydantic

# 🏃 Quick Start
1. Install Dependencies

```bash
poetry install
```

2. Run the App

```bash
poetry run python src/silvervector/main.py
```

3. The Workflow

1. Copy your DDL from DBeaver or SSMS;
2. Paste into SilverVector;
3. Click "Analyze" to verify columns;
4. Click "Generate Dashboard".
5. Import the resulting .json into your Grafana instance.

# 🛡 Philosophy & Security

- **Zero-Knowledge:** SilverVector never asks for database credentials or API keys. We only need your Schema structure (DDL).
- **Offline-First:** Built with a desktop GUI (CustomTkinter) to work in air-gapped or low-connectivity environments.
- **Human-in-the-Loop:** Regex isn't perfect. The UI allows you to verify and tweak detected metrics *before* generation, preventing broken JSONs.

# 🏗 Project Structure

```plaintext
silvervector/
├── silvervector/
│   ├── main.py        # CustomTkinter UI
│   ├── parser.py      # DDL to Intent logic
│   ├── generator.py   # Intent to Grafana JSON logic
│   └── templates/     # Base Dashboard JSON boilerplates
├── pyproject.toml
└── README.md
```

# 🔮 Future Roadmap (Concepts)

These are experimental ideas for expanding the tool's capabilities:

1. **Automated Alert Provisioning**
   - *Concept:* Automatically generate Grafana Alert Rules in the JSON based on schema patterns (e.g., column names like `status` or `error_code`).
   - *Goal:* Provide basic monitoring "out of the box" so users have starting points for their alerting strategy.

2. **Log Pattern Recognition (Loki Support)**
   - *Concept:* Allow users to provide a sample log line (JSON/NGINX) alongside their SQL schema.
   - *Goal:* Generate basic Loki dashboard panels (Logs Volume, Error Rate) to complement SQL metrics.

3. **Query Optimization Hints**
   - *Concept:* Analyze the DDL and generated dashboard queries to suggest potential indexes (e.g., "Filtering by `user_id` might benefit from an index").
   - *Goal:* Help users avoid slow queries when deploying generated dashboards on production databases.

4. **Reporting Templates**
   - *Concept:* Add a specific template option for "Executive Summary" dashboards.
   - *Goal:* Create layouts optimized for PDF export and monthly reporting (high-level KPIs, uptime stats).