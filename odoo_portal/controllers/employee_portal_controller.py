# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo Portal Models
#    Copyright (C) 2025 Odoo Box
#
###############################################################################

from odoo import http, fields
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime
import logging
import traceback

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
        return request.render("odoo_portal.employee_portal_home", values)

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
                
                # Certificate fields removed - not in default Odoo
                
                # Get available fields in hr.employee model to filter out non-existent fields
                employee_fields = set(request.env['hr.employee']._fields.keys())
                
                # Helper function to safely add field if it exists
                def safe_add_field(field_name, value, update_dict):
                    """Add field to update_dict only if it exists in the model"""
                    if field_name in employee_fields and value:
                        update_dict[field_name] = value
                
                # Update employee record - only include fields that exist in default Odoo
                update_vals = {}
                
                # Basic contact info (default Odoo fields)
                safe_add_field('work_phone', work_phone, update_vals)
                safe_add_field('work_email', work_email, update_vals)
                safe_add_field('mobile_phone', mobile_phone, update_vals)
                if image_data:
                    safe_add_field('image_1920', image_data, update_vals)
                
                # Certificate fields removed - not in default Odoo
                
                # Private Information fields (default Odoo fields)
                private_street = kw.get('private_street', '').strip()
                private_street2 = kw.get('private_street2', '').strip()
                private_city = kw.get('private_city', '').strip()
                private_zip = kw.get('private_zip', '').strip()
                private_phone = kw.get('private_phone', '').strip()
                km_home_work = kw.get('km_home_work', '').strip()
                license_plate = kw.get('license_plate', '').strip()
                marital = kw.get('marital', '').strip()
                children = kw.get('children', '').strip()
                emergency_contact = kw.get('emergency_contact', '').strip()
                emergency_phone = kw.get('emergency_phone', '').strip()
                certificate = kw.get('certificate_level', '').strip()
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
                permit_no = kw.get('work_permit_no', '').strip()
                visa_expire = kw.get('visa_expire', '').strip()
                work_permit_expiration_date = kw.get('work_permit_expiration_date', '').strip()
                
                # Add private information fields to update_vals (only if they exist)
                safe_add_field('private_street', private_street, update_vals)
                safe_add_field('private_street2', private_street2, update_vals)
                safe_add_field('private_city', private_city, update_vals)
                safe_add_field('private_zip', private_zip, update_vals)
                safe_add_field('private_phone', private_phone, update_vals)
                
                if km_home_work:
                    try:
                        safe_add_field('km_home_work', float(km_home_work), update_vals)
                    except:
                        pass
                
                safe_add_field('license_plate', license_plate, update_vals)
                safe_add_field('marital', marital, update_vals)
                
                if children:
                    try:
                        safe_add_field('children', int(children), update_vals)
                    except:
                        pass
                
                safe_add_field('emergency_contact', emergency_contact, update_vals)
                safe_add_field('emergency_phone', emergency_phone, update_vals)
                safe_add_field('certificate', certificate, update_vals)
                safe_add_field('study_field', study_field, update_vals)
                safe_add_field('study_school', study_school, update_vals)
                safe_add_field('identification_id', identification_id, update_vals)
                safe_add_field('ssnid', ssnid, update_vals)
                safe_add_field('passport_id', passport_id, update_vals)
                safe_add_field('gender', gender, update_vals)
                safe_add_field('birthday', birthday, update_vals)
                safe_add_field('place_of_birth', place_of_birth, update_vals)
                safe_add_field('country_of_birth', country_of_birth, update_vals)
                
                if 'is_non_resident' in employee_fields:
                    update_vals['is_non_resident'] = is_non_resident
                
                safe_add_field('visa_no', visa_no, update_vals)
                safe_add_field('permit_no', permit_no, update_vals)
                safe_add_field('visa_expire', visa_expire, update_vals)
                safe_add_field('work_permit_expiration_date', work_permit_expiration_date, update_vals)
                
                # Custom attachment fields removed - not in default Odoo
                # Only handle work_permit_attachment if field exists
                work_permit_file = kw.get('work_permit_attachment')
                if work_permit_file and 'has_work_permit' in employee_fields:
                    try:
                        file_data = base64.b64encode(work_permit_file.read()).decode('utf-8')
                        update_vals['has_work_permit'] = file_data
                    except Exception as e:
                        _logger.warning("Error processing work permit attachment: %s", str(e))
                
                if update_vals:
                    try:
                        # Filter out any fields that might not exist (double check)
                        employee_fields = set(request.env['hr.employee']._fields.keys())
                        filtered_vals = {k: v for k, v in update_vals.items() if k in employee_fields}
                        
                        if filtered_vals:
                            employee.sudo().write(filtered_vals)
                            success = "Profile updated successfully!"
                        else:
                            error = "No valid fields to update."
                    except Exception as write_error:
                        error = f"Error updating profile: {str(write_error)}"
                        _logger.error("Error writing employee profile: %s", str(write_error))
                        import traceback
                        _logger.error(traceback.format_exc())
                else:
                    error = "No changes to save."
                    
            except Exception as e:
                error = f"Error updating profile: {str(e)}"
                _logger.error("Error updating employee profile: %s", str(e))
                import traceback
                _logger.error(traceback.format_exc())
        
        # Helper function to safely get field value
        def safe_get_field(emp, field_name, default=''):
            """Safely get field value from employee record"""
            if not emp:
                return default
            try:
                if field_name in emp._fields:
                    value = getattr(emp, field_name, default)
                    # Handle Many2many and One2many fields - return empty list if None
                    if value is None and isinstance(default, list):
                        return []
                    # Return value or default
                    return value if value else default
            except (AttributeError, KeyError):
                pass
            return default
        
        values.update({
            'employee': employee,
            'error': error,
            'success': success,
            'page_name': 'employee_portal_profile',
            'safe_get_field': safe_get_field,  # Pass helper function to template
        })
        return request.render("odoo_portal.employee_portal_profile", values)

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
        return request.render("odoo_portal.employee_portal_time_off", values)

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
        return request.render("odoo_portal.employee_portal_attendance", values)

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
        return request.render("odoo_portal.employee_portal_payroll", values)

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
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
        
        if not employee:
            return request.redirect('/my/employee-portal/time-off')
        
        # Get leave types (holiday status)
        leave_types = request.env['hr.leave.type'].sudo().search([])
        if not leave_types:
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
                    return request.render("odoo_portal.employee_portal_time_off_create", values)
                
                # Convert date strings to date format
                try:
                    date_from_dt = None
                    date_to_dt = None
                    
                    if isinstance(date_from, str):
                        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d').date()
                    else:
                        date_from_dt = date_from if hasattr(date_from, 'date') else date_from
                    
                    if isinstance(date_to, str):
                        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d').date()
                    else:
                        date_to_dt = date_to if hasattr(date_to, 'date') else date_to
                    
                    # Validate that date_to is after date_from
                    if date_from_dt and date_to_dt and date_from_dt > date_to_dt:
                        values.update({
                            'error': 'End date must be after or equal to start date.',
                            'employee': employee,
                            'leave_types': leave_types,
                            'page_name': 'employee_portal_time_off_create',
                        })
                        return request.render("odoo_portal.employee_portal_time_off_create", values)
                except ValueError:
                    values.update({
                        'error': 'Invalid date format. Please use the date picker.',
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("odoo_portal.employee_portal_time_off_create", values)
                
                # Create leave request using request_date_from and request_date_to
                # Odoo will compute date_from and date_to from these
                leave_vals = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(holiday_status_id),
                    'request_date_from': date_from_dt,
                    'request_date_to': date_to_dt,
                    'name': name,
                }
                
                # Add half day options if available
                if request_unit_half:
                    leave_vals['request_unit_half'] = True
                    leave_vals['request_date_from_period'] = request_date_from_period
                
                # Try to create leave request and catch validation errors
                # Use sudo() with context to bypass permission checks for activity types
                # Skip date check for portal users to allow more flexible leave management
                try:
                    leave_request = request.env['hr.leave'].sudo().with_context(
                        leave_skip_date_check=True,  # Skip overlap validation for portal users
                        leave_skip_state_check=True,  # Skip state check
                        mail_create_nolog=True,  # Skip mail logging
                        mail_create_nosubscribe=True,  # Skip subscription
                        mail_notrack=True,  # Skip tracking
                        tracking_disable=True,  # Disable tracking
                        mail_activity_automation_skip=True,  # Skip activity automation
                        calendar_no_videocall=True,  # Skip video call creation
                        no_mail_to_attendees=True,  # Skip mail to attendees
                    ).create(leave_vals)
                except (ValidationError, UserError, AccessError) as ve:
                    error_msg = str(ve)
                    if hasattr(ve, 'name') and ve.name:
                        error_msg = ve.name
                    elif hasattr(ve, 'args') and ve.args:
                        error_msg = ve.args[0] if isinstance(ve.args[0], str) else str(ve)
                    
                    # If it's an AccessError about activity types, calendar events, or mail activities, try creating without mail features
                    if isinstance(ve, AccessError) and ('activity type' in error_msg.lower() or 'calendar event' in error_msg.lower() or 'activity' in error_msg.lower() and 'mail.activity' in error_msg.lower()):
                        try:
                            # Try creating with minimal mail context and skip date check
                            # Also ensure calendar event creation is handled with sudo
                            leave_request = request.env['hr.leave'].sudo().with_context(
                                leave_skip_date_check=True,
                                leave_skip_state_check=True,
                                mail_create_nosubscribe=True,
                                mail_notrack=True,
                                tracking_disable=True,
                                mail_activity_automation_skip=True,
                                no_mail_to_thread=True,
                                calendar_no_videocall=True,
                                no_mail_to_attendees=True,
                            ).create(leave_vals)
                            # If successful, redirect
                            return request.redirect('/my/employee-portal/time-off?created=1')
                        except Exception as e2:
                            error_msg = f"Permission error: Please contact your administrator to grant access to create leave requests."
                    
                    # If it's a ValidationError about overlapping dates, skip the date check and retry
                    if isinstance(ve, ValidationError) and ('overlap' in error_msg.lower() or 'already booked' in error_msg.lower()):
                        try:
                            # Retry with date check skipped
                            leave_request = request.env['hr.leave'].sudo().with_context(
                                leave_skip_date_check=True,
                                leave_skip_state_check=True,
                                mail_create_nolog=True,
                                mail_create_nosubscribe=True,
                                mail_notrack=True,
                                tracking_disable=True,
                                mail_activity_automation_skip=True,
                            ).create(leave_vals)
                            # If successful, redirect
                            return request.redirect('/my/employee-portal/time-off?created=1')
                        except Exception as e2:
                            # If it still fails, show the original error
                            pass
                    
                    values.update({
                        'error': error_msg,
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("odoo_portal.employee_portal_time_off_create", values)
                except Exception as e:
                    error_msg = str(e)
                    if 'constraint' in error_msg.lower() or 'check' in error_msg.lower():
                        error_msg = 'Invalid date range. Please ensure the end date is after the start date.'
                    
                    values.update({
                        'error': f'Error creating leave request: {error_msg}',
                        'employee': employee,
                        'leave_types': leave_types,
                        'page_name': 'employee_portal_time_off_create',
                    })
                    return request.render("odoo_portal.employee_portal_time_off_create", values)
                
                # Redirect to time off page with success message
                return request.redirect('/my/employee-portal/time-off?created=1')
                
            except Exception as e:
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
                return request.render("odoo_portal.employee_portal_time_off_create", values)
        
        values.update({
            'employee': employee,
            'leave_types': leave_types,
            'page_name': 'employee_portal_time_off_create',
        })
        return request.render("odoo_portal.employee_portal_time_off_create", values)

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
            
            # Custom attachment fields removed - not in default Odoo
            # This function is only for custom Many2many attachment fields which don't exist in default Odoo
            # Return error since these fields are not available
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

