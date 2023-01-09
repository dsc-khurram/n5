# -*- coding: utf-8 -*-
{
    'name': "Manufacturing",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "ERISP (Pvt) Ltd.",
    'website': "https://erisp.net",

    'category': 'Manufacturing',
    'version': '0.1',

    'depends':  ['mrp','stock'],

   'auto_install': False, 
    'images': [], 
    'data': [
        'security/ir.model.access.csv',
        'wizards/mrp_wizard.xml',
        'wizards/stock_wizard.xml',
        'views/mrp_extension.xml',
        'views/product.xml',
        'reports/mrp_reports.xml',
    ], 
    'installable': True, 
    'description': ''
} 