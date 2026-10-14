
from odoo import models, fields, api


class RetailerShop(models.Model):
    _name = 'my_app.shop'
    _description = 'Retailer Shop'

    # NEW FEATURE: Display the newest retailer shops first.
    # Odoo automatically maintains create_date and write_date.
    _order = 'create_date desc'

    name = fields.Char(
        string='Retailer Shop Name',
        required=True,
    )

    # NEW FEATURE: Active/Archive status for retailer shops.
    # Active retailers remain available; archived retailers can be hidden
    # from normal lists without deleting their records.
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck this to archive the retailer shop.',
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

    # EXISTING FEATURE: Automatically fill the unit price
    # when an Inventory product is selected.
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.rate = line.product_id.lst_price
            else:
                line.rate = 0.0
