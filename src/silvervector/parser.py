from simple_ddl_parser import DDLParser
from pydantic import BaseModel
from typing import List, Optional

class ColumnModel(BaseModel):
    name: str
    data_type: str
    is_time_col: bool = False
    is_metric: bool = False
    is_label: bool = False
    is_categorical: bool = False
    unit: str = "short"

class SilverVectorParser:
    def __init__(self, ddl_text: str):
        self.ddl_text = ddl_text
        self.tables = []

    def parse(self):
        # 1. Run the raw parser
        parser = DDLParser(self.ddl_text)
        raw_results = parser.run(group_by_type=True)

        # 2. Refine the results with SilverVector Logic
        for table in raw_results.get("tables", []):
            refined_cols = []
            for col in table["columns"]:
                refined_cols.append(self._classify_column(col))
            
            self.tables.append({
                "name": table["table_name"],
                "columns": refined_cols
            })
        return self.tables

    def _classify_column(self, col):
        name = col["name"].lower()
        ctype = col["type"].lower()
        unit = "short"
        
        # Defensive: Strip explicit "default" if parser leaks it into type
        if "default" in ctype:
            ctype = ctype.split("default")[0].strip()
        
        # 🕵️ Time/Latency Clues
        if any(k in name for k in ["latency", "duration", "delay"]):
            unit = "ms" if "ms" in name or "milli" in name else "s"
        
        # 💰 Currency Clues
        elif any(k in name for k in ["amount", "price", "revenue", "cost"]):
            unit = "currencyMYR"
            
        # 📈 Percentage Clues
        elif "percent" in name or "pct" in name:
            unit = "percent"

        # Logic: Identify Time columns
        # Refined heuristic: prevent "status" or "latency" matching "at"
        # Also handles "TIMESTAMP DEFAULT CURRENT_TIMESTAMP" safely via ctype check
        is_time = any(word in name for word in ["time", "date"]) or \
                  name == "at" or "_at" in name or name.endswith("at") or \
                  "date" in ctype or "time" in ctype or "timestamp" in ctype or "datetime" in ctype
        
        # Logic: Identify Metrics (Numbers that aren't IDs)
        is_metric = ("int" in ctype or "decimal" in ctype or "float" in ctype) and "id" not in name
        
        # Logic: Identify Labels (Dimensions to group by)
        is_label = (
            "varchar" in ctype or 
            "text" in ctype or 
            "status" in name or 
            "id" in name
        )

        # Logic: Identify Categorical (Good for Pie Charts/Stat Grouping)
        is_categorical = (
            "status" in name or 
            "state" in name or 
            "type" in name or 
            "category" in name or
            "level" in name or
            "priority" in name or
            "severity" in name or
            "version" in name or
            "source" in name or
            "target" in name or
            "method" in name or
            "mode" in name
        )

        return ColumnModel(
            name=col["name"],
            data_type=ctype,
            is_time_col=is_time,
            is_metric=is_metric,
            is_label=is_label,
            is_categorical=is_categorical,
            unit=unit
        )