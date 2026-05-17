CREATE TABLE IF NOT EXISTS candidates (

    id SERIAL PRIMARY KEY,

    full_name TEXT,
    email TEXT,
    phone TEXT,

    resume_filename TEXT,
    original_resume TEXT,
    masked_resume TEXT,

    skills TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS jobs (

    id SERIAL PRIMARY KEY,

    title TEXT,
    description TEXT,
    required_skills TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS applications (

    id SERIAL PRIMARY KEY,

    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),

    semantic_score FLOAT,
    keyword_score FLOAT,
    final_score FLOAT,
    confidence TEXT,
    governance_flag TEXT,
    application_status TEXT DEFAULT 'PENDING',
    confidence_score FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS audit_logs (

    id SERIAL PRIMARY KEY,

    application_id INTEGER REFERENCES applications(id),
    action_type TEXT,
    action_details TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS recruiter_feedback (

    id SERIAL PRIMARY KEY,

    application_id INTEGER REFERENCES applications(id),
    recruiter_action TEXT,
    recruiter_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS recruiter_memory (

    id SERIAL PRIMARY KEY,

    recruiter_query TEXT,
    system_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS email_logs (

    id SERIAL PRIMARY KEY,

    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    email_type TEXT,
    email_content TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS email_drafts (

    id SERIAL PRIMARY KEY,

    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'DRAFT',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS feedback (

    id SERIAL PRIMARY KEY,

    session_id TEXT,
    query TEXT,
    ai_response TEXT,
    feedback_type TEXT,
    feedback_score INTEGER,
    user_comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS conversation_memory (

    id SERIAL PRIMARY KEY,

    session_id TEXT,
    memory_scope TEXT,
    role TEXT,
    message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
