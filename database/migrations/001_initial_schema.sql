-- AI Model Studio Platform - Initial Database Schema
-- Version: 1.0.0
-- Description: Creates all core tables for the ML platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'enterprise')),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ============================================
-- PROJECTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(50) NOT NULL CHECK (domain IN ('ml', 'nlp', 'vision', 'timeseries', 'audio', 'rl', 'graph', 'robotics', 'genai', 'synthetic', 'mlops', 'edge', 'governance')),
    task_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    CONSTRAINT unique_user_project UNIQUE(user_id, name)
);

-- ============================================
-- DATASETS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT CHECK (file_size >= 0),
    file_type VARCHAR(50) CHECK (file_type IN ('csv', 'json', 'jsonl', 'parquet', 'xlsx', 'txt', 'pdf', 'jpg', 'png', 'wav', 'mp3', 'other')),
    num_rows INTEGER CHECK (num_rows >= 0),
    num_columns INTEGER CHECK (num_columns >= 0),
    schema_json JSONB,
    health_report JSONB,
    is_cleaned BOOLEAN DEFAULT FALSE,
    cleaned_dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- TRAINING JOBS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    hyperparameters JSONB,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'queued', 'running', 'completed', 'failed', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    celery_task_id VARCHAR(255) UNIQUE,
    logs_path VARCHAR(500),
    resource_usage JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_timestamps CHECK (completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at)
);

-- ============================================
-- MODEL ARTIFACTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS model_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    training_job_id UUID REFERENCES training_jobs(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    model_path VARCHAR(500) NOT NULL,
    model_type VARCHAR(100) CHECK (model_type IN ('sklearn', 'pytorch', 'tensorflow', 'onnx', 'huggingface', 'other')),
    model_size BIGINT CHECK (model_size >= 0),
    metrics JSONB,
    feature_columns JSONB,
    target_column VARCHAR(255),
    preprocessing_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deployed BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0 CHECK (download_count >= 0)
);

-- ============================================
-- EVALUATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_artifact_id UUID NOT NULL REFERENCES model_artifacts(id) ON DELETE CASCADE,
    test_dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    metrics JSONB NOT NULL,
    confusion_matrix JSONB,
    roc_curve_data JSONB,
    feature_importance JSONB,
    evaluation_type VARCHAR(50) DEFAULT 'validation' CHECK (evaluation_type IN ('validation', 'test', 'production', 'cross_validation')),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PREDICTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_artifact_id UUID NOT NULL REFERENCES model_artifacts(id) ON DELETE CASCADE,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    latency_ms INTEGER CHECK (latency_ms >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODEL REGISTRY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_artifact_id UUID NOT NULL REFERENCES model_artifacts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags VARCHAR(100)[],
    is_public BOOLEAN DEFAULT FALSE,
    star_count INTEGER DEFAULT 0 CHECK (star_count >= 0),
    fork_count INTEGER DEFAULT 0 CHECK (fork_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_registry_name UNIQUE(user_id, name)
);

-- ============================================
-- AUDIT LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    metadata JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_domain ON projects(domain);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);

-- Datasets indexes
CREATE INDEX IF NOT EXISTS idx_datasets_project_id ON datasets(project_id);
CREATE INDEX IF NOT EXISTS idx_datasets_uploaded_by ON datasets(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_datasets_is_cleaned ON datasets(is_cleaned);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON datasets(created_at DESC);

-- Training jobs indexes
CREATE INDEX IF NOT EXISTS idx_training_jobs_project_id ON training_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_training_jobs_dataset_id ON training_jobs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status);
CREATE INDEX IF NOT EXISTS idx_training_jobs_celery_task_id ON training_jobs(celery_task_id);
CREATE INDEX IF NOT EXISTS idx_training_jobs_created_at ON training_jobs(created_at DESC);

-- Model artifacts indexes
CREATE INDEX IF NOT EXISTS idx_model_artifacts_project_id ON model_artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_model_artifacts_training_job ON model_artifacts(training_job_id);
CREATE INDEX IF NOT EXISTS idx_model_artifacts_is_deployed ON model_artifacts(is_deployed);
CREATE INDEX IF NOT EXISTS idx_model_artifacts_created_at ON model_artifacts(created_at DESC);

-- Evaluations indexes
CREATE INDEX IF NOT EXISTS idx_evaluations_model_artifact_id ON evaluations(model_artifact_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluation_type ON evaluations(evaluation_type);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluated_at ON evaluations(evaluated_at DESC);

-- Predictions indexes
CREATE INDEX IF NOT EXISTS idx_predictions_model_artifact_id ON predictions(model_artifact_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);

-- Model registry indexes
CREATE INDEX IF NOT EXISTS idx_model_registry_user_id ON model_registry(user_id);
CREATE INDEX IF NOT EXISTS idx_model_registry_model_artifact_id ON model_registry(model_artifact_id);
CREATE INDEX IF NOT EXISTS idx_model_registry_is_public ON model_registry(is_public);
CREATE INDEX IF NOT EXISTS idx_model_registry_created_at ON model_registry(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_registry_tags ON model_registry USING GIN(tags);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- ============================================
-- TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View for project statistics
CREATE OR REPLACE VIEW project_statistics AS
SELECT
    p.id as project_id,
    p.name as project_name,
    p.user_id,
    COUNT(DISTINCT d.id) as dataset_count,
    COUNT(DISTINCT tj.id) as training_job_count,
    COUNT(DISTINCT ma.id) as model_count,
    COUNT(DISTINCT CASE WHEN tj.status = 'completed' THEN tj.id END) as completed_jobs,
    COUNT(DISTINCT CASE WHEN tj.status = 'running' THEN tj.id END) as running_jobs,
    COUNT(DISTINCT CASE WHEN tj.status = 'failed' THEN tj.id END) as failed_jobs,
    MAX(tj.created_at) as last_training_at
FROM projects p
LEFT JOIN datasets d ON d.project_id = p.id
LEFT JOIN training_jobs tj ON tj.project_id = p.id
LEFT JOIN model_artifacts ma ON ma.project_id = p.id
GROUP BY p.id, p.name, p.user_id;

-- View for user statistics
CREATE OR REPLACE VIEW user_statistics AS
SELECT
    u.id as user_id,
    u.email,
    u.full_name,
    COUNT(DISTINCT p.id) as project_count,
    COUNT(DISTINCT ma.id) as model_count,
    SUM(ma.download_count) as total_downloads,
    COUNT(DISTINCT mr.id) as published_models,
    MAX(p.created_at) as last_project_created_at
FROM users u
LEFT JOIN projects p ON p.user_id = u.id
LEFT JOIN model_artifacts ma ON ma.project_id = p.id
LEFT JOIN model_registry mr ON mr.user_id = u.id
GROUP BY u.id, u.email, u.full_name;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

-- Grant all privileges to the mlplatform user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mlplatform;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mlplatform;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mlplatform;

-- ============================================
-- INITIAL DATA (Optional)
-- ============================================

-- Create a default admin user (password: admin123 - change in production!)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (email, password_hash, full_name, role, is_active)
VALUES (
    'admin@mlplatform.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5esiWg7vDJU.u',
    'System Administrator',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Database schema initialized successfully!';
    RAISE NOTICE 'Tables created: users, projects, datasets, training_jobs, model_artifacts, evaluations, predictions, model_registry, audit_logs';
    RAISE NOTICE 'Views created: project_statistics, user_statistics';
    RAISE NOTICE 'Default admin user: admin@mlplatform.local (password: admin123)';
END $$;
