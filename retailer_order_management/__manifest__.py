
{
    'name': 'Retailer Order Management',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Sales',
    'summary': 'Manage retailer orders across order taking, inventory, and shipping departments',
    'description': """
        Retailer Order Management
        =========================
        - Create and manage retailer orders.
        - Track order status across departments.
        - Manage order products and totals.
        - Track shipping and delivery dates.
        - Provide a retailer order dashboard.
        - Define department security groups.
    """,
    'depends': [
        'base',
        'contacts',
        'product',
        'sale_management',
        'stock',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Sequences
        'data/sequence.xml',

        # Views and menus
        'views/retailer_order_views.xml',
        'views/retailer_order_dashboard.xml',
        'views/retailer_order_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}