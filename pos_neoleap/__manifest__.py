# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Neoleap',
    'version': '17.0',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a Neoleap payment terminal',
    'author': "SST",
    'website': "https://my-sst.com/",
    'data': [
        'views/pos_payment_method_views.xml',
        'views/pos_order.xml',
    ],
    'depends': [
        'point_of_sale',
        # 'pos_iot',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_neoleap/static/src/js/PaymentScreen.js',
            'pos_neoleap/static/src/js/Chrome.js',
            'pos_neoleap/static/src/js/payment_neoleap.js',
            'pos_neoleap/static/src/js/models.js',
            'pos_neoleap/static/src/xml/PaymentScreen.xml',
            'pos_neoleap/static/src/scss/pos.scss',
        ],
    }
}
