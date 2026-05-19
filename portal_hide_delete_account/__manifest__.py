# -*- coding: utf-8 -*-
{
    'name': 'Portal Hide Delete Account',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Hide the Delete Account section on the portal security page',
    'description': """
        Removes the "Delete Account" block from Connection & Security (/my/security)
        for all users, including portal users.
    """,
    'author': 'Custom',
    'depends': ['portal'],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
