from odoo import models, fields, api


class RetailerShop(models.Model):
    _name = 'my_app.shop'
    _description = 'Retailer Shop'
    _order = 'create_date desc'

    name = fields.Char(
        string='Retailer Shop Name',
        required=True,
    )

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

    # Automatically linked order for this retailer.
    order_id = fields.Many2one(
        'my_app.order',
        string='Retailer Order',
        readonly=True,
        copy=False,
        ondelete='set null',
    )

    @api.model_create_multi
    def create(self, vals_list):
        shops = super().create(vals_list)

        # Create an order automatically for each new retailer.
        for shop in shops:
            shop._sync_retailer_order()

        return shops

    def write(self, vals):
        result = super().write(vals)

        # Sync products when the retailer's product list changes.
        if 'product_ids' in vals:
            for shop in self:
                shop._sync_retailer_order()

        return result

    def _sync_retailer_order(self):
        for shop in self:
            order_lines = [
                (0, 0, {
                    'product_id': product.product_id.id,
                    'quantity': product.quantity,
                    'rate': product.rate,
                })
                for product in shop.product_ids
            ]

            if not shop.order_id:
                order = self.env['my_app.order'].create({
                    'retailer_id': shop.id,
                    'state': 'new',
                    'order_line_ids': order_lines,
                })

                shop.order_id = order.id

            elif shop.order_id.state == 'new':
                # Update the existing New order instead of
                # creating duplicate orders for the same retailer.
                shop.order_id.write({
                    'order_line_ids': [(5, 0, 0)] + order_lines,
                })


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
