# -*- coding: utf-8 -*-
{
    'name': 'UWE Sign',
    'summary': 'Electronic document signing for employees via portal',
    'description': 'Allows employees to sign documents electronically through the portal with Auto, Draw, or Upload signature modes.',
    'author': 'UWE',
    'category': 'Human Resources',
    'version': '17.0.1.0.0',
    'depends': ['base', 'portal', 'hr', 'mail', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/sign_backend_views.xml',
        'views/sign_portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'uwe_sign/static/src/css/sign.css',
            'uwe_sign/static/src/js/sign_dialog.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
