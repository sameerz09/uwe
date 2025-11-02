# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class PayrollDashboard(models.TransientModel):
    _name = 'payroll.dashboard'
    _description = 'Payroll Analytics Dashboard'

    currency_id = fields.Many2one('res.currency', string="Currency", 
                                   default=lambda self: self.env.company.currency_id,
                                   help="Select currency for payroll insights")
    date_from = fields.Date(string="From Date", 
                            default=lambda self: fields.Date.today().replace(day=1),
                            required=True)
    date_to = fields.Date(string="To Date", 
                          default=lambda self: fields.Date.today(),
                          required=True)
    department_ids = fields.Many2many('hr.department', string="Departments",
                                       help="Filter by departments")
    
    # Computed Fields for Dashboard Stats
    total_employees = fields.Integer(string="Total Employees", compute="_compute_dashboard_stats")
    active_contracts = fields.Integer(string="Active Contracts", compute="_compute_dashboard_stats")
    total_payroll_amount = fields.Monetary(string="Total Payroll Amount", 
                                           currency_field='currency_id',
                                           compute="_compute_dashboard_stats")
    average_salary = fields.Monetary(string="Average Salary", 
                                     currency_field='currency_id',
                                     compute="_compute_dashboard_stats")
    total_allowances = fields.Monetary(string="Total Allowances", 
                                       currency_field='currency_id',
                                       compute="_compute_dashboard_stats")
    total_deductions = fields.Monetary(string="Total Deductions", 
                                      currency_field='currency_id',
                                       compute="_compute_dashboard_stats")
    net_payroll = fields.Monetary(string="Net Payroll", 
                                  currency_field='currency_id',
                                  compute="_compute_dashboard_stats")
    
    # Monthly Breakdown
    monthly_payroll_data = fields.Text(string="Monthly Payroll Data", 
                                        compute="_compute_monthly_data",
                                        readonly=True)
    
    # Department Breakdown
    department_payroll_data = fields.Text(string="Department Payroll Data",
                                          compute="_compute_department_data",
                                          readonly=True)
    
    # Contract Type Breakdown
    contract_type_data = fields.Text(string="Contract Type Data",
                                     compute="_compute_contract_type_data",
                                     readonly=True)

    @api.depends('currency_id', 'date_from', 'date_to', 'department_ids')
    def _compute_dashboard_stats(self):
        """Compute main dashboard statistics"""
        for dashboard in self:
            domain = [
                ('state', '=', 'open'),
                ('date_start', '<=', dashboard.date_to),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', dashboard.date_from)
            ]
            
            if dashboard.department_ids:
                domain.append(('department_id', 'in', dashboard.department_ids.ids))
            
            contracts = self.env['hr.contract'].search(domain)
            
            dashboard.total_employees = len(contracts.mapped('employee_id'))
            dashboard.active_contracts = len(contracts)
            
            total_wage = 0.0
            total_allowances = 0.0
            total_deductions = 0.0
            
            company_currency = dashboard.currency_id or self.env.company.currency_id
            
            for contract in contracts:
                # Get wage (convert if needed)
                wage = contract.wage or 0.0
                if contract.company_id.currency_id != company_currency:
                    try:
                        wage = contract.company_id.currency_id._convert(
                            wage, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                total_wage += wage
                
                # Get allowances (food, commission)
                food_allowance = contract.food_allowance or 0.0
                if contract.company_id.currency_id != company_currency:
                    try:
                        food_allowance = contract.company_id.currency_id._convert(
                            food_allowance, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                commission = getattr(contract, 'commission_allowance', 0.0) or 0.0
                if contract.company_id.currency_id != company_currency:
                    try:
                        commission = contract.company_id.currency_id._convert(
                            commission, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                total_allowances += food_allowance + commission
                
                # Get deductions
                off_deduction = getattr(contract, 'off_deduction', 0.0) or 0.0
                penalty_deduction = getattr(contract, 'penalty_deduction', 0.0) or 0.0
                
                if contract.company_id.currency_id != company_currency:
                    try:
                        off_deduction = contract.company_id.currency_id._convert(
                            off_deduction, company_currency, contract.company_id, fields.Date.today())
                        penalty_deduction = contract.company_id.currency_id._convert(
                            penalty_deduction, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                total_deductions += off_deduction + penalty_deduction
            
            dashboard.total_payroll_amount = total_wage + total_allowances - total_deductions
            dashboard.total_allowances = total_allowances
            dashboard.total_deductions = total_deductions
            dashboard.net_payroll = dashboard.total_payroll_amount
            dashboard.average_salary = total_wage / len(contracts) if contracts else 0.0

    @api.depends('currency_id', 'date_from', 'date_to')
    def _compute_monthly_data(self):
        """Compute monthly payroll breakdown"""
        for dashboard in self:
            company_currency = dashboard.currency_id or self.env.company.currency_id
            monthly_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
            
            # Get payslips in the date range
            payslips = self.env['hr.payslip'].search([
                ('date_from', '>=', dashboard.date_from),
                ('date_to', '<=', dashboard.date_to),
                ('state', '=', 'done')
            ])
            
            for payslip in payslips:
                month_key = payslip.date_from.strftime('%Y-%m')
                amount = payslip.net_wage or 0.0
                
                if payslip.currency_id != company_currency:
                    try:
                        amount = payslip.currency_id._convert(
                            amount, company_currency, payslip.company_id, payslip.date_from)
                    except:
                        pass
                
                monthly_data[month_key]['amount'] += amount
                monthly_data[month_key]['count'] += 1
            
            # Format as JSON-like string for frontend
            dashboard.monthly_payroll_data = str(dict(monthly_data))

    @api.depends('currency_id', 'date_from', 'date_to', 'department_ids')
    def _compute_department_data(self):
        """Compute department-wise payroll breakdown"""
        for dashboard in self:
            company_currency = dashboard.currency_id or self.env.company.currency_id
            dept_data = defaultdict(lambda: {'amount': 0.0, 'employees': 0})
            
            domain = [
                ('state', '=', 'open'),
                ('date_start', '<=', dashboard.date_to),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', dashboard.date_from)
            ]
            
            if dashboard.department_ids:
                domain.append(('department_id', 'in', dashboard.department_ids.ids))
            
            contracts = self.env['hr.contract'].search(domain)
            
            for contract in contracts:
                dept_name = contract.department_id.name if contract.department_id else 'No Department'
                wage = contract.wage or 0.0
                
                if contract.company_id.currency_id != company_currency:
                    try:
                        wage = contract.company_id.currency_id._convert(
                            wage, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                dept_data[dept_name]['amount'] += wage
                dept_data[dept_name]['employees'] += 1
            
            dashboard.department_payroll_data = str(dict(dept_data))

    @api.depends('currency_id', 'date_from', 'date_to')
    def _compute_contract_type_data(self):
        """Compute contract type breakdown"""
        for dashboard in self:
            company_currency = dashboard.currency_id or self.env.company.currency_id
            type_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
            
            domain = [
                ('state', '=', 'open'),
                ('date_start', '<=', dashboard.date_to),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', dashboard.date_from)
            ]
            
            contracts = self.env['hr.contract'].search(domain)
            
            for contract in contracts:
                contract_type = contract.contract_type_id.name if contract.contract_type_id else 'Other'
                wage = contract.wage or 0.0
                
                if contract.company_id.currency_id != company_currency:
                    try:
                        wage = contract.company_id.currency_id._convert(
                            wage, company_currency, contract.company_id, fields.Date.today())
                    except:
                        pass
                
                type_data[contract_type]['amount'] += wage
                type_data[contract_type]['count'] += 1
            
            dashboard.contract_type_data = str(dict(type_data))

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        self._compute_dashboard_stats()
        self._compute_monthly_data()
        self._compute_department_data()
        self._compute_contract_type_data()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Dashboard Refreshed'),
                'message': _('Dashboard data has been updated.'),
                'type': 'success',
                'sticky': False,
            }
        }




