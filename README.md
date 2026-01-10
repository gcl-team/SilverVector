# 📦 SilverVector

> "Precision Observability for the Modern Enterprise."

SilverVector is a zero-trust observability architect. It takes your raw Database Schema (DDL) and instantly generates a professional Grafana Dashboard JSON, without ever requiring access to your live database.

# 🚀 The Mission
Enterprises are often "data-blind" because their business logic is buried in SQL tables. SilverVector bridges the gap between Raw Data and Executive Insights in seconds.

# ✨ Expected Features

## Phase 1: The Core
- [ ] Static DDL Parsing: * Description: Paste a CREATE TABLE script and automatically extract table names, column types, and constraints.
  - Tech: simple-ddl-parser.

- [ ] Smart Column Classification:

  - Description: Automatically tag columns as Time-Series (e.g., created_at), Metrics (e.g., total_amount), or Dimensions (e.g., status, store_id).

- [ ] Basic JSON Generation:

  - Description: Export a valid Grafana Dashboard JSON containing a basic Time-Series graph and a Stat panel.

## Phase 2: The "Sales Engineer" Polish
- [ ] Auto-Join Suggestions:

  - Description: Detect Foreign Keys or matching column names (e.g., user_id) to suggest SQL JOIN queries for cross-table insights.

- [ ] Multi-Panel Layouts:
  - Description: Logic to arrange panels in a clean grid (24-column system) so the dashboard looks "Pro" out of the box.

- [ ] Variable Injection:

  - Description: Automatically add Grafana Variables (Dropdowns) for categorical columns like Region or Status.

## Phase 3: The "Kiasi" SME Layer
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

# 🛡 Security & Privacy

- No Database Connection: SilverVector never asks for your host, username, or password.
- Local Processing: Your schema never leaves your machine.
- Static Only: We read the structure, not the data.

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
