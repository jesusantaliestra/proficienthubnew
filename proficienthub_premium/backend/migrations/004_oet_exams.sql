-- =============================================================================
-- ProficientHub - OET Exam System Migration
-- Creates tables for OET exam generation, storage, and evaluation
-- =============================================================================

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- ENUM TYPES
-- =============================================================================

-- OET Professions
DO $$ BEGIN
    CREATE TYPE oet_profession AS ENUM (
        'medicine',
        'nursing',
        'dentistry',
        'pharmacy',
        'physiotherapy',
        'radiography',
        'occupational_therapy',
        'dietetics',
        'podiatry',
        'speech_pathology',
        'optometry',
        'veterinary_science'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- OET Sections
DO $$ BEGIN
    CREATE TYPE oet_section AS ENUM (
        'listening',
        'reading',
        'writing',
        'speaking'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- OET Grades
DO $$ BEGIN
    CREATE TYPE oet_grade AS ENUM (
        'A',
        'B',
        'C+',
        'C',
        'D',
        'E'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Exam Status
DO $$ BEGIN
    CREATE TYPE oet_exam_status AS ENUM (
        'created',
        'in_progress',
        'completed',
        'expired',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =============================================================================
-- OET EXAMS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS oet_exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mock_exam_section_id UUID REFERENCES mock_exam_sections(id) ON DELETE SET NULL,

    -- Exam details
    profession oet_profession NOT NULL,
    section oet_section NOT NULL,

    -- Content (JSONB for flexible storage)
    content JSONB NOT NULL DEFAULT '{}',

    -- User answers
    answers JSONB NOT NULL DEFAULT '{}',

    -- Results
    raw_score INTEGER,
    max_score INTEGER,
    scaled_score INTEGER,  -- 0-500
    grade VARCHAR(10),

    -- Detailed results and feedback
    detailed_results JSONB NOT NULL DEFAULT '{}',
    feedback JSONB NOT NULL DEFAULT '{}',

    -- Timing
    time_limit_seconds INTEGER NOT NULL,
    time_elapsed_seconds INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Status
    status VARCHAR(50) DEFAULT 'created'
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_oet_exams_user_id ON oet_exams(user_id);
CREATE INDEX IF NOT EXISTS idx_oet_exams_user_section ON oet_exams(user_id, section);
CREATE INDEX IF NOT EXISTS idx_oet_exams_status ON oet_exams(status);
CREATE INDEX IF NOT EXISTS idx_oet_exams_profession ON oet_exams(profession);
CREATE INDEX IF NOT EXISTS idx_oet_exams_created_at ON oet_exams(created_at DESC);

-- =============================================================================
-- OET CONTENT ITEMS TABLE (Reusable content bank)
-- =============================================================================

CREATE TABLE IF NOT EXISTS oet_content_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Classification
    section oet_section NOT NULL,
    content_type VARCHAR(50) NOT NULL,  -- question, passage, task, roleplay
    profession oet_profession NOT NULL,

    -- Content data
    content JSONB NOT NULL,

    -- Metadata
    difficulty_level INTEGER DEFAULT 3 CHECK (difficulty_level BETWEEN 1 AND 5),
    medical_specialty VARCHAR(100),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    average_score FLOAT,

    -- Quality control
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_oet_content_section_type ON oet_content_items(section, content_type);
CREATE INDEX IF NOT EXISTS idx_oet_content_profession ON oet_content_items(profession);
CREATE INDEX IF NOT EXISTS idx_oet_content_active ON oet_content_items(is_active);
CREATE INDEX IF NOT EXISTS idx_oet_content_difficulty ON oet_content_items(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_oet_content_tags ON oet_content_items USING GIN(tags);

-- =============================================================================
-- OET AUDIO CONTENT TABLE (Listening section audio)
-- =============================================================================

CREATE TABLE IF NOT EXISTS oet_audio_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Classification
    part VARCHAR(20) NOT NULL,  -- part_a, part_b, part_c
    profession oet_profession NOT NULL,

    -- Audio file
    audio_url VARCHAR(500) NOT NULL,
    duration_seconds INTEGER NOT NULL,

    -- Transcript
    transcript TEXT NOT NULL,
    speaker_labels JSONB DEFAULT '{}',

    -- Metadata
    title VARCHAR(255) NOT NULL,
    description TEXT,
    medical_scenario VARCHAR(255) NOT NULL,

    -- Quality
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_oet_audio_part_profession ON oet_audio_content(part, profession);
CREATE INDEX IF NOT EXISTS idx_oet_audio_active ON oet_audio_content(is_active);

-- =============================================================================
-- OET USER PROGRESS TABLE (Track user's OET journey)
-- =============================================================================

CREATE TABLE IF NOT EXISTS oet_user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profession oet_profession NOT NULL,

    -- Section progress
    listening_attempts INTEGER DEFAULT 0,
    listening_best_grade VARCHAR(10),
    listening_best_score INTEGER,
    listening_avg_score FLOAT,

    reading_attempts INTEGER DEFAULT 0,
    reading_best_grade VARCHAR(10),
    reading_best_score INTEGER,
    reading_avg_score FLOAT,

    writing_attempts INTEGER DEFAULT 0,
    writing_best_grade VARCHAR(10),
    writing_best_score INTEGER,
    writing_avg_score FLOAT,

    speaking_attempts INTEGER DEFAULT 0,
    speaking_best_grade VARCHAR(10),
    speaking_best_score INTEGER,
    speaking_avg_score FLOAT,

    -- Overall
    total_exams INTEGER DEFAULT 0,
    overall_best_grade VARCHAR(10),
    overall_avg_score FLOAT,

    -- Timestamps
    first_exam_at TIMESTAMP WITH TIME ZONE,
    last_exam_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_oet_user_profession UNIQUE(user_id, profession)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_oet_progress_user ON oet_user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_oet_progress_profession ON oet_user_progress(profession);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_oet_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_oet_exams_updated_at ON oet_exams;
CREATE TRIGGER trigger_oet_exams_updated_at
    BEFORE UPDATE ON oet_exams
    FOR EACH ROW EXECUTE FUNCTION update_oet_updated_at();

DROP TRIGGER IF EXISTS trigger_oet_content_updated_at ON oet_content_items;
CREATE TRIGGER trigger_oet_content_updated_at
    BEFORE UPDATE ON oet_content_items
    FOR EACH ROW EXECUTE FUNCTION update_oet_updated_at();

DROP TRIGGER IF EXISTS trigger_oet_progress_updated_at ON oet_user_progress;
CREATE TRIGGER trigger_oet_progress_updated_at
    BEFORE UPDATE ON oet_user_progress
    FOR EACH ROW EXECUTE FUNCTION update_oet_updated_at();

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to update user progress after exam completion
CREATE OR REPLACE FUNCTION update_oet_user_progress()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        -- Update or insert progress record
        INSERT INTO oet_user_progress (
            user_id,
            profession,
            total_exams,
            first_exam_at,
            last_exam_at
        )
        VALUES (
            NEW.user_id,
            NEW.profession,
            1,
            NOW(),
            NOW()
        )
        ON CONFLICT (user_id, profession) DO UPDATE SET
            total_exams = oet_user_progress.total_exams + 1,
            last_exam_at = NOW();

        -- Update section-specific stats based on section type
        CASE NEW.section
            WHEN 'listening' THEN
                UPDATE oet_user_progress SET
                    listening_attempts = listening_attempts + 1,
                    listening_best_score = GREATEST(COALESCE(listening_best_score, 0), NEW.scaled_score),
                    listening_best_grade = CASE
                        WHEN NEW.scaled_score > COALESCE(listening_best_score, 0) THEN NEW.grade
                        ELSE listening_best_grade
                    END
                WHERE user_id = NEW.user_id AND profession = NEW.profession;
            WHEN 'reading' THEN
                UPDATE oet_user_progress SET
                    reading_attempts = reading_attempts + 1,
                    reading_best_score = GREATEST(COALESCE(reading_best_score, 0), NEW.scaled_score),
                    reading_best_grade = CASE
                        WHEN NEW.scaled_score > COALESCE(reading_best_score, 0) THEN NEW.grade
                        ELSE reading_best_grade
                    END
                WHERE user_id = NEW.user_id AND profession = NEW.profession;
            WHEN 'writing' THEN
                UPDATE oet_user_progress SET
                    writing_attempts = writing_attempts + 1,
                    writing_best_score = GREATEST(COALESCE(writing_best_score, 0), NEW.scaled_score),
                    writing_best_grade = CASE
                        WHEN NEW.scaled_score > COALESCE(writing_best_score, 0) THEN NEW.grade
                        ELSE writing_best_grade
                    END
                WHERE user_id = NEW.user_id AND profession = NEW.profession;
            WHEN 'speaking' THEN
                UPDATE oet_user_progress SET
                    speaking_attempts = speaking_attempts + 1,
                    speaking_best_score = GREATEST(COALESCE(speaking_best_score, 0), NEW.scaled_score),
                    speaking_best_grade = CASE
                        WHEN NEW.scaled_score > COALESCE(speaking_best_score, 0) THEN NEW.grade
                        ELSE speaking_best_grade
                    END
                WHERE user_id = NEW.user_id AND profession = NEW.profession;
        END CASE;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_oet_progress ON oet_exams;
CREATE TRIGGER trigger_update_oet_progress
    AFTER UPDATE ON oet_exams
    FOR EACH ROW EXECUTE FUNCTION update_oet_user_progress();

-- =============================================================================
-- VIEWS
-- =============================================================================

-- User exam summary view
CREATE OR REPLACE VIEW oet_user_exam_summary AS
SELECT
    user_id,
    profession,
    section,
    COUNT(*) as total_attempts,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    MAX(scaled_score) as best_score,
    AVG(scaled_score) FILTER (WHERE status = 'completed') as avg_score,
    MIN(created_at) as first_attempt,
    MAX(created_at) as last_attempt
FROM oet_exams
GROUP BY user_id, profession, section;

-- Content usage stats view
CREATE OR REPLACE VIEW oet_content_usage_stats AS
SELECT
    section,
    content_type,
    profession,
    COUNT(*) as total_items,
    COUNT(*) FILTER (WHERE is_verified) as verified_items,
    COUNT(*) FILTER (WHERE is_active) as active_items,
    SUM(times_used) as total_uses,
    AVG(average_score) as avg_item_score
FROM oet_content_items
GROUP BY section, content_type, profession;

-- =============================================================================
-- SAMPLE CONTENT (Optional - remove in production)
-- =============================================================================

-- Insert sample content item for testing
INSERT INTO oet_content_items (
    section,
    content_type,
    profession,
    content,
    difficulty_level,
    medical_specialty,
    tags,
    is_verified,
    is_active
)
VALUES (
    'reading',
    'passage',
    'medicine',
    '{"title": "Sample Reading Passage", "content": "This is a sample passage for testing...", "word_count": 500}',
    3,
    'general_medicine',
    ARRAY['sample', 'test', 'reading'],
    true,
    true
)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- GRANTS (adjust roles as needed)
-- =============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

COMMENT ON TABLE oet_exams IS 'OET exam sessions with content, answers, and results';
COMMENT ON TABLE oet_content_items IS 'Reusable content bank for OET exam generation';
COMMENT ON TABLE oet_audio_content IS 'Audio files and transcripts for OET Listening section';
COMMENT ON TABLE oet_user_progress IS 'User progress tracking across OET sections and professions';
