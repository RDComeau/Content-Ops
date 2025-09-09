-- Content Ops Database Initialization
-- This script sets up the initial database structure for WordPress sites

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS content_ops;
USE content_ops;

-- Create additional indexes for better performance
-- These will be applied after WordPress creates its tables

-- Optimize post queries
ALTER TABLE site1_posts ADD INDEX idx_post_type_status_date (post_type, post_status, post_date);
ALTER TABLE site2_posts ADD INDEX idx_post_type_status_date (post_type, post_status, post_date);

-- Optimize meta queries
ALTER TABLE site1_postmeta ADD INDEX idx_meta_key_value (meta_key, meta_value(255));
ALTER TABLE site2_postmeta ADD INDEX idx_meta_key_value (meta_key, meta_value(255));

-- Optimize user queries
ALTER TABLE site1_users ADD INDEX idx_user_email (user_email);
ALTER TABLE site2_users ADD INDEX idx_user_email (user_email);

-- Create shared tables for cross-site functionality
CREATE TABLE IF NOT EXISTS content_sync_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_site VARCHAR(50) NOT NULL,
    target_site VARCHAR(50) NOT NULL,
    post_id INT NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    error_message TEXT NULL,
    INDEX idx_status_created (status, created_at),
    INDEX idx_source_target (source_site, target_site)
);

CREATE TABLE IF NOT EXISTS backup_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,
    backup_path VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    r2_key VARCHAR(255) NULL,
    status ENUM('created', 'uploaded', 'failed') DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_at TIMESTAMP NULL,
    error_message TEXT NULL,
    INDEX idx_status_created (status, created_at),
    INDEX idx_backup_type (backup_type)
);

CREATE TABLE IF NOT EXISTS automation_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(50) NULL,
    site VARCHAR(50) NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_site_date (metric_name, site, recorded_at),
    INDEX idx_recorded_date (recorded_at)
);

-- Insert initial automation stats
INSERT INTO automation_stats (metric_name, metric_value, metric_unit) VALUES
('backup_frequency', 24, 'hours'),
('sync_frequency', 6, 'hours'),
('retention_days', 30, 'days');

-- Create user for automation scripts (if not using root)
CREATE USER IF NOT EXISTS 'content_automation'@'%' IDENTIFIED BY 'automation_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON content_ops.* TO 'content_automation'@'%';
GRANT SELECT ON information_schema.* TO 'content_automation'@'%';
FLUSH PRIVILEGES;