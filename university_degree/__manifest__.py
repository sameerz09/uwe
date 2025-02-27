# -*- coding: utf-8 -*-
{
    'name': 'University Degree',
    'version': '17.0.3.0.5',
    'category': 'University',
    'summary': """
        University Degree
    """,
    'description': """
        Module for create University Degree .
    """,
    'author': 'Amr Gebil',
    'depends': [
        'education_university_management',

    ],
    'data': [
        'reports/university_degree.xml',  # Ensure the XML file exists and is valid
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
