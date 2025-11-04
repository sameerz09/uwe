# -*- coding: utf-8 -*-
{
    'name': 'Student Certificates',
    'summary': 'Send Student Registration Certificate',
    'description': """
        This module allows sending student registration certificates via email.
        Features:
        - Certificate fields for passport, Emirati ID, program, and academic year
        - PDF certificate generation
        - Email sending functionality
    """,
    'author': 'UWE',
    'category': 'Education',
    'version': '17.0.1.0.0',
    'depends': ['education_university_management', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'reports/student_certificate_report.xml',
        'wizard/certificate_wizard_view.xml',
        'views/university_student_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

