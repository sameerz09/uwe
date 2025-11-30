# -*- coding: utf-8 -*-
###############################################################################
#
#    UWE Portal Models
#    Copyright (C) 2024 UWE
#
###############################################################################

{
    'name': 'UWE Portal Models',
    'summary': """Res Users Portal Module - Employee Portal User Type""",
    'description': """Extends res.users to add Employee Portal User type for employees with portal access""",
    'author': "UWE",
    'category': 'Portal',
    'version': '17.0.1.0.0',
    'depends': ['base', 'portal', 'hr', 'hr_holidays', 'hr_attendance', 'hr_payroll', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/res_groups_data.xml',
        'views/employee_portal_templates.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
