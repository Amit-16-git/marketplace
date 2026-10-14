
{
    'name': 'My_App',
    'version': '20.0.1.0.0',
    'summary': 'Retailer Order and Department Workflow Management',
    'author': 'Agile',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'base',
        'product',
        'stock',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.access.csv',

        # Order numbering
        'data/sequence.xml',

        # Retailer and order views
        'views/my_app_views.xml',
        'views/order_views.xml',

        # Manager dashboard action and menu
        'views/dashboard_views.xml',
    ],
    'application': True,
    'installable': True,
}
