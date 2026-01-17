import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from pygments import lex
from pygments.lexers import SqlLexer, JsonLexer
import json

# Try importing from package, fallback to local if running script directly
try:
    from silvervector.parser import SilverVectorParser
except ImportError:
    from parser import SilverVectorParser

# Initialize the UI Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SilverVectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SilverVector - The Enterprise Grafana Bridge")
        self.geometry("1100x700")

        # NEW Layout Configuration: Side-by-Side
        # Column 0: Editor Source (Weight 1)
        # Column 1: Config/Preview (Weight 1)
        # Row 0: Toolbar (Auto-height)
        # Row 1: Text Area (Expandable weight)
        # Row 2: Status Bar / Progress (Auto-height)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Top Toolbar ---
        self.toolbar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color="#2b2b2b")
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Logo/Brand (Compact)
        self.logo_label = ctk.CTkLabel(self.toolbar, text="SilverVector", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        self.logo_label.pack(side="left", padx=15)

        # Square Icon Buttons
        btn_size = 32

        # Load File (Unicode Folder)
        self.load_btn = ctk.CTkButton(self.toolbar, text="\U0001F4C1", width=btn_size, height=btn_size, 
                                    fg_color="transparent", hover_color="#404040",
                                    command=self.load_file)
        self.load_btn.pack(side="left", padx=5, pady=5)

        # Analyze (Unicode Magnifying Glass)
        self.analyze_btn = ctk.CTkButton(self.toolbar, text="\U0001F50D", width=btn_size, height=btn_size, 
                                        fg_color="transparent", hover_color="#404040",
                                        command=self.analyze_ddl)
        self.analyze_btn.pack(side="left", padx=5, pady=5)

        # Separator
        self.sep = ctk.CTkFrame(self.toolbar, width=2, height=20, fg_color="#444444")
        self.sep.pack(side="left", padx=10)

        # Generate (Unicode Rocket)
        self.generate_btn = ctk.CTkButton(self.toolbar, text="\U0001F680", width=btn_size, height=btn_size, 
                                        fg_color="#0085D0", hover_color="#23A9F2",
                                        command=self.generate_grafana_json)
        self.generate_btn.pack(side="left", padx=5, pady=5)

        # --- 2. Main Editor Area ---
        # We use a frame to give it some nice padding from the edges
        self.editor_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.editor_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(0, weight=1)

        # Tabview for Source/Output
        self.editor_tabs = ctk.CTkTabview(self.editor_frame)
        self.editor_tabs.grid(row=0, column=0, sticky="nsew")
        self.editor_tabs.add("Source SQL")
        self.editor_tabs.add("Generated JSON")

        # Tab 1: Source SQL
        self.text_area = ctk.CTkTextbox(self.editor_tabs.tab("Source SQL"), font=("Consolas", 14), corner_radius=8,
                                        border_width=1, border_color="#333333")
        self.text_area.pack(expand=True, fill="both")

        # Tab 2: JSON Output
        self.json_area = ctk.CTkTextbox(self.editor_tabs.tab("Generated JSON"), font=("Consolas", 14), corner_radius=8,
                                        border_width=1, border_color="#333333")
        self.json_area.pack(expand=True, fill="both")

        # --- 2.5 Preview/Config Area (Right Side) ---
        self.preview_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.preview_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        # Title for Preview
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Dashboard Config", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.preview_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_frame, label_text="Detected Metrics",
                                                   label_font=ctk.CTkFont(size=12, weight="bold"))
        self.preview_scroll.grid(row=1, column=0, sticky="nsew")

        # --- 3. Bottom Status/Progress Bar ---
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#2b2b2b")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=("Segoe UI", 11))
        self.status_label.pack(side="left", padx=10)
        self.status_label.configure(text_color="#0085D0")

        self.progress_bar = ctk.CTkProgressBar(self.status_bar, mode="indeterminate", height=4)
        self.progress_bar.pack(side="right", padx=10, fill="x", expand=True)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget() # Hide initially

        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        # Define colors for dark mode (SQL)
        self.text_area.tag_config("keyword", foreground="#569cd6")
        self.text_area.tag_config("type", foreground="#4ec9b0")
        self.text_area.tag_config("string", foreground="#ce9178")
        self.text_area.tag_config("comment", foreground="#6a9955")
        self.text_area.bind("<KeyRelease>", self.highlight_sql)

        # Define colors for dark mode (JSON)
        self.json_area.tag_config("key", foreground="#9cdcfe")      # Keys (Light Blue)
        self.json_area.tag_config("string", foreground="#ce9178")   # Strings (Orange)
        self.json_area.tag_config("number", foreground="#b5cea8")   # Numbers (Light Green)
        self.json_area.tag_config("keyword", foreground="#569cd6")  # Booleans/Null (Blue)
        self.json_area.bind("<KeyRelease>", self.highlight_json)

    def highlight_json(self, event=None):
        content = self.json_area.get("1.0", "end-1c")
        
        # Remove existing tags
        for tag in ["key", "string", "number", "keyword"]:
            self.json_area.tag_remove(tag, "1.0", "end")

        # Use Pygments to lex the JSON
        lexer = JsonLexer()
        tokens = lex(content, lexer)
        
        # Apply tags based on token types
        start_index = "1.0"
        for token_type, value in tokens:
            end_index = self.json_area.index(f"{start_index} + {len(value)}c")
            
            token_str = str(token_type)
            if "Name.Tag" in token_str: # JSON Keys
                self.json_area.tag_add("key", start_index, end_index)
            elif "Literal.String" in token_str: # String Values
                self.json_area.tag_add("string", start_index, end_index)
            elif "Literal.Number" in token_str: # Numbers
                self.json_area.tag_add("number", start_index, end_index)
            elif "Keyword" in token_str: # true/false/null
                self.json_area.tag_add("keyword", start_index, end_index)
                
            start_index = end_index

    def highlight_sql(self, event=None):
        content = self.text_area.get("1.0", "end-1c")
        # Store the current cursor position
        cursor_pos = self.text_area.index("insert")
        
        # Remove existing tags
        for tag in ["keyword", "type", "string", "comment"]:
            self.text_area.tag_remove(tag, "1.0", "end")

        # Use Pygments to lex the SQL
        lexer = SqlLexer()
        tokens = lex(content, lexer)
        
        # Apply tags based on token types
        start_index = "1.0"
        for token_type, value in tokens:
            end_index = self.text_area.index(f"{start_index} + {len(value)}c")
            
            # Map Pygments tokens to our text box tags
            token_str = str(token_type)
            if "Keyword" in token_str:
                self.text_area.tag_add("keyword", start_index, end_index)
            elif "Name.Builtin" in token_str or "Keyword.Type" in token_str:
                self.text_area.tag_add("type", start_index, end_index)
            elif "Literal.String" in token_str:
                self.text_area.tag_add("string", start_index, end_index)
            elif "Comment" in token_str:
                self.text_area.tag_add("comment", start_index, end_index)
                
            start_index = end_index

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQL Files", "*.sql"), ("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                content = f.read()
            
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", content)
            self.highlight_sql()
            self.set_status(f"Loaded file: {os.path.basename(file_path)}")

    def analyze_ddl(self):
        sql_input = self.text_area.get("1.0", "end").strip()
        if not sql_input:
            messagebox.showwarning("Empty Input", "Please paste a DDL first!")
            return

        try:
            # Phase 1: Parsing using SilverVectorParser
            parser = SilverVectorParser(sql_input)
            tables = parser.parse()
            
            if tables:
                # Clear existing widgets
                for widget in self.preview_scroll.winfo_children():
                    widget.destroy()

                for table in tables:
                    table_name = table['name']
                    
                    # Filter for relevant columns first
                    relevant_cols = [c for c in table['columns'] if c.is_metric or c.is_time_col]
                    
                    # If no relevant columns, skip this table entirely
                    if not relevant_cols:
                        continue
                    
                    # Table Heading
                    heading = ctk.CTkLabel(self.preview_scroll, text=f"\U0001F4C4 {table_name}", 
                                         font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
                    heading.pack(fill="x", pady=(10, 5))

                    # Group columns
                    for col in relevant_cols:
                        icon = "\U0001F4C8" if col.is_metric else "\U0001F550"
                        col_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
                        col_frame.pack(fill="x", pady=2, padx=10)
                        
                        # Checkbox for enabled/disabled
                        chk = ctk.CTkCheckBox(col_frame, text=f"{col.name} ({col.data_type})", 
                                            font=ctk.CTkFont(size=12))
                        chk.select()
                        chk.pack(side="left")
                        
                        # Type Badge
                        badge = ctk.CTkLabel(col_frame, text=icon, width=20)
                        badge.pack(side="right")

                self.set_status("Analysis completed. Config updated.")
            else:
                self.set_status("Error: Could not find a valid CREATE TABLE statement.", is_error=True)
        except Exception as e:
            self.set_status("Error during parsing.", is_error=True)

    def generate_grafana_json(self):
        sql_input = self.text_area.get("1.0", "end").strip()
        if not sql_input:
            messagebox.showwarning("Empty Input", "Please paste a DDL first!")
            return

        # Start Progress
        self.progress_bar.pack(side="left", padx=10, fill="x", expand=True) # Show
        self.progress_bar.start()
        self.update_idletasks() # Force UI update often

        try:
            # 1. Parse Data
            parser = SilverVectorParser(sql_input)
            tables = parser.parse()
            
            if not tables:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.set_status("Error: No valid tables found.", is_error=True)
                return

            # 2. Load Template
            # Locate the template file relative to this script
            base_path = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_path, "templates", "base_dashboard.json")
            
            with open(template_path, 'r') as f:
                dashboard = json.load(f)

            # 3. Generate Panels
            stat_panels = []
            graph_panels = []
            panel_id_counter = 1
            x_pos = 0
            y_pos = 4

            # --- Orchard Core Specific Detection & Panels ---
            # Normalize table names (remove brackets) for detection
            table_names = [t['name'].replace('[', '').replace(']', '') for t in tables]
            is_orchard = "ContentItemIndex" in table_names

            if is_orchard:
                # 1. Content Velocity (Graph)
                # Daily publishing rate
                vel_sql = (
                    "SELECT (unixepoch(PublishedUtc)/86400)*86400 as time, count(*) as value "
                    "FROM ContentItemIndex WHERE Published = 1 "
                    "AND unixepoch(PublishedUtc) BETWEEN $__from/1000 AND $__to/1000 "
                    "GROUP BY 1 ORDER BY 1"
                )
                graph_panels.append(self.create_time_series_panel(
                    "Content Velocity (Items/Day)", vel_sql, panel_id_counter, x_pos, y_pos, "short"
                ))
                panel_id_counter += 1
                x_pos += 12
                if x_pos >= 24: x_pos = 0; y_pos += 8

                # 2. Content Types (Pie)
                type_sql = "SELECT ContentType, count(*) as value FROM ContentItemIndex WHERE Published = 1 GROUP BY 1 ORDER BY 2 DESC"
                graph_panels.append(self.create_pie_chart_panel(
                    "Content Type Distribution", type_sql, panel_id_counter, x_pos, y_pos
                ))
                panel_id_counter += 1
                x_pos += 12
                if x_pos >= 24: x_pos = 0; y_pos += 8
                
                # 3. Recent Activity (Table)
                # Last 10 modifications
                activity_sql = (
                    "SELECT ModifiedUtc, DisplayText, Author, ContentType "
                    "FROM ContentItemIndex "
                    "ORDER BY ModifiedUtc DESC LIMIT 10"
                )
                graph_panels.append(self.create_table_panel(
                    "Recent Content Activity", activity_sql, panel_id_counter, x_pos, y_pos
                ))
                panel_id_counter += 1
                x_pos += 12
                if x_pos >= 24: x_pos = 0; y_pos += 8
                
                # 4. Total Users (Stat) - if UserIndex exists
                if "UserIndex" in table_names:
                    user_sql = "SELECT count(*) as value FROM UserIndex"
                    stat_panels.append(self.create_stat_panel(
                        "Total Users", user_sql, panel_id_counter, x_pos, y_pos, "short"
                    ))
                    panel_id_counter += 1
                    x_pos += 12
                    if x_pos >= 24: x_pos = 0; y_pos += 8

            # --- Generic Panel Generation ---
            for table in tables:
                table_name = table['name']
                t_cols = table['columns']

                # Find the primary time column (heuristic: first one found)
                time_col = next((c for c in t_cols if c.is_time_col), None)
                if not time_col:
                    continue # Skip tables without time dimension for now
                
                # Create a panel for each metric
                metrics = [c for c in t_cols if c.is_metric]
                for metric in metrics:
                    # --- 1. The Financial "Executive" Stat (ONLY for MYR) ---
                    is_money = "myr" in metric.name.lower()
                    unit = "currencyMYR" if is_money else "short"
                    
                    if is_money:
                        stat_sql = (
                            f"SELECT SUM({metric.name}) as value FROM {table_name} "
                            f"WHERE unixepoch(created_at) BETWEEN $__from/1000 AND $__to/1000"
                        )
                        stat = self.create_stat_panel(
                            title=f"Total Revenue ({metric.name})",
                            sql_query=stat_sql,
                            panel_id=panel_id_counter,
                            x_pos=x_pos, 
                            y_pos=y_pos,
                            unit=unit
                        )
                        stat_panels.append(stat)
                        panel_id_counter += 1

                        x_pos += 12
                        if x_pos >= 24:
                            x_pos = 0
                            y_pos += 8

                    # --- 2. The Detailed Trend Graph (FOR ALL METRICS) ---
                    sql_query = (
                        f"SELECT (unixepoch({time_col.name})/3600)*3600 as time, "
                        f"SUM({metric.name}) as value "
                        f"FROM {table_name} "
                        f"WHERE unixepoch({time_col.name}) BETWEEN $__from/1000 AND $__to/1000 "
                        f"GROUP BY 1 ORDER BY 1"
                    )

                    graph = self.create_time_series_panel(
                        title=f"{table_name} - {metric.name} Trend",
                        sql_query=sql_query,
                        panel_id=panel_id_counter,
                        x_pos=x_pos,
                        y_pos=y_pos,
                        unit=unit
                    )
                    graph_panels.append(graph)
                    panel_id_counter += 1

                    # --- 3. Grid Layout Logic for Graphs ---
                    x_pos += 12
                    if x_pos >= 24:
                        x_pos = 0
                        y_pos += 8

                # --- 4. Total Records Stat ---
                count_sql = f"SELECT count(*) as value FROM {table_name}"
                count_stat = self.create_stat_panel(
                    title=f"{table_name} - Total Records",
                    sql_query=count_sql,
                    panel_id=panel_id_counter,
                    x_pos=x_pos,
                    y_pos=y_pos,
                    unit="short"
                )
                stat_panels.append(count_stat)
                panel_id_counter += 1
                
                x_pos += 12
                if x_pos >= 24:
                    x_pos = 0
                    y_pos += 8

                # --- 5. Categorical Pie Charts ---
                categorical_cols = [c for c in t_cols if c.is_categorical]
                for cat_col in categorical_cols:
                    pie_sql = (
                        f"SELECT {cat_col.name}, count(*) as value "
                        f"FROM {table_name} "
                        f"GROUP BY 1 ORDER BY 2 DESC"
                    )
                    pie = self.create_pie_chart_panel(
                        title=f"{table_name} - {cat_col.name} Distribution",
                        sql_query=pie_sql,
                        panel_id=panel_id_counter,
                        x_pos=x_pos,
                        y_pos=y_pos
                    )
                    graph_panels.append(pie)
                    panel_id_counter += 1

                    x_pos += 12
                    if x_pos >= 24:
                        x_pos = 0
                        y_pos += 8

            all_panels = stat_panels + graph_panels
            dashboard["panels"] = all_panels
            dashboard["title"] = "SilverVector Generated Dashboard"
            dashboard["refresh"] = "10s" # Adds auto-refresh
            dashboard["time"] = {"from": "now-30d", "to": "now"} # Default view

            self.progress_bar.stop()
            self.progress_bar.pack_forget() # Hide

            if not graph_panels:
                self.set_status("Warning: No panels were generated.", is_error=True)
                return

            # 4. Display JSON in Tab
            json_str = json.dumps(dashboard, indent=2)
            self.json_area.delete("1.0", "end")
            self.json_area.insert("1.0", json_str)
            self.highlight_json()
            
            # Switch to JSON Tab
            self.editor_tabs.set("Generated JSON")
            self.set_status(f"Generated {len(all_panels)} panels. JSON ready in output tab.")

            # 5. Optional Save (Ask user)
            if messagebox.askyesno("Save to File?", "JSON generated successfully! Do you also want to save it to a .json file?"):
                file_path = filedialog.asksaveasfilename(
                    title="Save Grafana Dashboard",
                    initialfile="silvervector_dashboard.json",
                    defaultextension=".json", 
                    filetypes=[("JSON Files", "*.json")]
                )
                if file_path:
                    with open(file_path, 'w') as f:
                        f.write(json_str)
                    self.set_status(f"Dashboard JSON saved to {os.path.basename(file_path)}")

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.set_status(f"Generation failed: {str(e)}", is_error=True)

    # Helper to update status bar
    def set_status(self, text, is_error=False):
        self.status_label.configure(text=text)
        if is_error:
            self.status_label.configure(text_color="#ff4444")
        else:
            self.status_label.configure(text_color="#0085D0")
        self.update_idletasks()

    # Helper for generating panel JSON
    def create_time_series_panel(self, title, sql_query, panel_id, x_pos, y_pos, unit):
        return {
            "title": title,
            "type": "timeseries",
            "id": panel_id,
            "gridPos": {"h": 8, "w": 12, "x": x_pos, "y": y_pos},
            "datasource": {
                "type": "frser-sqlite-datasource",
                "uid": "${datasource}"
            },
            "targets": [
                {
                    "datasource": {
                        "type": "frser-sqlite-datasource",
                        "uid": "${datasource}"
                    },
                    "format": "table",
                    "queryText": sql_query,
                    "rawQueryText": sql_query,
                    "rawSql": sql_query,
                    "refId": "A",
                    "timeColumns": ["time", "ts"]
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "smooth",
                        "spanNulls": False
                    },
                    "unit": unit
                }
            }
        }
    
    # Helper for generating stat panel JSON
    def create_stat_panel(self, title, sql_query, panel_id, x_pos, y_pos, unit="short"):
        return {
            "title": title,
            "type": "stat",
            "id": panel_id,
            "gridPos": {"h": 8, "w": 12, "x": x_pos, "y": y_pos}, # Shorter and narrower
            "datasource": {
                "type": "frser-sqlite-datasource",
                "uid": "${datasource}"
            },
            "targets": [
                {
                    "datasource": {"type": "frser-sqlite-datasource", "uid": "${datasource}"},
                    "format": "table",
                    "queryText": sql_query,
                    "rawQueryText": sql_query,
                    "rawSql": sql_query,
                    "refId": "A",
                    "timeColumns": ["time", "ts"]
                }
            ],
            "options": {
                "graphMode": "area", # Adds a small sparkline under the number
                "colorMode": "background", # Colors the whole box
                "justifyMode": "center"
            },
            "fieldConfig": {
                "defaults": {
                    "unit": unit,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None}
                        ]
                    }
                }
            }
        }

    # Helper for generating pie chart panel JSON
    def create_pie_chart_panel(self, title, sql_query, panel_id, x_pos, y_pos):
        return {
            "title": title,
            "type": "piechart",
            "id": panel_id,
            "gridPos": {"h": 8, "w": 12, "x": x_pos, "y": y_pos},
            "datasource": {
                "type": "frser-sqlite-datasource",
                "uid": "${datasource}"
            },
            "targets": [
                {
                    "datasource": {"type": "frser-sqlite-datasource", "uid": "${datasource}"},
                    "format": "table",
                    "queryText": sql_query,
                    "rawQueryText": sql_query,
                    "rawSql": sql_query,
                    "refId": "A",
                }
            ],
            "options": {
                "legend": {"displayMode": "list", "placement": "right"},
                "pieType": "donut",
                "reduceOptions": {"values": True, "calcs": ["lastNotNull"], "fields": ""}
            }
        }

    # Helper for generating table panel JSON
    def create_table_panel(self, title, sql_query, panel_id, x_pos, y_pos):
        return {
            "title": title,
            "type": "table",
            "id": panel_id,
            "gridPos": {"h": 8, "w": 12, "x": x_pos, "y": y_pos},
            "datasource": {
                "type": "frser-sqlite-datasource",
                "uid": "${datasource}"
            },
            "targets": [
                {
                    "datasource": {"type": "frser-sqlite-datasource", "uid": "${datasource}"},
                    "format": "table",
                    "queryText": sql_query,
                    "rawQueryText": sql_query,
                    "rawSql": sql_query,
                    "refId": "A",
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "custom": {
                        "align": "auto",
                        "displayMode": "auto",
                        "inspect": False
                    }
                }
            }
        }
if __name__ == "__main__":
    app = SilverVectorApp()
    app.mainloop()
