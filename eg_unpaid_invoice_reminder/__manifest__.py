{
    'name': 'Unpaid Invoice Reminder',
    'version': '17.0',
    'category': 'Account',
    'summary': 'Unpaid Invoice Reminder',
    'author': 'Amr Gebil',
    'website': 'https://www.linkedin.com/in/amr-gebil-557a9024a/',
    'depends': ['account'],
    
    'data': [
        'data/data.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
