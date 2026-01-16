-- =============================================================================
-- ProficientHub B2B Migration Script
-- Sistema de Academias, Planes de Exámenes y Mock Exams
-- =============================================================================

-- =============================================================================
-- 1. ACADEMIAS
-- =============================================================================

CREATE TABLE IF NOT EXISTS academies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    
    -- Contact
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    website VARCHAR(500),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Spain',
    timezone VARCHAR(50) DEFAULT 'Europe/Madrid',
    
    -- Subscription
    tier VARCHAR(20) NOT NULL DEFAULT 'starter' CHECK (tier IN ('starter', 'professional', 'enterprise')),
    max_students INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Branding
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#6366F1',
    
    -- Settings (JSON)
    settings JSONB DEFAULT '{}',
    
    -- Owner
    admin_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_academies_slug ON academies(slug);
CREATE INDEX idx_academies_active ON academies(is_active);
CREATE INDEX idx_academies_tier ON academies(tier);

-- =============================================================================
-- 2. PLANES DE EXÁMENES DE ACADEMIAS
-- =============================================================================

CREATE TABLE IF NOT EXISTS academy_exam_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Exam info
    exam_type VARCHAR(100) NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    
    -- Credits
    total_credits INTEGER NOT NULL CHECK (total_credits > 0),
    used_credits INTEGER DEFAULT 0 CHECK (used_credits >= 0),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'expired', 'exhausted', 'cancelled')),
    
    -- Validity
    starts_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Pricing (for records)
    price_paid DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT check_credits_not_exceeded CHECK (used_credits <= total_credits)
);

CREATE INDEX idx_exam_plans_academy ON academy_exam_plans(academy_id);
CREATE INDEX idx_exam_plans_academy_type ON academy_exam_plans(academy_id, exam_type);
CREATE INDEX idx_exam_plans_status ON academy_exam_plans(status);
CREATE INDEX idx_exam_plans_expires ON academy_exam_plans(expires_at);

-- =============================================================================
-- 3. ESTUDIANTES DE ACADEMIAS
-- =============================================================================

CREATE TABLE IF NOT EXISTS academy_students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Student info
    student_code VARCHAR(50),
    group_name VARCHAR(100),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Unique constraint
    CONSTRAINT uq_academy_student UNIQUE (academy_id, user_id)
);

CREATE INDEX idx_academy_students_academy ON academy_students(academy_id);
CREATE INDEX idx_academy_students_user ON academy_students(user_id);
CREATE INDEX idx_academy_students_active ON academy_students(academy_id, is_active);

-- =============================================================================
-- 4. MOCK EXAMS DE ESTUDIANTES
-- =============================================================================

CREATE TABLE IF NOT EXISTS student_mock_exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    student_id UUID NOT NULL REFERENCES academy_students(id) ON DELETE CASCADE,
    exam_plan_id UUID NOT NULL REFERENCES academy_exam_plans(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Exam info
    exam_type VARCHAR(100) NOT NULL,
    exam_number INTEGER NOT NULL CHECK (exam_number > 0),
    
    -- Mode: full_mock = simulacro completo, section = secciones individuales
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('full_mock', 'section')),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'not_started' 
        CHECK (status IN ('not_started', 'in_progress', 'paused', 'completed', 'expired')),
    
    -- Topic
    topic VARCHAR(500),
    
    -- Timing
    total_time_limit_minutes INTEGER DEFAULT 165,
    time_elapsed_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Credits
    credits_used DECIMAL(4, 2) DEFAULT 0.00,
    
    -- Results
    overall_band VARCHAR(10),
    overall_percentage DECIMAL(5, 2),
    section_results JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Unique constraint: student can only have one exam #1, one exam #2, etc. per plan
    CONSTRAINT uq_student_exam_number UNIQUE (student_id, exam_plan_id, exam_number)
);

CREATE INDEX idx_mock_exams_student ON student_mock_exams(student_id);
CREATE INDEX idx_mock_exams_student_status ON student_mock_exams(student_id, status);
CREATE INDEX idx_mock_exams_plan ON student_mock_exams(exam_plan_id);
CREATE INDEX idx_mock_exams_user ON student_mock_exams(user_id);

-- =============================================================================
-- 5. SECCIONES DE MOCK EXAMS
-- =============================================================================

