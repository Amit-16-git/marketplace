
from odoo import models, fields


class RetailerShop(models.Model):
    _name = 'my_app.shop'
    _description = 'Retailer Shop'

    name = fields.Char(
        string='Retailer Shop Name',
        required=True
    )

    product_ids = fields.One2many(
        'my_app.product',
        'shop_id',
        string='Product List'
    )


class RetailerProduct(models.Model):
    _name = 'my_app.product'
    _description = 'Retailer Product'

    name = fields.Char(
        string='Product Name',
        required=True
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0
    )

    rate = fields.Float(
        string='Rate',
        default=0.0
    )

    shop_id = fields.Many2one(
        'my_app.shop',
        string='Retailer Shop',
        required=True,
        ondelete='cascade'
    )
