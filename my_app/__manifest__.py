
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
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/my_app_views.xml',
        'views/order_views.xml',
        'views/inventory_views.xml',
        'views/dashboard_views.xml',
    ],

    'application': True,
    'installable': True,
}