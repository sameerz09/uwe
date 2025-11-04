# -*- coding: utf-8 -*-
{
    'name': 'Employee Certificates',
    'summary': 'Send Employee Registration Certificate',
    'description': """
        This module allows sending employee registration certificates via email.
        Features:
        - Certificate fields for passport, Emirati ID, program, and academic year
        - PDF certificate generation
        - Email sending functionality
    """,
    'author': 'UWE',
    'category': 'Human Resource',
    'version': '17.0.1.0.2',
    'depends': ['hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'reports/employee_certificate_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

