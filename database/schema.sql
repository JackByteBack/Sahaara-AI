-- Sahaara AI — PostgreSQL schema (reference for production deployments)
-- Source: ai/database-schema-sql.md + build/tech-specs.md §2
-- The backend also bootstraps schema automatically via SQLAlchemy (SQLite/Postgres).

-- 1. USERS TABLE (Feature 1.11 roles)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) DEFAULT '',
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'operator', 'supervisor', 'counsellor')),
    language VARCHAR(8) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. CASES TABLE (Features 1.4, 1.5, 1.6, 1.7, 2.2)
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(20) UNIQUE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'reviewing', 'referred', 'closed')),
    created_by UUID REFERENCES users(id),
    review_priority_score FLOAT DEFAULT 0.0,
    safety_override BOOLEAN DEFAULT FALSE,
    safety_override_reason TEXT DEFAULT '',
    victim_safety_profile JSONB,   -- Feature 2.2 multidimensional profile
    ai_flags JSONB,                -- Feature 1.5 explainable indicators
    uncertainty JSONB,             -- Feature 2.10 uncertainty-aware assessment
    language_info JSONB,           -- Features 1.3 / 2.9
    transcript JSONB,              -- segments with timestamps
    summary JSONB,                 -- Feature 1.9 (ai vs fallback labeled)
    final_decision JSONB,          -- Feature 1.6 human decision
    consent JSONB,                 -- Feature 1.7 / 1.10 consent-first
    notes JSONB DEFAULT '[]',
    followups JSONB DEFAULT '[]',  -- Feature 2.17 longitudinal
    session_mode VARCHAR(20) DEFAULT 'text',
    trauma_mode BOOLEAN DEFAULT FALSE,      -- Feature 2.13
    is_demo BOOLEAN DEFAULT FALSE,          -- Feature 1.15
    anonymized BOOLEAN DEFAULT FALSE,       -- Feature 1.10
    assessment_confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. REFERRALS TABLE (Features 1.8 / 2.16)
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    referral_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    ai_suggested BOOLEAN DEFAULT FALSE,
    notes TEXT DEFAULT '',
    created_by UUID REFERENCES users(id),
    confirmed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. AUDIT LOGS TABLE (Feature 1.13)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,   -- login, created, reviewed, escalated, referral, export, deleted, ...
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. RATE LIMITS (session start throttling)
CREATE TABLE IF NOT EXISTS rate_limits (
    id VARCHAR(64) PRIMARY KEY,
    count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_priority ON cases(review_priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_case ON audit_logs(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ts ON audit_logs(timestamp DESC);
