---

#### `build/sql-migrations.md`

````markdown
# SQL Migration Scripts

## Migration 001: Initial Schema

Run this first to set up the database.

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator' CHECK (role IN ('admin', 'operator', 'supervisor', 'counsellor')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Cases
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(20) UNIQUE,
    status VARCHAR(20) DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    ai_flags JSONB DEFAULT '{}',
    transcript TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
````

Migration 002: Add Safety Profile

Adds the multidimensional profile column.

ALTER TABLE cases ADD COLUMN victim_safety_profile JSONB DEFAULT '{}';
-- Example data insertion for testing
INSERT INTO cases (case_number, victim_safety_profile) VALUES
('SAH-TEST-001', '{
"psych_distress": {"level": "HIGH", "confidence": 0.8},
"immediate_danger": {"level": "NONE", "confidence": 0.9}
}');
