# -*- coding: utf-8 -*-
{
    'name': 'UWE Contact Portal User',
    'summary': 'Smart button on contact form to create or open Employee Portal User',
    'description': 'Adds a smart button on res.partner to create an Employee Portal User directly from the contact form.',
    'author': 'UWE',
    'category': 'Portal',
    'version': '17.0.1.0.0',
    'depends': ['base', 'contacts', 'uwe_portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
