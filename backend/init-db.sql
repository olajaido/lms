-- ============================================================================
-- LMS Platform Database Initialization Script
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USER SERVICE TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'instructor', 'admin')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COURSE SERVICE TABLES
-- ============================================================================

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructor VARCHAR(100),
    duration INTEGER DEFAULT 0,
    difficulty VARCHAR(20) DEFAULT 'beginner' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    category VARCHAR(100),
    price DECIMAL(10,2) DEFAULT 0.00,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENROLLMENT SERVICE TABLES
-- ============================================================================

-- Enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'in_progress', 'completed', 'dropped')),
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    grade DECIMAL(5,2),
    UNIQUE(user_id, course_id)
);

-- ============================================================================
-- ASSESSMENT SERVICE TABLES
-- ============================================================================

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) DEFAULT 'quiz' CHECK (type IN ('quiz', 'exam', 'assignment')),
    course_id INTEGER,
    total_points INTEGER DEFAULT 100,
    time_limit INTEGER DEFAULT 0,
    passing_score DECIMAL(5,2) DEFAULT 70.00,
    allow_retakes BOOLEAN DEFAULT false,
    max_attempts INTEGER DEFAULT 1,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessment submissions table
CREATE TABLE IF NOT EXISTS assessment_submissions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score DECIMAL(5,2),
    max_score DECIMAL(5,2),
    attempt_number INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted', 'graded', 'failed')),
    feedback TEXT
);

-- ============================================================================
-- PROGRESS SERVICE TABLES
-- ============================================================================

-- Progress tracking table
CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    module_id INTEGER,
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    time_spent INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ANALYTICS SERVICE TABLES
-- ============================================================================

-- User analytics table
CREATE TABLE IF NOT EXISTS user_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_duration INTEGER DEFAULT 0,
    login_count INTEGER DEFAULT 0,
    last_login TIMESTAMP,
    total_courses_enrolled INTEGER DEFAULT 0,
    completed_courses INTEGER DEFAULT 0,
    average_grade DECIMAL(5,2),
    engagement_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMMUNICATION SERVICE TABLES
-- ============================================================================

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CONTENT SERVICE TABLES
-- ============================================================================

-- Content table
CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    mime_type VARCHAR(100),
    duration INTEGER,
    thumbnail_path VARCHAR(500),
    course_id INTEGER,
    module_id INTEGER,
    uploaded_by INTEGER,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    download_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    content_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample admin user
INSERT INTO users (email, username, first_name, last_name, hashed_password, role, is_verified) 
VALUES (
    'admin@lms.com',
    'admin',
    'Admin',
    'User',
    crypt('admin123', gen_salt('bf')),
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert sample instructor user
INSERT INTO users (email, username, first_name, last_name, hashed_password, role, is_verified) 
VALUES (
    'instructor@lms.com',
    'instructor',
    'John',
    'Doe',
    crypt('instructor123', gen_salt('bf')),
    'instructor',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert sample student user
INSERT INTO users (email, username, first_name, last_name, hashed_password, role, is_verified) 
VALUES (
    'student@lms.com',
    'student',
    'Jane',
    'Smith',
    crypt('student123', gen_salt('bf')),
    'student',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert sample courses
INSERT INTO courses (title, description, instructor, duration, difficulty, category, price, is_published) 
VALUES 
    ('Introduction to Python Programming', 'Learn the basics of Python programming language', 'John Doe', 120, 'beginner', 'Programming', 49.99, true),
    ('Advanced Web Development', 'Master modern web development techniques', 'John Doe', 180, 'intermediate', 'Web Development', 79.99, true),
    ('Data Science Fundamentals', 'Introduction to data science and machine learning', 'Jane Wilson', 240, 'advanced', 'Data Science', 99.99, true),
    ('Digital Marketing Strategy', 'Learn effective digital marketing strategies', 'Mike Johnson', 90, 'beginner', 'Marketing', 39.99, true),
    ('Project Management Essentials', 'Master project management fundamentals', 'Sarah Brown', 150, 'intermediate', 'Business', 59.99, true),
    ('Cybersecurity Basics', 'Introduction to cybersecurity principles', 'David Lee', 200, 'intermediate', 'Security', 69.99, true)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Courses indexes
CREATE INDEX IF NOT EXISTS idx_courses_instructor ON courses(instructor);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_courses_published ON courses(is_published);

-- Enrollments indexes
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status);

-- Assessments indexes
CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_assessments_type ON assessments(type);

-- Progress indexes
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_course_id ON progress(course_id);

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);

-- Content indexes
CREATE INDEX IF NOT EXISTS idx_content_course_id ON content(course_id);
CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_public ON content(is_public);

-- ============================================================================
-- COMMIT TRANSACTION
-- ============================================================================

COMMIT; 