import sqlite3
import random
import datetime
import uuid
import os

# Configuration
DB_PATH = "demo_orchard.db"
DAYS_OF_HISTORY = 30
NUM_USERS = 45
NUM_CONTENT_ITEMS = 350

# Data Pools
CONTENT_TYPES = ["Article", "BlogPost", "Product", "Event", "Page"]
AUTHORS = ["admin", "editor_sarah", "writer_john", "marketing_team", "guest_contributor"]
TITLES = [
    "Q1 Roadmap", "New Feature Release", "Summer Sale", "Team Outing", "Privacy Policy Update",
    "How to use SilverVector", "Grafana Tips", "Orchard Core Deep Dive", "Cloud Migration Strategy",
    "Customer Success Story", "Weekly Update", "Maintenance Window", "API Documentation"
]

def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read the DDL from the existing file
    # Assuming we are running from src/silvervector/examples/orchard-core/
    ddl_path = os.path.join("orchard-data", "orchardcore_ddl.sql")
    
    if not os.path.exists(ddl_path):
        print(f"Error: Could not find DDL at {ddl_path}")
        return None

    with open(ddl_path, 'r') as f:
        ddl_script = f.read()
        
    # Execute DDL (Skip sqlite_sequence as it is internal)
    clean_ddl = "\n".join([line for line in ddl_script.splitlines() if "sqlite_sequence" not in line])
    cursor.executescript(clean_ddl)
    conn.commit()
    print(f"Created fresh database at {DB_PATH}")
    return conn

def generate_data(conn):
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    print("Generating Users...")
    # 1. Generate Users
    for i in range(NUM_USERS):
        user_id = str(uuid.uuid4())
        username = f"user_{i}"
        email = f"user_{i}@example.com"
        is_enabled = 1
        
        cursor.execute("""
            INSERT INTO UserIndex (DocumentId, UserId, NormalizedUserName, NormalizedEmail, IsEnabled)
            VALUES (?, ?, ?, ?, ?)
        """, (i, user_id, username.upper(), email.upper(), is_enabled))

    print("Generating Content...")
    # 2. Generate Content Items
    for i in range(NUM_CONTENT_ITEMS):
        # Random timestamp within last 30 days
        days_ago = random.randint(0, DAYS_OF_HISTORY)
        seconds_ago = random.randint(0, 86400)
        created_date = now - datetime.timedelta(days=days_ago, seconds=seconds_ago)
        
        # Published shortly after creation
        published_date = created_date + datetime.timedelta(minutes=random.randint(10, 300))
        modified_date = published_date # Initially same
        
        # Random attributes
        ctype = random.choice(CONTENT_TYPES)
        author = random.choice(AUTHORS)
        title = f"{random.choice(TITLES)} - {i}"
        
        # Insert
        cursor.execute("""
            INSERT INTO ContentItemIndex 
            (DocumentId, ContentItemId, ContentType, DisplayText, Author, Owner, CreatedUtc, PublishedUtc, ModifiedUtc, Published, Latest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        """, (
            i + 1000, # Offset DocumentId
            str(uuid.uuid4()),
            ctype,
            title,
            author,
            author,
            created_date.strftime("%Y-%m-%d %H:%M:%S"),
            published_date.strftime("%Y-%m-%d %H:%M:%S"),
            modified_date.strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    print(f"Successfully injected {NUM_USERS} users and {NUM_CONTENT_ITEMS} content items.")

if __name__ == "__main__":
    conn = create_db()
    if conn:
        generate_data(conn)
        conn.close()
