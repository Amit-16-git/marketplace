
{
    'name': 'Retailer Order Management',
    'version': '19.0.1.0.0',
    'category': 'Operations',
    'summary': 'Manage retailer orders and workflow',
    'description': """
        Manage retailer orders, order status, products,
        totals, shipping, and delivery.
    """,
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/retailer_order_views.xml',
        'views/retailer_order_dashboard.xml',
        'views/retailer_order_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}