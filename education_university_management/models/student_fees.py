from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class StudentFees(models.Model):
    _name = 'student.fees'
    _description = 'Student Fees'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('university.student', string='Student', required=True)
    student_no = fields.Char(related='student_id.student_no', string='Student No', store=True)
    fee_structure_id = fields.Many2one('fee.structure', string='Fee Structure', required=True)
    student_fees_line_ids = fields.One2many('student.fees.line', 'student_fees_id', string='Student Fees Line', help="Student Fees Line")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft', help="Status of attendance")
    is_fees_created = fields.Boolean(string='Fees Created',
                                           help="Is Fees created or not")
    academic_year_id = fields.Many2one('university.academic.year', string='Academic Year', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    invoices_count = fields.Integer(compute='_compute_invoices_count', string='Invoices Count')

    def _compute_invoices_count(self):
        for rec in self:
            rec.invoices_count = self.env['account.move'].search_count([('student_fees_id', '=', rec.id)])
            print('Invoices Count: ', rec.invoices_count)
            print('Invoices Count: ', rec.invoices_count)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['university.student'].browse(vals['student_id']).name + ' - ' + self.env['fee.structure'].browse(vals['fee_structure_id']).name + ' - ' + self.env['university.academic.year'].browse(vals['academic_year_id']).name
        return super(StudentFees, self).create(vals)
    
    def action_student_fees_done(self):
        self.state = 'done'

    # def action_create_fees_line(self):
    #     if self.search_count([('student_id', '=', self.student_id.id), ('fee_structure_id', '=', self.fee_structure_id.id), ('state', '=', 'done')]) == 1:
    #         raise ValidationError(
    #             _('Fees for this student on this fee structure already exists.'))
    #     if len(self.fee_structure_id.structure_line_ids) < 1:
    #         raise UserError(_('There are no fees in this Fee Structure'))
    #     due_date = self.date
    #     for fee in self.fee_structure_id.structure_line_ids:
    #         if not fee.fee_type_id.is_registraion_fees:
    #             # make the due date the 28 day of the month
    #             due_date = fields.Date.to_string(fields.Date.from_string(due_date).replace(day=28))
    #             if fee.fee_type_id.due_month:
    #                 # make the month of the due date the same as the due month, the value of the due month is the month number
    #                 due_date = fields.Date.to_string(fields.Date.from_string(due_date).replace(month=int(fee.fee_type_id.due_month)))
    #         self.env['student.fees.line'].create(
    #             {
    #              'student_fees_id': self.id,
    #              'fee_type_id': fee.fee_type_id.id,
    #              'is_registraion_fees': fee.is_registraion_fees,
    #              'fee_description': "fee.fee_description",
    #              'due_amount': fee.due_amount,
    #                 'due_date': due_date,
    #             })
    #         due_date = fields.Date.to_string(fields.Date.from_string(due_date) + relativedelta(months=1))
    #     self.is_fees_created = True

    def action_create_fees_line(self):
        if self.search_count(
                [('student_id', '=', self.student_id.id), ('fee_structure_id', '=', self.fee_structure_id.id),
                 ('state', '=', 'done')]) == 1:
            raise ValidationError(
                _('Fees for this student on this fee structure already exist.'))
        if len(self.fee_structure_id.structure_line_ids) < 1:
            raise UserError(_('There are no fees in this Fee Structure'))

        due_date = self.date
        sequence_number = 1  # Start numbering from 1 for non-registration fees

        for index, fee in enumerate(self.fee_structure_id.structure_line_ids):
            if fee.fee_type_id.is_registraion_fees:
                # First line description should always be "Registration Fees"
                description = "Registration Fees"
            else:
                # Other lines should follow the sequence 1, 2, 3, ...
                description = str(sequence_number)
                sequence_number += 1

                # Adjust due date for non-registration fees
                due_date = fields.Date.to_string(fields.Date.from_string(due_date).replace(day=28))
                if fee.fee_type_id.due_month:
                    due_date = fields.Date.to_string(
                        fields.Date.from_string(due_date).replace(month=int(fee.fee_type_id.due_month)))

            # Create the student fee line
            self.env['student.fees.line'].create({
                'student_fees_id': self.id,
                'fee_type_id': fee.fee_type_id.id,
                'is_registraion_fees': fee.is_registraion_fees,
                'fee_description': description,  # Use the dynamically set description
                'due_amount': fee.due_amount,
                'due_date': due_date,
            })

            # Increment the due date for the next fee line
            due_date = fields.Date.to_string(fields.Date.from_string(due_date) + relativedelta(months=1))

        self.is_fees_created = True

    def action_delete_fees_line(self):
        self.student_fees_line_ids.unlink()
        self.is_fees_created = False

    def action_create_invoices(self):
        # create invoice for each student fees line
        # sales_account = self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)], limit=1)
        sales_account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        for line in self.student_fees_line_ids:
            invoice = self.env['account.move'].create({
                'partner_id': self.student_id.partner_id.id,
                'invoice_date': fields.Date.today(),
                'move_type': 'out_invoice',
                'student_fees_id': self.id,
                'invoice_date_due': line.due_date,
                'invoice_origin': self.name,
                'journal_id': journal.id,
                'invoice_line_ids': [(0, 0, {
                    'name': line.fee_description,
                    'quantity': 1,
                    'price_unit': line.due_amount,
                    'account_id': sales_account.id,
                    'partner_id': self.student_id.partner_id.id,
                })],
            })
            invoice.action_post()
            # line.invoice_id = invoice.id

    def action_reset_draft(self):
        self.state = 'draft'

    def action_view_invoices(self):
        return {
            'name': 'Account Moves',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('student_fees_id', '=', self.id)],
        }

    # for adding log note
    def add_log_note(self, log_message):
        # Ensure this method is called on a single record
        if len(self) != 1:
            raise ValueError("This method should be called on a single record.")
        # Add the log note to the chatter of the specific record
        self.message_post(
            body=log_message,
            message_type='comment',
            subtype_xmlid='mail.mt_note'  # Ensures it's a log note
        )


class StudentAccountMove(models.Model):
    _inherit = 'account.move'

    # override create method to add student_fees_id
    @api.model
    def create(self, vals):
        print("###################")
        print('vals: ')
        print(vals)
        result = super(StudentAccountMove, self).create(vals)
        print("###################")
        print('result: ')
        print(result)
        return result