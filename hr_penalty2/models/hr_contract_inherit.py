from odoo import models, fields, api
from datetime import datetime
import calendar

class HrContract(models.Model):
    _inherit = 'hr.contract'

    number_of_month_days = fields.Integer(string="Number of Month Days")
    number_of_working_holidays = fields.Integer(string="Number of Working Holidays")
    eligible_days = fields.Integer(string="Eligible Days")
    holiday_working_days = fields.Integer(string="Holiday Working Days")
    overtime_hours = fields.Float(string="Overtime Hours")
    deductions = fields.Float(string="Deductions")
    overtime_per_hour_amount = fields.Float(string="Overtime Per Hour Amount")
    overtime_amount = fields.Float(string="Overtime Amount", compute="_compute_overtime_amount", store=True)
    food_allowance = fields.Float(string="Food Allowance")
    total_package = fields.Float(string="Total Package", compute="_compute_total_package", store=True)
    holiday_total_amount = fields.Float(string="Holiday Amount", compute="_compute_holiday_total_amount", store=True)
    total_variable_amount = fields.Float(string="Holiday And Overtime Amount", compute="_compute_total_variable_amount", store=True)
    net_salary = fields.Float(string="Net Salary", compute="_compute_net_salary", store=True)
    net_salary_rounded = fields.Float(string="Net Salary (Rounded)", compute="_compute_net_salary_rounded", store=True)
    off_deduction = fields.Float(string="Off Deduction")  # Renamed
    penalty_deduction = fields.Float(string="Penalty Deduction")  # New field
    commission_allowance = fields.Float(string="Commission Allowance")  # New field

    def update_number_of_month_days(self):
        today = datetime.today()
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]

        contracts = self.search([])
        for contract in contracts:
            contract.number_of_month_days = days_in_month

    @api.depends('net_salary')
    def _compute_net_salary_rounded(self):
        for contract in self:
            contract.net_salary_rounded = round(contract.net_salary or 0.0)

    @api.depends('total_package', 'total_variable_amount')
    def _compute_net_salary(self):
        for contract in self:
            contract.net_salary = (contract.total_package or 0.0) + (contract.total_variable_amount or 0.0)



    @api.depends('wage', 'food_allowance')
    def _compute_total_package(self):
        for contract in self:
            contract.total_package = (contract.wage or 0.0) + (contract.food_allowance or 0.0)

    @api.depends('total_package', 'number_of_month_days', 'holiday_working_days')
    def _compute_holiday_total_amount(self):
        for contract in self:
            if contract.holiday_working_days and contract.number_of_month_days:
                contract.holiday_total_amount = (
                    (contract.total_package / contract.number_of_month_days) * contract.holiday_working_days
                )
            else:
                contract.holiday_total_amount = 0.0

    @api.depends('overtime_per_hour_amount', 'overtime_hours')
    def _compute_overtime_amount(self):
        for contract in self:
            contract.overtime_amount = (contract.overtime_per_hour_amount or 0.0) * (contract.overtime_hours or 0.0)

    @api.depends('overtime_amount', 'holiday_total_amount')
    def _compute_total_variable_amount(self):
        for contract in self:
            contract.total_variable_amount = (contract.overtime_amount or 0.0) + (contract.holiday_total_amount or 0.0)
