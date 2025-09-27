# -*- coding: utf-8 -*-
{
    'name': 'UWE Simple Payroll',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Simple payroll list view for UWE',
    'author': 'University of Wisconsin',
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_views.xml',
        'wizard/payslip_import_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}