CREATE TABLE IF NOT EXISTS mock_exam_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mock_exam_id UUID NOT NULL REFERENCES student_mock_exams(id) ON DELETE CASCADE,
    
    -- Section info
    section_type VARCHAR(50) NOT NULL CHECK (section_type IN ('reading', 'writing', 'listening', 'speaking')),
    section_order INTEGER NOT NULL CHECK (section_order BETWEEN 1 AND 4),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'locked' 
        CHECK (status IN ('locked', 'available', 'in_progress', 'completed', 'skipped')),
    
    -- Timing
    time_limit_minutes INTEGER NOT NULL,
    time_elapsed_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Link to generated exam content
    exam_session_id UUID REFERENCES exam_sessions(id) ON DELETE SET NULL,
    
    -- Results
    raw_score DECIMAL(6, 2),
    max_score DECIMAL(6, 2),
    percentage_score DECIMAL(5, 2),
    band_score VARCHAR(10),
    
    -- Feedback
    feedback JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Unique constraint
    CONSTRAINT uq_mock_section_type UNIQUE (mock_exam_id, section_type)
);

CREATE INDEX idx_sections_mock ON mock_exam_sections(mock_exam_id);
CREATE INDEX idx_sections_mock_order ON mock_exam_sections(mock_exam_id, section_order);
CREATE INDEX idx_sections_status ON mock_exam_sections(status);

-- =============================================================================
-- 6. FUNCIONES DE UTILIDAD
-- =============================================================================

-- Función para actualizar timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para auto-update de updated_at
CREATE TRIGGER update_academies_updated_at
    BEFORE UPDATE ON academies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_academy_exam_plans_updated_at
    BEFORE UPDATE ON academy_exam_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_academy_students_updated_at
    BEFORE UPDATE ON academy_students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_mock_exams_updated_at
    BEFORE UPDATE ON student_mock_exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mock_exam_sections_updated_at
    BEFORE UPDATE ON mock_exam_sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 7. DATOS DE EJEMPLO
-- =============================================================================

-- Insertar academia de ejemplo
INSERT INTO academies (id, name, slug, email, city, country, tier, max_students)
VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'English Excellence Academy',
    'english-excellence',
    'info@englishexcellence.com',
    'Madrid',
    'Spain',
    'professional',
    200
);

-- Insertar plan de exámenes de ejemplo (5 IELTS Academic)
INSERT INTO academy_exam_plans (id, academy_id, exam_type, plan_name, total_credits, expires_at)
VALUES (
    'b2c3d4e5-f6a7-8901-bcde-f12345678901',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'ielts_academic',
    'IELTS Academic - 5 Exams Pack',
    5,
    NOW() + INTERVAL '6 months'
);

-- =============================================================================
-- 8. VISTA PARA DASHBOARD DE ACADEMIA
-- =============================================================================

CREATE OR REPLACE VIEW academy_dashboard_stats AS
SELECT 
    a.id AS academy_id,
    a.name AS academy_name,
    a.tier,
    COUNT(DISTINCT s.id) AS total_students,
    COUNT(DISTINCT s.id) FILTER (WHERE s.is_active) AS active_students,
    COUNT(DISTINCT ep.id) AS total_plans,
    SUM(ep.total_credits) AS total_credits_purchased,
    SUM(ep.used_credits) AS total_credits_used,
    SUM(ep.total_credits - ep.used_credits) AS total_credits_remaining,
    COUNT(DISTINCT me.id) AS total_mock_exams,
    COUNT(DISTINCT me.id) FILTER (WHERE me.status = 'completed') AS completed_mock_exams,
    AVG(me.overall_percentage) FILTER (WHERE me.status = 'completed') AS avg_score
FROM academies a
LEFT JOIN academy_students s ON a.id = s.academy_id
LEFT JOIN academy_exam_plans ep ON a.id = ep.academy_id
LEFT JOIN student_mock_exams me ON ep.id = me.exam_plan_id
WHERE a.is_deleted = FALSE
GROUP BY a.id, a.name, a.tier;

-- =============================================================================
-- 9. DOCUMENTACIÓN
-- =============================================================================

COMMENT ON TABLE academies IS 'Academias/instituciones que compran planes de exámenes';
COMMENT ON TABLE academy_exam_plans IS 'Planes de exámenes comprados por academias. Cada plan tiene X créditos.';
COMMENT ON TABLE academy_students IS 'Relación entre usuarios y academias como estudiantes';
COMMENT ON TABLE student_mock_exams IS 'Simulacros de examen de estudiantes. Pueden ser FULL_MOCK o SECTION mode.';
COMMENT ON TABLE mock_exam_sections IS 'Secciones individuales dentro de un mock exam';

COMMENT ON COLUMN student_mock_exams.mode IS 'full_mock: 4 secciones secuenciales (1 crédito). section: secciones individuales (0.25 créditos cada una)';
COMMENT ON COLUMN student_mock_exams.credits_used IS 'Créditos consumidos. full_mock=1.0, section=0.25 por sección completada';
COMMENT ON COLUMN mock_exam_sections.status IS 'locked: no disponible aún. available: lista para empezar. in_progress: en curso. completed: terminada.';
