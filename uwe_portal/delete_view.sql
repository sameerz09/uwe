-- Run this SQL script to delete the problematic view
-- You can run it using: psql -d uwe3 -f delete_view.sql
-- Or copy and paste these commands in psql

DELETE FROM ir_ui_view 
WHERE name = 'res.users.groups.hide.user.type' 
AND model = 'res.users';

DELETE FROM ir_model_data 
WHERE module = 'uwe_portal' 
AND model = 'ir.ui.view'
AND (name LIKE '%employee_portal%' OR name LIKE '%group_employee%');

