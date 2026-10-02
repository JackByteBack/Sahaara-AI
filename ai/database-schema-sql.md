---

#### `ai/database-schema-sql.md`

```markdown
# SQL Database Schemas

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
username VARCHAR(50) NOT NULL UNIQUE,
password_hash VARCHAR(255) NOT NULL,
role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'operator', 'supervisor', 'counsellor')),
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. CASES TABLE
CREATE TABLE IF NOT EXISTS cases (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
case_number VARCHAR(20) UNIQUE,
status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'reviewing', 'referred', 'closed')),
created_by UUID REFERENCES users(id),
review_priority_score FLOAT DEFAULT 0.0,
victim_safety_profile JSONB, -- Stores Feature 2.2 data
ai_flags JSONB, -- Stores Feature 1.5 data
transcript TEXT,
summary TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. REFERRALS TABLE
CREATE TABLE IF NOT EXISTS referrals (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
referral_type VARCHAR(50), -- 'medical', 'legal', 'police'
status VARCHAR(20) DEFAULT 'pending',
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
case_id UUID REFERENCES cases(id),
user_id UUID REFERENCES users(id),
action VARCHAR(50) NOT NULL, -- 'created', 'reviewed', 'flag_modified'
details TEXT,
timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_audit_logs_case ON audit_logs(case_id);
```
