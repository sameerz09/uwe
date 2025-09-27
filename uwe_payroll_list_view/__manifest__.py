# -*- coding: utf-8 -*-
{
    'name': "UWE Payroll List View",
    'summary': "Payroll list view for UWE",
    'description': "Custom payroll list view for UWE",
    'author': "University of Wisconsin",
    'website': "https://www.uw.edu",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['base', 'hr_payroll'],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}