import sqlite3
from datetime import datetime, timedelta
import random
import os

def init_db():
    # Ensure the directory exists
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    db_path = os.path.join(os.path.dirname(__file__), 'silvervector_demo.db')
    
    print(f"Initializing database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Run the DDL (Matches ecommerce.sql)
    # Note: SQLite types are slightly different but it accepts most SQL standard types as affinities
    print("Creating tables...")
    cursor.executescript("""
    DROP TABLE IF EXISTS RegisteredCustomers;
    DROP TABLE IF EXISTS OnlineTransactions;
    DROP TABLE IF EXISTS SystemLogs;

    -- 1. Registered Customers
    CREATE TABLE RegisteredCustomers (
        customer_id INTEGER PRIMARY KEY,
        full_name VARCHAR(255),
        email VARCHAR(100) UNIQUE,
        region VARCHAR(50),
        signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. Online Transactions
    CREATE TABLE OnlineTransactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INT,
        amount_myr DECIMAL(10, 2),
        payment_status VARCHAR(20),
        created_at DATETIME,
        FOREIGN KEY (customer_id) REFERENCES RegisteredCustomers(customer_id)
    );

    -- 3. Application Logs
    CREATE TABLE SystemLogs (
        log_id INTEGER PRIMARY KEY,
        endpoint VARCHAR(255),
        response_code INT,
        latency_ms INT,
        error_message TEXT,
        log_time TIMESTAMP
    );
    """)

    # 2. Seed with dummy data
    print("Seeding data...")
    
    # --- Seed Customers ---
    regions = ['North', 'South', 'East', 'West', 'Central', 'Singapore', 'Johor']
    first_names = ['Ali', 'Siti', 'Chong', 'Muthu', 'David', 'Sarah', 'Jessica', 'Ahmad', 'Wei', 'Ravi']
    last_names = ['Tan', 'Lim', 'Wong', 'Singh', 'Abdullah', 'Lee', 'Goh', 'Fernandez', 'Liew']
    
    customers = []
    for i in range(1, 51): # 50 Customers
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"user{i}@example.com"
        region = random.choice(regions)
        # Random signup in last 60 days
        days_ago = random.randint(1, 60)
        signup_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        customers.append((i, name, email, region, signup_date))
    
    cursor.executemany("INSERT INTO RegisteredCustomers VALUES (?, ?, ?, ?, ?)", customers)
    print(f"Inserted {len(customers)} customers.")

    # --- Seed Transactions ---
    statuses = ['Success'] * 80 + ['Failed'] * 15 + ['Pending'] * 5 # Weighted probability
    transactions = []
    for i in range(1, 201): # 200 Transactions
        cust_id = random.randint(1, 50)
        amount = round(random.uniform(10.0, 500.0), 2)
        status = random.choice(statuses)
        # Time distribution: uniform over last 30 days
        days_ago = random.uniform(0, 30)
        created_at = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        transactions.append((i, cust_id, amount, status, created_at))

    cursor.executemany("INSERT INTO OnlineTransactions VALUES (?, ?, ?, ?, ?)", transactions)
    print(f"Inserted {len(transactions)} transactions.")

    # --- Seed System Logs ---
    endpoints = ['/api/login', '/api/checkout', '/api/search', '/api/cart/add', '/home']
    status_codes = [200, 200, 200, 200, 201, 301, 400, 403, 404, 500]
    logs = []
    
    for i in range(1, 301): # 300 Logs
        endpoint = random.choice(endpoints)
        code = random.choice(status_codes)
        
        # Correlate latency and errors with status codes roughly
        if code == 500:
            latency = random.randint(500, 2000)
            msg = "Internal Server Error: Database timeout"
        elif code >= 400:
            latency = random.randint(50, 200)
            msg = "Client Error: Bad Request"
        else:
            latency = random.randint(20, 150)
            msg = None
            
        # Time distribution: heavily weighted towards "now" to simulate recent traffic
        minutes_ago = random.randint(0, 60 * 24 * 7) # Last 7 days
        log_time = (datetime.now() - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        logs.append((i, endpoint, code, latency, msg, log_time))

    cursor.executemany("INSERT INTO SystemLogs VALUES (?, ?, ?, ?, ?, ?)", logs)
    print(f"Inserted {len(logs)} logs.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
