USE jobportal;
CREATE TABLE IF NOT EXISTS tracked_jobs (
    tracked_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NULL,                          -- filled for portal jobs, NULL for external jobs
    company VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    source VARCHAR(50) DEFAULT 'Manual',      -- Portal, Indeed, Internshala, Manual
    status VARCHAR(20) NOT NULL DEFAULT 'Wishlist',
    applied_date DATE NULL,
    notes VARCHAR(500) NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    UNIQUE KEY uq_candidate_job (candidate_id, job_id)
);