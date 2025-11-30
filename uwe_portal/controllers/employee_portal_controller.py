# -*- coding: utf-8 -*-
###############################################################################
#
#    UWE Portal Models
#    Copyright (C) 2024 UWE
#
###############################################################################

from odoo import http, fields
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class EmployeePortalController(CustomerPortal):
    """Controller for Employee Portal User portal page"""

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """Override portal home to redirect Employee Portal Users to custom page"""
        values = self._prepare_portal_layout_values()
        
        # Check if user is Employee Portal User
        if request.env.user.user_type == 'employee_portal':
            return request.redirect('/my/employee-portal')
        
        return super(EmployeePortalController, self).home(**kw)

    @http.route(['/my/employee-portal'], type='http', auth="user", website=True)
    def employee_portal_home(self, **kw):
        """Custom portal home page for Employee Portal Users"""
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'employee_portal_home',
        })
        return request.render("uwe_portal.employee_portal_home", values)

    @http.route(['/my/employee-portal/profile'], type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=True)
    def employee_portal_profile(self, **kw):
        """Employee profile page - editable"""
        values = self._prepare_portal_layout_values()
        
        # Get employee record if exists
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            # Search by user_id
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        error = None
        success = None
        
        # Handle form submission
        if request.httprequest.method == 'POST' and employee:
            try:
                import base64
                
                # Get form values - Basic contact info
                work_phone = kw.get('work_phone', '').strip()
                work_email = kw.get('work_email', '').strip()
                mobile_phone = kw.get('mobile_phone', '').strip()
                private_email = kw.get('private_email', '').strip()
                
                # Handle image upload
                image_file = kw.get('image_1920')
                image_data = None
                if image_file:
                    # image_file is a FileStorage object from werkzeug
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Certificate fields - Full Names
                full_name_english = kw.get('full_name_english', '').strip()
                full_name_arabic = kw.get('full_name_arabic', '').strip()
                
                # Certificate fields - Details
                passport_number = kw.get('passport_number', '').strip()
                visa_number = kw.get('visa_number', '').strip()
                emirati_id_number = kw.get('emirati_id_number', '').strip()
                english_level_exam = kw.get('english_level_exam', '').strip()
                program_name = kw.get('program_name', '').strip()
                academic_year = kw.get('academic_year', '').strip()
                license_number = kw.get('license_number', '').strip()
                
                # Certificate fields - Letters (HTML)
                letter_to_students = kw.get('letter_to_students', '').strip()
                letter_to_employees = kw.get('letter_to_employees', '').strip()
                
                # Certificate fields - Template
                certificate_template = kw.get('certificate_template', '').strip()
                custom_certificate_message = kw.get('custom_certificate_message', '').strip()
                
                # Update employee record
                update_vals = {}
                if work_phone:
                    update_vals['work_phone'] = work_phone
                if work_email:
                    update_vals['work_email'] = work_email
                if mobile_phone:
                    update_vals['mobile_phone'] = mobile_phone
                if private_email:
                    update_vals['private_email'] = private_email
                if image_data:
                    update_vals['image_1920'] = image_data
                
                # Certificate fields
                if full_name_english:
                    update_vals['full_name_english'] = full_name_english
                if full_name_arabic:
                    update_vals['full_name_arabic'] = full_name_arabic
                if passport_number:
                    update_vals['passport_number'] = passport_number
                if visa_number:
                    update_vals['visa_number'] = visa_number
                if emirati_id_number:
                    update_vals['emirati_id_number'] = emirati_id_number
                if english_level_exam:
                    update_vals['english_level_exam'] = english_level_exam
                if program_name:
                    update_vals['program_name'] = program_name
                if academic_year:
                    update_vals['academic_year'] = academic_year
                if license_number:
                    update_vals['license_number'] = license_number
                if letter_to_students:
                    update_vals['letter_to_students'] = letter_to_students
                if letter_to_employees:
                    update_vals['letter_to_employees'] = letter_to_employees
                if certificate_template:
                    update_vals['certificate_template'] = certificate_template
                if custom_certificate_message:
                    update_vals['custom_certificate_message'] = custom_certificate_message
                
                # Private Information fields
                private_street = kw.get('private_street', '').strip()
                private_street2 = kw.get('private_street2', '').strip()
                private_city = kw.get('private_city', '').strip()
                private_zip = kw.get('private_zip', '').strip()
                private_phone = kw.get('private_phone', '').strip()
                bank_account_id = kw.get('bank_account_id', '').strip()
                lang = kw.get('lang', '').strip()
                km_home_work = kw.get('km_home_work', '').strip()
                license_plate = kw.get('license_plate', '').strip()
                marital = kw.get('marital', '').strip()
                children = kw.get('children', '').strip()
                emergency_contact = kw.get('emergency_contact', '').strip()
                emergency_phone = kw.get('emergency_phone', '').strip()
                certificate = kw.get('certificate_level', '').strip()  # Note: field name is 'certificate' not 'certificate_level'
                study_field = kw.get('study_field', '').strip()
                study_school = kw.get('study_school', '').strip()
                identification_id = kw.get('identification_id', '').strip()
                ssnid = kw.get('ssnid', '').strip()
                passport_id = kw.get('passport_id', '').strip()
                gender = kw.get('gender', '').strip()
                birthday = kw.get('birthday', '').strip()
                place_of_birth = kw.get('place_of_birth', '').strip()
                country_of_birth = kw.get('country_of_birth', '').strip()
                is_non_resident = kw.get('is_non_resident') == 'on'
                visa_no = kw.get('visa_no', '').strip()
                permit_no = kw.get('work_permit_no', '').strip()  # Note: field name is 'permit_no' not 'work_permit_no'
                visa_expire = kw.get('visa_expire', '').strip()
                work_permit_expiration_date = kw.get('work_permit_expiration_date', '').strip()
                
                # Add private information fields to update_vals
                if private_street:
                    update_vals['private_street'] = private_street
                if private_street2:
                    update_vals['private_street2'] = private_street2
                if private_city:
                    update_vals['private_city'] = private_city
                if private_zip:
                    update_vals['private_zip'] = private_zip
                if private_phone:
                    update_vals['private_phone'] = private_phone
                if lang:
                    update_vals['lang'] = lang
                if km_home_work:
                    try:
                        update_vals['km_home_work'] = float(km_home_work)
                    except:
                        pass
                if license_plate:
                    update_vals['license_plate'] = license_plate
                if marital:
                    update_vals['marital'] = marital
                if children:
                    try:
                        update_vals['children'] = int(children)
                    except:
                        pass
                if emergency_contact:
                    update_vals['emergency_contact'] = emergency_contact
                if emergency_phone:
                    update_vals['emergency_phone'] = emergency_phone
                if certificate:
                    update_vals['certificate'] = certificate
                if study_field:
                    update_vals['study_field'] = study_field
                if study_school:
                    update_vals['study_school'] = study_school
                if identification_id:
                    update_vals['identification_id'] = identification_id
                if ssnid:
                    update_vals['ssnid'] = ssnid
                if passport_id:
                    update_vals['passport_id'] = passport_id
                if gender:
                    update_vals['gender'] = gender
                if birthday:
                    update_vals['birthday'] = birthday
                if place_of_birth:
                    update_vals['place_of_birth'] = place_of_birth
                update_vals['is_non_resident'] = is_non_resident
                if visa_no:
                    update_vals['visa_no'] = visa_no
                if permit_no:
                    update_vals['permit_no'] = permit_no
                if visa_expire:
                    update_vals['visa_expire'] = visa_expire
                if work_permit_expiration_date:
                    update_vals['work_permit_expiration_date'] = work_permit_expiration_date
                
                # Handle file uploads for Many2many attachments
                attachment_field_mapping = {
                    'letter_to_students_attachment': 'letter_to_students_attachment_ids',
                    'letter_to_employees_attachment': 'letter_to_employees_attachment_ids',
                    'passport_or_id_attachment': 'passport_or_id_attachment_ids',
                    'cv_attachment': 'cv_attachment_ids',
                    'photo_attachment': 'photo_attachment_ids',
                    'visa_uae_attachment': 'visa_uae_attachment_ids',
                    'degree_attachment': 'degree_attachment_ids',
                }
                
                # Process each attachment field
                for form_field_name, model_field_name in attachment_field_mapping.items():
                    file_obj = kw.get(form_field_name)
                    if file_obj:
                        # Create ir.attachment record
                        file_data = base64.b64encode(file_obj.read()).decode('utf-8')
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file_obj.filename,
                            'type': 'binary',
                            'datas': file_data,
                            'res_model': 'hr.employee',
                            'res_id': employee.id,
                        })
                        # Add to Many2many field
                        if model_field_name not in update_vals:
                            update_vals[model_field_name] = [(4, attachment.id)]
                        else:
                            # If already has attachments, append
                            if isinstance(update_vals[model_field_name], list):
                                update_vals[model_field_name].append((4, attachment.id))
                            else:
                                update_vals[model_field_name] = [(4, attachment.id)]
                
                # Handle work_permit_attachment separately (still Binary field)
                work_permit_file = kw.get('work_permit_attachment')
                if work_permit_file:
                    file_data = base64.b64encode(work_permit_file.read()).decode('utf-8')
                    update_vals['has_work_permit'] = file_data
                
                if update_vals:
                    employee.sudo().write(update_vals)
                    success = "Profile updated successfully!"
                else:
                    error = "No changes to save."
                    
            except Exception as e:
                error = f"Error updating profile: {str(e)}"
                _logger.error("Error updating employee profile: %s", str(e))
                import traceback
                _logger.error(traceback.format_exc())
        
        values.update({
            'employee': employee,
            'error': error,
            'success': success,
            'page_name': 'employee_portal_profile',
        })
        return request.render("uwe_portal.employee_portal_profile", values)

    @http.route(['/my/employee-portal/time-off'], type='http', auth="user", website=True)
    def employee_portal_time_off(self, **kw):
        """Time off requests page for Employee Portal Users"""
        values = self._prepare_portal_layout_values()
        
        # Get employee record if exists
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            # Search by user_id
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        # Get time off requests (hr.leave)
        leave_requests = []
        if employee:
            leave_requests = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order='date_from desc')
        
        values.update({
            'employee': employee,
            'leave_requests': leave_requests,
            'page_name': 'employee_portal_time_off',
        })
        return request.render("uwe_portal.employee_portal_time_off", values)

    @http.route(['/my/employee-portal/attendance'], type='http', auth="user", website=True)
    def employee_portal_attendance(self, **kw):
        """Attendance records page for Employee Portal Users"""
        values = self._prepare_portal_layout_values()
        
        # Get employee record if exists
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            # Search by user_id
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        # Get attendance records (hr.attendance)
        attendance_records = []
        current_attendance = False
        if employee:
            # Get attendance records - hr.attendance contains check-in/check-out records
            try:
                attendance_records = request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee.id)
                ], order='check_in desc', limit=100)
                
                # Get current open attendance (checked in but not checked out)
                current_attendance = request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False)
                ], order='check_in desc', limit=1)
            except Exception as e:
                # Log error but continue with empty list
                attendance_records = []
        
        values.update({
            'employee': employee,
            'attendance_records': attendance_records,
            'current_attendance': current_attendance,
            'page_name': 'employee_portal_attendance',
        })
        return request.render("uwe_portal.employee_portal_attendance", values)

    @http.route(['/my/employee-portal/attendance/check-in'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def employee_portal_attendance_check_in(self, **kw):
        """Check in for attendance"""
        # Get employee record
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        if not employee:
            return request.redirect('/my/employee-portal/attendance?error=1')
        
        try:
            # Check if already checked in
            current_attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], limit=1)
            
            if current_attendance:
                return request.redirect('/my/employee-portal/attendance?error=2')
            
            # Create check in record
            request.env['hr.attendance'].sudo().create({
                'employee_id': employee.id,
            })
            
            return request.redirect('/my/employee-portal/attendance?checked_in=1')
        except Exception as e:
            return request.redirect('/my/employee-portal/attendance?error=1')

    @http.route(['/my/employee-portal/attendance/check-out'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def employee_portal_attendance_check_out(self, **kw):
        """Check out for attendance"""
        # Get employee record
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        if not employee:
            return request.redirect('/my/employee-portal/attendance?error=1')
        
        try:
            # Get current attendance
            current_attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], order='check_in desc', limit=1)
            
            if not current_attendance:
                return request.redirect('/my/employee-portal/attendance?error=3')
            
            # Check out
            current_attendance.write({
                'check_out': fields.Datetime.now()
            })
            
            return request.redirect('/my/employee-portal/attendance?checked_out=1')
        except Exception as e:
            return request.redirect('/my/employee-portal/attendance?error=1')

    @http.route(['/my/employee-portal/payroll'], type='http', auth="user", website=True)
    def employee_portal_payroll(self, **kw):
        """Payroll payslips page for Employee Portal Users"""
        values = self._prepare_portal_layout_values()
        
        # Get employee record if exists
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            # Search by user_id
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        # Get payslips (hr.payslip)
        payslips = []
        if employee:
            try:
                # Search for payslips with sudo to bypass access rights
                # Try without any domain restrictions first to see all payslips
                all_payslips = request.env['hr.payslip'].sudo().search([
                    ('employee_id', '=', employee.id)
                ])
                
                _logger.info("Total payslips found for employee %s (ID: %s): %d", employee.name, employee.id, len(all_payslips))
                
                # Now get the ordered and limited set
                payslips = all_payslips.sorted(key=lambda p: p.date_from or fields.Date.today(), reverse=True)[:100]
                
                _logger.info("Returning %d payslips for employee %s (ID: %s)", len(payslips), employee.name, employee.id)
            except Exception as e:
                _logger.error("Error fetching payslips for employee %s: %s", employee.name if employee else 'Unknown', str(e))
                import traceback
                _logger.error(traceback.format_exc())
                payslips = []
        
        # Get company currency symbol
        try:
            company_currency = request.env.company.currency_id
            currency_symbol = company_currency.symbol if company_currency and company_currency.symbol else ''
        except:
            company_currency = False
            currency_symbol = ''
        
        # Get foreign currency from employee's active contract
        foreign_currency = False
        foreign_currency_symbol = ''
        if employee:
            try:
                # Get active contract for the employee
                active_contract = request.env['hr.contract'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open')
                ], limit=1, order='date_start desc')
                
                if active_contract and active_contract.foreign_currency_id:
                    foreign_currency = active_contract.foreign_currency_id
                    foreign_currency_symbol = foreign_currency.symbol if foreign_currency.symbol else foreign_currency.name
                    _logger.info("Found foreign currency %s for employee %s from contract", foreign_currency.name, employee.name)
                else:
                    _logger.info("No foreign currency found in contract for employee %s", employee.name)
            except Exception as e:
                _logger.warning("Error getting foreign currency from contract: %s", str(e))
                foreign_currency = False
        
        # Prepare payslips with foreign currency conversion (if foreign currency is set in contract)
        payslips_with_foreign = []
        for payslip in payslips:
            payslip_data = {
                'payslip': payslip,
                'foreign_amounts': {}
            }
            
            # Only convert if foreign currency is set in contract
            if foreign_currency and company_currency:
                try:
                    # Get amounts from payslip lines
                    basic_line = payslip.line_ids.filtered(lambda l: l.code == 'BASIC')
                    gross_line = payslip.line_ids.filtered(lambda l: l.code == 'GROSS')
                    net_line = payslip.line_ids.filtered(lambda l: l.code == 'NET')
                    
                    basic_amount = basic_line[0].total if basic_line else 0.0
                    gross_amount = gross_line[0].total if gross_line else 0.0
                    net_amount = net_line[0].total if net_line else 0.0
                    deduction_amount = gross_amount - net_amount
                    
                    # Use _convert for accurate conversion based on payslip creation date
                    # Convert create_date (datetime) to date for currency conversion
                    if payslip.create_date:
                        payslip_date = fields.Date.to_date(payslip.create_date)
                    else:
                        payslip_date = payslip.date_from or fields.Date.today()
                    
                    try:
                        # Convert to foreign currency using payslip creation date
                        basic_foreign = company_currency._convert(basic_amount, foreign_currency, request.env.company, payslip_date)
                        gross_foreign = company_currency._convert(gross_amount, foreign_currency, request.env.company, payslip_date)
                        net_foreign = company_currency._convert(net_amount, foreign_currency, request.env.company, payslip_date)
                        deduction_foreign = company_currency._convert(deduction_amount, foreign_currency, request.env.company, payslip_date)
                        
                        payslip_data['foreign_amounts'] = {
                            'basic': basic_foreign,
                            'gross': gross_foreign,
                            'net': net_foreign,
                            'deduction': deduction_foreign,
                        }
                        
                        # Calculate conversion rate for display
                        test_amount = 1.0
                        conversion_rate = company_currency._convert(
                            test_amount,
                            foreign_currency,
                            request.env.company,
                            payslip_date
                        )
                        payslip_data['conversion_rate'] = conversion_rate
                        
                    except Exception as e:
                        _logger.warning("Error converting payslip %s to foreign currency %s: %s", payslip.id, foreign_currency.name, str(e))
                        payslip_data['foreign_amounts'] = {}
                except Exception as e:
                    _logger.warning("Error processing payslip %s for foreign currency conversion: %s", payslip.id, str(e))
                    payslip_data['foreign_amounts'] = {}
            
            payslips_with_foreign.append(payslip_data)
        
        if not employee:
            # Employee not found - log for debugging
            _logger.warning("Employee not found for user: %s (ID: %s)", request.env.user.name, request.env.user.id)
        
        values.update({
            'employee': employee,
            'payslips': payslips,
            'payslips_with_foreign': payslips_with_foreign,
            'currency_symbol': currency_symbol or '',
            'foreign_currency': foreign_currency,
            'foreign_currency_symbol': foreign_currency_symbol,
            'foreign_currency_available': bool(foreign_currency),
            'page_name': 'employee_portal_payroll',
        })
        return request.render("uwe_portal.employee_portal_payroll", values)

    @http.route(['/my/employee-portal/time-off/create'], type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=True)
    def employee_portal_time_off_create(self, **kw):
        """Create new time off request page"""
        values = self._prepare_portal_layout_values()
        
        # Get employee record if exists
        employee = False
        if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
            employee = request.env.user.employee_id
        elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
            employee = request.env.user.employee_ids[0]
        else:
            # Search by user_id
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        if not employee:
            return request.redirect('/my/employee-portal/time-off')
        
        # Get leave types (holiday status)
        leave_types = request.env['hr.leave.type'].sudo().search([])
        if not leave_types:
            # Try hr.leave.type or hr.holidays.status
            leave_types = request.env['hr.holidays.status'].sudo().search([])
        
        # Handle form submission
        if request.httprequest.method == 'POST':
            try:
                # Get form data
                holiday_status_id = kw.get('holiday_status_id')
                date_from = kw.get('date_from')
                date_to = kw.get('date_to')
                request_unit_half = kw.get('request_unit_half', False)
                request_date_from_period = kw.get('request_date_from_period', 'am')
                name = kw.get('name', '')
                
                if not holiday_status_id or not date_from or not date_to:
                    values.update({
                        'error': 'Please fill in all required fields.',
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("uwe_portal.employee_portal_time_off_create", values)
                
                # Convert date strings to datetime format
                # Odoo expects datetime strings in format: 'YYYY-MM-DD HH:MM:SS'
                # For full day leaves, we use start of day for date_from and end of day for date_to
                try:
                    date_from_dt = None
                    date_to_dt = None
                    
                    if isinstance(date_from, str):
                        # Parse the date and add time component
                        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                        # Use 00:00:00 for start of day
                        date_from_str = date_from_dt.strftime('%Y-%m-%d 00:00:00')
                    else:
                        date_from_str = date_from
                    
                    if isinstance(date_to, str):
                        # Parse the date and add time component
                        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                        # Use 23:59:59 for end of day
                        date_to_str = date_to_dt.strftime('%Y-%m-%d 23:59:59')
                    else:
                        date_to_str = date_to
                    
                    # Validate that date_to is after date_from
                    if date_from_dt and date_to_dt and date_from_dt > date_to_dt:
                        values.update({
                            'error': 'End date must be after or equal to start date.',
                            'employee': employee,
                            'leave_types': leave_types,
                            'page_name': 'employee_portal_time_off_create',
                        })
                        return request.render("uwe_portal.employee_portal_time_off_create", values)
                except ValueError as ve:
                    values.update({
                        'error': 'Invalid date format. Please use the date picker.',
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("uwe_portal.employee_portal_time_off_create", values)
                
                # Check for overlapping leave requests before creating
                # Use datetime objects for comparison
                date_from_for_search = date_from_dt if date_from_dt else datetime.strptime(date_from_str, '%Y-%m-%d %H:%M:%S')
                date_to_for_search = date_to_dt if date_to_dt else datetime.strptime(date_to_str, '%Y-%m-%d %H:%M:%S')
                
                existing_leaves = request.env['hr.leave'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('state', 'in', ['draft', 'confirm', 'validate']),
                ])
                
                # Filter overlapping leaves manually
                overlapping_leaves = []
                for existing in existing_leaves:
                    if existing.date_from and existing.date_to:
                        # Check if dates overlap
                        if (date_from_for_search <= existing.date_to and date_to_for_search >= existing.date_from):
                            overlapping_leaves.append(existing)
                
                if overlapping_leaves:
                    # Format existing leave dates for error message
                    overlap_dates = []
                    for existing in overlapping_leaves:
                        if existing.date_from and existing.date_to:
                            from_date = existing.date_from.strftime('%m/%d/%Y')
                            to_date = existing.date_to.strftime('%m/%d/%Y')
                            state = dict(existing._fields['state'].selection).get(existing.state, existing.state)
                            overlap_dates.append(f"from {from_date} to {to_date} - {state}")
                    
                    if overlap_dates:
                        error_msg = f"You've already booked time off which overlaps with this period: {', '.join(overlap_dates)}. Attempting to double-book your time off won't magically make your vacation 2x better!"
                    else:
                        error_msg = "You've already booked time off which overlaps with this period. Attempting to double-book your time off won't magically make your vacation 2x better!"
                    
                    values.update({
                        'error': error_msg,
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("uwe_portal.employee_portal_time_off_create", values)
                
                # Create leave request
                leave_vals = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(holiday_status_id),
                    'date_from': date_from_str,
                    'date_to': date_to_str,
                    'name': name,
                }
                
                # Add half day options if available
                if request_unit_half:
                    leave_vals['request_unit_half'] = True
                    leave_vals['request_date_from_period'] = request_date_from_period
                
                # Try to create leave request and catch validation errors
                try:
                    leave_request = request.env['hr.leave'].sudo().create(leave_vals)
                except (ValidationError, UserError) as ve:
                    # Extract error message from ValidationError
                    error_msg = str(ve)
                    if hasattr(ve, 'name') and ve.name:
                        error_msg = ve.name
                    elif hasattr(ve, 'args') and ve.args:
                        error_msg = ve.args[0] if isinstance(ve.args[0], str) else str(ve)
                    
                    values.update({
                        'error': error_msg,
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("uwe_portal.employee_portal_time_off_create", values)
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's a constraint violation
                    if 'constraint' in error_msg.lower() or 'check' in error_msg.lower():
                        error_msg = 'Invalid date range. Please ensure the end date is after the start date.'
                    
                    values.update({
                        'error': f'Error creating leave request: {error_msg}',
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("uwe_portal.employee_portal_time_off_create", values)
                
                # Redirect to time off page with success message
                return request.redirect('/my/employee-portal/time-off?created=1')
                
            except Exception as e:
                # Handle any other unexpected errors
                error_msg = str(e)
                if isinstance(e, (ValidationError, UserError)):
                    if hasattr(e, 'name') and e.name:
                        error_msg = e.name
                    elif hasattr(e, 'args') and e.args:
                        error_msg = e.args[0] if isinstance(e.args[0], str) else str(e)
                
                values.update({
                    'error': f'Error creating leave request: {error_msg}',
                    'employee': employee,
                    'leave_types': leave_types,
                    'page_name': 'employee_portal_time_off_create',
                })
                return request.render("uwe_portal.employee_portal_time_off_create", values)
        
        values.update({
            'employee': employee,
            'leave_types': leave_types,
            'page_name': 'employee_portal_time_off_create',
        })
        return request.render("uwe_portal.employee_portal_time_off_create", values)

    @http.route(['/my/employee-portal/time-off/cancel'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def employee_portal_time_off_cancel(self, **kw):
        """Cancel or delete time off request"""
        leave_id = kw.get('leave_id')
        
        if not leave_id:
            return request.redirect('/my/employee-portal/time-off?error=1')
        
        try:
            # Get employee record
            employee = False
            if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
                employee = request.env.user.employee_id
            elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
                employee = request.env.user.employee_ids[0]
            else:
                employee = request.env['hr.employee'].sudo().search([
                    ('user_id', '=', request.env.user.id)
                ], limit=1)
            
            if not employee:
                return request.redirect('/my/employee-portal/time-off?error=1')
            
            # Get leave request with new cursor to avoid transaction issues
            leave = request.env['hr.leave'].sudo().browse(int(leave_id))
            
            # Verify the leave belongs to the employee
            if not leave.exists() or leave.employee_id.id != employee.id:
                return request.redirect('/my/employee-portal/time-off?error=1')
            
            # Cancel or delete based on state
            if leave.state == 'draft':
                # Delete draft requests
                leave.unlink()
            elif leave.state == 'confirm':
                # Cancel confirmed requests - try to refuse first
                try:
                    # Try to refuse the leave request
                    if hasattr(leave, 'action_refuse'):
                        leave.action_refuse()
                    else:
                        # If action_refuse doesn't exist, try to write state directly
                        leave.write({'state': 'refuse'})
                except (ValidationError, UserError) as ve:
                    # If we can't refuse, try to delete
                    try:
                        leave.unlink()
                    except Exception:
                        return request.redirect('/my/employee-portal/time-off?error=1')
                except Exception as e:
                    # Try to delete
                    try:
                        leave.unlink()
                    except Exception:
                        return request.redirect('/my/employee-portal/time-off?error=1')
            else:
                # For other states, we can't cancel
                return request.redirect('/my/employee-portal/time-off?error=2')
            
            # Redirect with success message
            return request.redirect('/my/employee-portal/time-off?canceled=1')
            
        except (ValidationError, UserError) as ve:
            return request.redirect('/my/employee-portal/time-off?error=1')
        except Exception as e:
            return request.redirect('/my/employee-portal/time-off?error=1')

    @http.route(['/my/employee-portal/profile/attachment/delete/<int:employee_id>/<string:field_name>/<int:attachment_id>'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def employee_portal_profile_attachment_delete(self, employee_id, field_name, attachment_id, **kw):
        """Delete an attachment from a Many2many field"""
        try:
            # Get employee record
            employee = request.env['hr.employee'].sudo().browse(employee_id)
            
            # Verify employee ownership
            user_employee = False
            if hasattr(request.env.user, 'employee_id') and request.env.user.employee_id:
                user_employee = request.env.user.employee_id
            elif hasattr(request.env.user, 'employee_ids') and request.env.user.employee_ids:
                user_employee = request.env.user.employee_ids[0]
            else:
                user_employee = request.env['hr.employee'].sudo().search([
                    ('user_id', '=', request.env.user.id)
                ], limit=1)
            
            if not user_employee or user_employee.id != employee.id:
                return request.redirect('/my/employee-portal/profile?error=unauthorized')
            
            # Map field names
            field_mapping = {
                'letter_to_students_attachment': 'letter_to_students_attachment_ids',
                'letter_to_employees_attachment': 'letter_to_employees_attachment_ids',
                'passport_or_id_attachment': 'passport_or_id_attachment_ids',
                'cv_attachment': 'cv_attachment_ids',
                'photo_attachment': 'photo_attachment_ids',
                'visa_uae_attachment': 'visa_uae_attachment_ids',
                'degree_attachment': 'degree_attachment_ids',
            }
            
            model_field_name = field_mapping.get(field_name)
            if not model_field_name or not hasattr(employee, model_field_name):
                return request.redirect('/my/employee-portal/profile?error=invalid_field')
            
            # Get attachment and verify it belongs to the employee
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            if not attachment.exists() or attachment.res_model != 'hr.employee' or attachment.res_id != employee.id:
                return request.redirect('/my/employee-portal/profile?error=invalid_attachment')
            
            # Remove attachment from Many2many field
            employee.write({model_field_name: [(3, attachment_id)]})
            
            # Delete the attachment record
            attachment.unlink()
            
            return request.redirect('/my/employee-portal/profile?deleted=1')
            
        except Exception as e:
            _logger.error("Error deleting attachment: %s", str(e))
            return request.redirect('/my/employee-portal/profile?error=delete_failed')

