{
    'name': 'Electronic invoice KSA - Sale, Purchase, Invoice, Credit Note, Debit Note | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode | Saudi Invoice QR Code',
    'version': '17.0.0.0',
    'sequence':1,
    'category': 'Accounting',
    'summary': 'Electronic invoice KSA - Sale, Purchase, Invoice, Credit Note, Debit Note | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode',
    
    'description': """
     Electronic invoice KSA - Sale, Purchase, Invoice, Credit Note, Debit Note | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode
     Using this module you can print Saudi electronic invoice for Sale, Purchase, Invoice and  POS Order Invoice Report.
     According to Saudi Government QR code with Display Saudi Tax detials, Customer Name, Customer Vat, Invoice Date, Total of VAT, Totaol of Amount.
     """,
    "price": 25,
    'currency': 'EUR',
    "author" : "MAISOLUTIONSLLC",
    'sequence': 1,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'depends': ['sale_management','purchase', 'account','point_of_sale'],

    'data': [
        'report/vat_invoice_report_print_old2.xml',
        'report/vat_report_action_call.xml',
        # 'report/vat_sale_report_print.xml',
        'report/vat_purchase_report_print.xml',
        'report/simpli_vat_invoice_report.xml',
        'report/simpli_vat_invoice_report_pos.xml',
        'views/sale_purchase_invoice_view.xml',
        # 'report/invoice_default_attach.xml',
    ],
    "live_test_url" : "https://youtu.be/ZgcCGBkZV1U",    
    'images': ['static/description/main_screenshot.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}





