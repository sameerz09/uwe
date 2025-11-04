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
    number_of_working_hours = fields.Float(string="Number of Working Hours",
                                           help="Total number of working hours (for hourly contracts)")
    total_working_hours = fields.Float(string="Total Working Hours",
                                       help="Total working hours including regular and overtime hours")
    hourly_rate = fields.Monetary(string="Hourly Rate",
                                 currency_field='currency_id',
                                 help="Hourly rate for the employee")
    hourly_wage = fields.Monetary(string="Hourly Wage",
                                 currency_field='currency_id',
                                 compute="_compute_hourly_wage",
                                 store=True,
                                 help="Hourly Wage calculated as Hourly Rate × Total Working Hours, converted to company currency (visible when Wage Type is Hourly)")
    total_amount_foreign_currency = fields.Monetary(string="Total Amount (Foreign Currency)",
                                                     currency_field='foreign_currency_id',
                                                     compute="_compute_total_amount_foreign_currency",
                                                     store=True,
                                                     help="Total amount calculated as Hourly Rate × Total Working Hours in foreign currency (visible when Wage Type is Hourly)")

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

    @api.depends('hourly_rate', 'total_working_hours', 'wage_type', 'foreign_currency_id')
    def _compute_hourly_wage(self):
        """
        Compute hourly wage for hourly contracts.
        Formula: (Hourly Rate in Foreign Currency × Total Working Hours) converted to Company Currency
        Only calculated when wage_type is 'hourly'
        Also updates wage field to equal hourly_wage for hourly contracts
        """
        for contract in self:
            if contract.wage_type == 'hourly' and contract.foreign_currency_id:
                company = contract.company_id or self.env.company
                company_currency = company.currency_id
                
                if company_currency:
                    # Get hourly_rate in foreign currency
                    hourly_rate_foreign = contract.hourly_rate or 0.0
                    total_hours = contract.total_working_hours or 0.0
                    
                    # Calculate total in foreign currency
                    total_in_foreign_currency = hourly_rate_foreign * total_hours
                    
                    if total_in_foreign_currency > 0:
                        # Check if currencies are the same for 1:1 conversion
                        if contract.foreign_currency_id == company_currency:
                            # 1:1 conversion when currencies are the same
                            contract.hourly_wage = total_in_foreign_currency
                            contract.wage = contract.hourly_wage
                        else:
                            # Convert from foreign currency to company currency
                            conversion_date = fields.Date.today()
                            try:
                                hourly_wage_company_currency = contract.foreign_currency_id._convert(
                                    total_in_foreign_currency,
                                    company_currency,
                                    company,
                                    conversion_date
                                )
                                contract.hourly_wage = hourly_wage_company_currency
                                # Update wage field to equal hourly_wage
                                contract.wage = contract.hourly_wage
                            except Exception:
                                # If conversion fails, use raw calculation
                                contract.hourly_wage = total_in_foreign_currency
                                contract.wage = contract.hourly_wage
                    else:
                        contract.hourly_wage = 0.0
                        if contract.wage_type == 'hourly':
                            contract.wage = 0.0
                else:
                    # If no company currency, calculate directly
                    hourly_rate = contract.hourly_rate or 0.0
                    total_hours = contract.total_working_hours or 0.0
                    contract.hourly_wage = hourly_rate * total_hours
                    # Update wage field to equal hourly_wage
                    contract.wage = contract.hourly_wage
            else:
                contract.hourly_wage = 0.0
    
    @api.depends('hourly_rate', 'total_working_hours', 'wage_type', 'foreign_currency_id')
    def _compute_total_amount_foreign_currency(self):
        """
        Compute total amount in foreign currency for hourly contracts.
        Formula: Hourly Rate × Total Working Hours (in foreign currency)
        Only calculated when wage_type is 'hourly' and foreign_currency_id is set
        """
        for contract in self:
            if contract.wage_type == 'hourly' and contract.foreign_currency_id:
                hourly_rate = contract.hourly_rate or 0.0
                total_hours = contract.total_working_hours or 0.0
                contract.total_amount_foreign_currency = hourly_rate * total_hours
            else:
                contract.total_amount_foreign_currency = 0.0
    
    @api.onchange('hourly_wage', 'wage_type')
    def _onchange_hourly_wage_update_wage(self):
        """
        Update wage field to equal hourly_wage when wage_type is 'hourly'
        """
        if self.wage_type == 'hourly':
            self.wage = self.hourly_wage or 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Update wage from hourly_wage on create if wage_type is hourly
        """
        contracts = super().create(vals_list)
        for contract in contracts:
            if contract.wage_type == 'hourly' and contract.hourly_wage:
                contract.wage = contract.hourly_wage
        return contracts
    
    def write(self, vals):
        """
        Update wage from hourly_wage on write if wage_type is hourly
        """
        result = super().write(vals)
        if 'hourly_wage' in vals or 'wage_type' in vals:
            for contract in self:
                if contract.wage_type == 'hourly' and contract.hourly_wage:
                    contract.write({'wage': contract.hourly_wage})
        return result


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
        
        # Check if currencies are the same - if so, use 1:1 conversion
        same_currency = (self.foreign_currency_id == company_currency)
        
        # Get today's date for exchange rate
        conversion_date = fields.Date.today()
        
        # Initialize updates dictionary
        updates = {}
        
        # Mapping of foreign currency fields to original fields
        # Only include fields that exist on the contract model
        # Note: 'wage' will be handled separately if wage_type is 'hourly'
        field_mapping = {
            'foreign_food_allowance': 'food_allowance',
            'foreign_commission_allowance': 'commission_allowance',
            'foreign_off_deduction': 'off_deduction',
            'foreign_penalty_deduction': 'penalty_deduction',
        }
        
        # Get contract fields once for all checks
        contract_fields = self._fields.keys()
        
        # Allowance fields - try both standard and UAE localization field names
        # UAE localization uses l10n_ae_ prefix for these fields (e.g., l10n_ae_housing_allowance)
        allowance_fields = {
            'foreign_housing_allowance': ['l10n_ae_housing_allowance', 'housing_allowance'],
            'foreign_transportation_allowance': ['l10n_ae_transportation_allowance', 'transportation_allowance'],
            'foreign_other_allowances': ['l10n_ae_other_allowances', 'other_allowances'],
        }
        
        # Add allowance fields to mapping - try UAE localization names first, then standard names
        for foreign_field, possible_original_fields in allowance_fields.items():
            for original_field in possible_original_fields:
                if original_field in contract_fields:
                    field_mapping[foreign_field] = original_field
                    break  # Use the first matching field name found
        
        # Handle wage field based on wage_type
        # If hourly, calculate from hourly_rate (in foreign currency) × total_working_hours
        # Otherwise, use foreign_wage
        # Note: Wage conversion is optional - other fields can still be converted even if wage fields are missing
        if self.wage_type == 'hourly':
            # For hourly contracts, use hourly_rate (in foreign currency) × total_working_hours
            # Then convert the result to company currency and update wage
            hourly_rate_foreign = self.hourly_rate or 0.0
            total_hours = self.total_working_hours or 0.0
            
            if hourly_rate_foreign > 0 and total_hours > 0:
                try:
                    # Calculate total in foreign currency: hourly_rate × total_working_hours
                    total_in_foreign_currency = hourly_rate_foreign * total_hours
                    
                    if total_in_foreign_currency > 0:
                        # Convert from foreign currency to company currency
                        if same_currency:
                            # 1:1 conversion when currencies are the same
                            converted_wage = total_in_foreign_currency
                        else:
                            converted_wage = self.foreign_currency_id._convert(
                                total_in_foreign_currency,
                                company_currency,
                                company,
                                conversion_date
                            )
                        updates['wage'] = converted_wage
                except Exception as e:
                    # Log error but don't prevent other fields from converting
                    pass  # Allow other fields to convert even if wage conversion fails
        else:
            # For non-hourly contracts, convert foreign_wage to company currency
            if self.foreign_wage and self.foreign_wage > 0:
                try:
                    if same_currency:
                        # 1:1 conversion when currencies are the same
                        converted_wage = self.foreign_wage
                    else:
                        converted_wage = self.foreign_currency_id._convert(
                            self.foreign_wage,
                            company_currency,
                            company,
                            conversion_date
                        )
                    updates['wage'] = converted_wage
                except Exception as e:
                    # Log error but don't prevent other fields from converting
                    pass  # Allow other fields to convert even if wage conversion fails
        
        # Additional optional fields that may exist in other modules
        # Check if they exist before adding to mapping
        optional_fields = {
            # Add any other optional fields here if needed in the future
        }
        
        # Add optional fields to mapping if they exist on the model
        for foreign_field, original_field in optional_fields.items():
            if original_field in contract_fields:
                field_mapping[foreign_field] = original_field
        
        # Convert and update each field
        for foreign_field, original_field in field_mapping.items():
            foreign_value = getattr(self, foreign_field, 0.0)
            
            if foreign_value and foreign_value > 0:
                try:
                    # Convert foreign currency to company currency
                    if same_currency:
                        # 1:1 conversion when currencies are the same
                        converted_amount = foreign_value
                    else:
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
            # Show notification and reload the form to display updated values
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conversion Complete'),
                    'message': _('Original fields have been updated based on foreign currency values and exchange rates.'),
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                }
            }
        else:
            # Provide more specific error message based on wage_type
            if self.wage_type == 'hourly':
                raise UserError(_(
                    "No foreign currency values found to convert. "
                    "For hourly contracts, please enter:\n"
                    "- Hourly Rate (in foreign currency)\n"
                    "- Total Working Hours\n"
                    "And optionally: Foreign Food Allowance, Commission Allowance, Off Deduction, Penalty Deduction, etc."
                ))
            else:
                raise UserError(_(
                    "No foreign currency values found to convert. "
                    "Please enter at least one of the following:\n"
                    "- Wage (Foreign Currency) for non-hourly contracts\n"
                    "- Foreign Food Allowance\n"
                    "- Foreign Commission Allowance\n"
                    "- Foreign Off Deduction\n"
                    "- Foreign Penalty Deduction\n"
                    "Or any other foreign currency allowance/deduction fields."
                ))
