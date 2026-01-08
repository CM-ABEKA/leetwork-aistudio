-- AI Model Studio Platform - Seed Data
-- Description: Sample data for development and testing

-- ============================================
-- SAMPLE USERS
-- ============================================

-- Note: All passwords are 'password123' (hashed with bcrypt)
-- In production, users should change these immediately!

INSERT INTO users (email, password_hash, full_name, role, is_active) VALUES
    ('demo@mlplatform.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5esiWg7vDJU.u', 'Demo User', 'user', true),
    ('data.analyst@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5esiWg7vDJU.u', 'Dana Analyst', 'user', true),
    ('ml.engineer@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5esiWg7vDJU.u', 'Mike Engineer', 'user', true)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- SAMPLE PROJECTS
-- ============================================

DO $$
DECLARE
    demo_user_id UUID;
    analyst_user_id UUID;
    engineer_user_id UUID;
    project1_id UUID;
    project2_id UUID;
    project3_id UUID;
BEGIN
    -- Get user IDs
    SELECT id INTO demo_user_id FROM users WHERE email = 'demo@mlplatform.local';
    SELECT id INTO analyst_user_id FROM users WHERE email = 'data.analyst@company.com';
    SELECT id INTO engineer_user_id FROM users WHERE email = 'ml.engineer@company.com';

    -- Create sample projects
    INSERT INTO projects (id, user_id, name, description, domain, task_type, status)
    VALUES
        (gen_random_uuid(), demo_user_id, 'Customer Churn Prediction', 'Predict which customers are likely to churn based on usage patterns', 'ml', 'classification', 'active'),
        (gen_random_uuid(), analyst_user_id, 'Sentiment Analysis', 'Analyze customer feedback sentiment', 'nlp', 'text_classification', 'active'),
        (gen_random_uuid(), engineer_user_id, 'Image Classification', 'Classify product images into categories', 'vision', 'image_classification', 'active')
    RETURNING id INTO project1_id;

    RAISE NOTICE 'Sample projects created successfully!';
END $$;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Seed data loaded successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sample Users:';
    RAISE NOTICE '  - admin@mlplatform.local (admin) - password: admin123';
    RAISE NOTICE '  - demo@mlplatform.local (user) - password: password123';
    RAISE NOTICE '  - data.analyst@company.com (user) - password: password123';
    RAISE NOTICE '  - ml.engineer@company.com (user) - password: password123';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT: Change all default passwords in production!';
    RAISE NOTICE '========================================';
END $$;
