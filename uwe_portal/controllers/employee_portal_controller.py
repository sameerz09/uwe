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

    @http.route(['/my/employee-portal/profile'], type='http', auth="user", website=True)
    def employee_portal_profile(self, **kw):
        """Employee profile page"""
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
        
        values.update({
            'employee': employee,
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
        else:
            # Employee not found - log for debugging
            _logger.warning("Employee not found for user: %s (ID: %s)", request.env.user.name, request.env.user.id)
        
        values.update({
            'employee': employee,
            'payslips': payslips,
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

