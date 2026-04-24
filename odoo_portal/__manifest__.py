# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo Portal Models
#    Copyright (C) 2025 Odoo Box
#
###############################################################################

{
    'name': 'Odoo Portal Models',
    'summary': """Res Users Portal Module - Employee Portal User Type""",
    'description': """Extends res.users to add Employee Portal User type for employees with portal access""",
    'author': "Odoo Box",
    'website': 'https://www.odoobox.com',
    'category': 'Portal',
    'version': '17.0.1.0.0',
    'depends': ['base', 'portal', 'hr', 'hr_holidays', 'hr_attendance', 'hr_payroll', 'website', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_leave_security.xml',
        'data/res_groups_data.xml',
        'views/employee_portal_templates.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
