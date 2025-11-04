-- SQL script to add missing columns to hr_employee table
-- Run this script directly on your PostgreSQL database if the upgrade fails

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS full_name_english VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS full_name_arabic VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS visa_number VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS english_level_exam VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_students TEXT;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_employees TEXT;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_students_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_students_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_employees_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS letter_to_employees_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS certificate_template VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS custom_certificate_message TEXT;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS passport_or_id_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS passport_or_id_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS cv_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS cv_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS photo_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS photo_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS visa_uae_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS visa_uae_filename VARCHAR;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS degree_attachment BYTEA;

ALTER TABLE hr_employee 
ADD COLUMN IF NOT EXISTS degree_filename VARCHAR;

