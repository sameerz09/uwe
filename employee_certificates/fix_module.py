#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix missing columns in hr_employee table
Run this using Odoo shell: python odoo-bin shell -d uwe3 < fix_module.py
"""

# Add missing columns
env.cr.execute("""
    ALTER TABLE hr_employee 
    ADD COLUMN IF NOT EXISTS full_name_english VARCHAR,
    ADD COLUMN IF NOT EXISTS full_name_arabic VARCHAR,
    ADD COLUMN IF NOT EXISTS visa_number VARCHAR,
    ADD COLUMN IF NOT EXISTS english_level_exam VARCHAR,
    ADD COLUMN IF NOT EXISTS letter_to_students TEXT,
    ADD COLUMN IF NOT EXISTS letter_to_employees TEXT,
    ADD COLUMN IF NOT EXISTS letter_to_students_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS letter_to_students_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS letter_to_employees_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS letter_to_employees_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS certificate_template VARCHAR,
    ADD COLUMN IF NOT EXISTS custom_certificate_message TEXT,
    ADD COLUMN IF NOT EXISTS passport_or_id_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS passport_or_id_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS cv_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS cv_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS photo_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS photo_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS visa_uae_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS visa_uae_filename VARCHAR,
    ADD COLUMN IF NOT EXISTS degree_attachment BYTEA,
    ADD COLUMN IF NOT EXISTS degree_filename VARCHAR;
""")
env.cr.commit()

print("Columns added successfully!")

