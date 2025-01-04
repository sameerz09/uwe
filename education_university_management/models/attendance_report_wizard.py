from odoo import models, fields, api, _
import xlsxwriter
import io
import base64


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'


    period_selection = fields.Selection([
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('last_3_months', 'Last 3 Months'),
        ('custom', 'Custom Period')
    ], string='Period', required=True, default='this_month')
    subject_id = fields.Many2one('university.subject', string='Subject', required=True)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')

    @api.onchange('period_selection')
    def _onchange_period_selection(self):
        if self.period_selection != 'custom':
            self.date_from = False
            self.date_to = False


    def generate_report(self):
        data = {
            'period_selection': self.period_selection,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        print(data)
        # return self.env.ref('education_university_management.attendance_report_action').report_action(self, data=data)
        excel_data = self._generate_excel_data()
        encoded_data = base64.b64encode(excel_data).decode('utf-8')
        report_name = 'attendance_report.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': report_name,
            'type': 'binary',
            'datas': encoded_data,
            'store_fname': report_name,
            'res_model': 'attendance.report.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def _generate_excel_data(self):
        # Create an in-memory output file for the Excel data.
        output = io.BytesIO()

        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Attendance Report')

        # Define a format for the header cells.
        bold_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
        text_format = workbook.add_format({'align': 'center', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#BFBFBF', 'border': 1, 'font_size': 14})
        date_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#BFBFBF', 'border': 1, 'font_size': 12})

        # Write headers
        worksheet.merge_range('B1:K1', 'SUBJECT / COURSE:', bold_format)
        worksheet.merge_range('L1:Z1', 'NetWork', text_format)

        # Merge and add the second row (TIME:)
        worksheet.merge_range('AA1:AB1', 'TIME:', bold_format)
        # worksheet.merge_range('AC1:AF1', '06-07:30:30 Sun, Tue, Thu', text_format)

        # Merge and add the third row (GROUP and LOCATION:)
        worksheet.merge_range('B2:C2', 'GROUP:', bold_format)
        worksheet.merge_range('D2:K2', self.subject_id.name, text_format)

        # worksheet.merge_range('L2:M2', 'LOCATION:', bold_format)
        # worksheet.merge_range('N2:Z2', 'Online', text_format)

        # Merge and add the Date (July 2024)
        worksheet.merge_range('AH1:AK2', 'July\n2024', header_format)

        # Set column widths to match the layout
        worksheet.set_column('A:A', 1)    # Empty Column
        worksheet.set_column('B:B', 20)   # Subject / Course
        worksheet.set_column('C:Z', 3)    # Merged Cells
        worksheet.set_column('AA:AF', 10) # Time
        worksheet.set_column('AG:AK', 5)  # Date
        # Write data
        # worksheet.write('A2', dict(self._fields['period_selection'].selection).get(self.period_selection))

        # if self.period_selection == 'custom':
        #     worksheet.write('B2', str(self.date_from))
        #     worksheet.write('C2', str(self.date_to))

        # Close the workbook and return the Excel data.
        workbook.close()
        output.seek(0)
        return output.read()
