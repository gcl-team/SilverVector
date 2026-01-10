-- 1. Registered Customers (The 'Who')
CREATE TABLE RegisteredCustomers (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    region VARCHAR(50), -- Categorical Label for Dropdowns
    signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Time-Series
);

-- 2. Online Transactions (The 'Wealth')
CREATE TABLE OnlineTransactions (
    transaction_id INT PRIMARY KEY,
    customer_id INT, -- Potential Join Key
    amount_myr DECIMAL(10, 2), -- Metric
    payment_status VARCHAR(20), -- Categorical (Success/Fail)
    created_at DATETIME, -- Time-Series
    FOREIGN KEY (customer_id) REFERENCES RegisteredCustomers(customer_id)
);

-- 3. Application Logs (The 'Health')
CREATE TABLE SystemLogs (
    log_id BIGINT PRIMARY KEY,
    endpoint VARCHAR(255),
    response_code INT, -- Metric (e.g., 500 = Error)
    latency_ms INT, -- Metric
    error_message TEXT,
    log_time TIMESTAMP -- Time-Series
);