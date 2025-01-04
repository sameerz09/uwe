# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name' :'Penalty',
    'summary': """Manage Penality to employees """,

    'description': """Manage Penality to employees""",


    'author': "UWE",
    'category': 'Human Resource',

    'depends' : ['hr','hr_contract','sale','account','hr_recruitment'],

    'data' : [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/hr_penalty_view.xml',
        'views/hr_tacher_attendance_view.xml',
        'report/report.xml',
        'report/penalty_template.xml',
        'data/ir_sequence_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_payroll_structure_data.xml',

    ],

    'installable':True,
    'auto_install':False,
}

