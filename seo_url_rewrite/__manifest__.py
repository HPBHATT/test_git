{
    # App information
    'name': 'Seo URL Rewrite',
    'category': 'Website',
    'version': '13.0.0.0.0',
    'license': 'OPL-1',
    'summary': '',
    'description': """  """,

    # Dependencies
    'depends': [
        'website_sale'
    ],

    # Views
    'data': [        
        'security/ir.model.access.csv',
        'templates/template.xml',
        'views/product_public_category.xml',
        'views/product_template.xml',
        'views/website.xml',
        'views/res_config_settings.xml',
    ],

    # Author
    'author': '',
    'website': '',
    'maintainer': '',

    # Technical
    'installable': True,
    'auto_install': False,
    'application' : True,

}