
from odoo import models, fields, api


class RetailerShop(models.Model):
    _name = 'my_app.shop'
    _description = 'Retailer Shop'

    name = fields.Char(
        string='Retailer Shop Name',
        required=True,
    )

    product_ids = fields.One2many(
        'my_app.product',
        'shop_id',
        string='Products',
    )


class RetailerProduct(models.Model):
    _name = 'my_app.product'
    _description = 'Retailer Product'

    shop_id = fields.Many2one(
        'my_app.shop',
        string='Retailer Shop',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Inventory Product',
        required=True,
        ondelete='restrict',
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )

    rate = fields.Float(
        string='Unit Price',
        default=0.0,
        required=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.rate = line.product_id.lst_price
            else:
                line.rate = 0.0
