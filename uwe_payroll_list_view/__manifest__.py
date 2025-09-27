# -*- coding: utf-8 -*-
{
    'name': 'UWE Payroll List View',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Customize payroll list view for UWE',
    'author': 'University of Wisconsin',
    'depends': ['hr_payroll'],
    'data': [
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
