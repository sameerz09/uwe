from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
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

    # Multi-Currency Fields
    foreign_currency_id = fields.Many2one('res.currency', string="Foreign Currency",
                                           help="Select a foreign currency to enter equivalent values")
    foreign_wage = fields.Monetary(string="Wage (Foreign Currency)", 
                                   currency_field='foreign_currency_id',
                                   help="Wage amount in the selected foreign currency")
    foreign_housing_allowance = fields.Monetary(string="Housing Allowance (Foreign Currency)",
                                                currency_field='foreign_currency_id',
                                                help="Housing allowance in the selected foreign currency")
    foreign_transportation_allowance = fields.Monetary(string="Transportation Allowance (Foreign Currency)",
                                                       currency_field='foreign_currency_id',
                                                       help="Transportation allowance in the selected foreign currency")
    foreign_other_allowances = fields.Monetary(string="Other Allowances (Foreign Currency)",
                                              currency_field='foreign_currency_id',
                                              help="Other allowances in the selected foreign currency")
    foreign_commission_allowance = fields.Monetary(string="Commission Allowance (Foreign Currency)",
                                                    currency_field='foreign_currency_id',
                                                    help="Commission allowance in the selected foreign currency")
    foreign_off_deduction = fields.Monetary(string="Off Deduction (Foreign Currency)",
                                            currency_field='foreign_currency_id',
                                            help="Off deduction in the selected foreign currency")
    foreign_penalty_deduction = fields.Monetary(string="Penalty Deduction (Foreign Currency)",
                                               currency_field='foreign_currency_id',
                                               help="Penalty deduction in the selected foreign currency")
    foreign_food_allowance = fields.Monetary(string="Food Allowance (Foreign Currency)",
                                            currency_field='foreign_currency_id',
                                            help="Food allowance in the selected foreign currency")

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

    def action_compute_from_foreign_currency(self):
        """
        Compute original field values from foreign currency values using exchange rates.
        Converts foreign currency amounts to company currency using current exchange rates.
        """
        self.ensure_one()
        
        if not self.foreign_currency_id:
            raise UserError(_("Please select a foreign currency first."))
        
        company = self.company_id or self.env.company
        company_currency = company.currency_id
        
        if not company_currency:
            raise UserError(_("Company currency is not set. Please configure company currency first."))
        
        if self.foreign_currency_id == company_currency:
            raise UserError(_("Foreign currency cannot be the same as company currency."))
        
        # Get today's date for exchange rate
        conversion_date = fields.Date.today()
        
        # Mapping of foreign currency fields to original fields
        # Only include fields that exist on the contract model
        field_mapping = {
            'foreign_wage': 'wage',
            'foreign_food_allowance': 'food_allowance',
            'foreign_commission_allowance': 'commission_allowance',
            'foreign_off_deduction': 'off_deduction',
            'foreign_penalty_deduction': 'penalty_deduction',
        }
        
        # Optional fields that may exist in other modules
        # Check if they exist before adding to mapping
        optional_fields = {
            'foreign_housing_allowance': 'housing_allowance',
            'foreign_transportation_allowance': 'transportation_allowance',
            'foreign_other_allowances': 'other_allowances',
        }
        
        # Add optional fields to mapping if they exist on the model
        contract_fields = self._fields.keys()
        for foreign_field, original_field in optional_fields.items():
            if original_field in contract_fields:
                field_mapping[foreign_field] = original_field
        
        # Convert and update each field
        updates = {}
        for foreign_field, original_field in field_mapping.items():
            foreign_value = getattr(self, foreign_field, 0.0)
            
            if foreign_value and foreign_value > 0:
                try:
                    # Convert foreign currency to company currency
                    converted_amount = self.foreign_currency_id._convert(
                        foreign_value,
                        company_currency,
                        company,
                        conversion_date
                    )
                    # Only update if field exists on the model
                    if original_field in contract_fields:
                        updates[original_field] = converted_amount
                except Exception as e:
                    raise UserError(_("Error converting %s: %s") % (foreign_field, str(e)))
            else:
                # If foreign field is empty or zero, keep original value unchanged
                pass  # Don't update if foreign value is not set
        
        # Update the contract with converted values
        if updates:
            self.write(updates)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conversion Complete'),
                    'message': _('Original fields have been updated based on foreign currency values and exchange rates.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No foreign currency values found to convert. Please enter foreign currency values first."))
