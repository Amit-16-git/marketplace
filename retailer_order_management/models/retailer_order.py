
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RetailerOrder(models.Model):
    _name = 'retailer.order'
    _description = 'Retailer Order Management'
    _order = 'create_date desc'

    # 1. Order Reference
    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    # 2. Retailer Details
    retailer_id = fields.Many2one(
        'res.partner',
        string='Retailer',
        required=True,
        domain=[('is_company', '=', True)]
    )

    order_date = fields.Date(
        string='Order Date',
        default=fields.Date.context_today,
        required=True
    )

    # 3. Employee Responsible for Taking the Order
    order_taken_by = fields.Many2one(
        'res.users',
        string='Order Taken By',
        default=lambda self: self.env.user,
        readonly=True
    )

    # 4. Products Ordered by the Retailer
    order_line_ids = fields.One2many(
        'retailer.order.line',
        'order_id',
        string='Order Products'
    )

    # 5. Total Order Amount
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True
    )

    # 6. Current Department / Order Status
    state = fields.Selection(
        [
            ('new', 'New'),
            ('processing', 'Processing'),
            ('adding_products', 'Adding Products to Cart'),
            ('ready_to_ship', 'Ready to Ship'),
            ('shipping', 'Shipping'),
            ('dispatched', 'Dispatched'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        string='Order Status',
        default='new',
        required=True,
        tracking=True
    )

    # 7. Shipping Details
    shipping_employee_id = fields.Many2one(
        'res.users',
        string='Shipping Employee'
    )

    dispatch_date = fields.Datetime(
        string='Dispatch Date'
    )

    delivery_date = fields.Datetime(
        string='Delivery Date'
    )

    # 8. Generate Unique Order Reference
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'retailer.order'
                    ) or 'New'
                )
        return super().create(vals_list)

    # 9. Calculate Total Amount
    @api.depends('order_line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(
                order.order_line_ids.mapped('subtotal')
            )

    # 10. Move Order to Inventory Processing
    def action_start_processing(self):
        for order in self:
            if order.state != 'new':
                raise ValidationError(
                    'Only new orders can start processing.'
                )
            order.state = 'processing'

    # 11. Start Adding Products to Cart
    def action_add_products(self):
        for order in self:
            if order.state != 'processing':
                raise ValidationError(
                    'Order must be in Processing status first.'
                )
            order.state = 'adding_products'

    # 12. Mark Order Ready to Ship
    def action_ready_to_ship(self):
        for order in self:
            if order.state != 'adding_products':
                raise ValidationError(
                    'Products must be added before shipping.'
                )
            if not order.order_line_ids:
                raise ValidationError(
                    'Add at least one product before proceeding.'
                )
            order.state = 'ready_to_ship'

    # 13. Start Shipping
    def action_start_shipping(self):
        for order in self:
            if order.state != 'ready_to_ship':
                raise ValidationError(
                    'Only ready-to-ship orders can be shipped.'
                )
            order.write({
                'state': 'shipping',
                'shipping_employee_id': self.env.user.id,
            })

    # 14. Mark Order as Dispatched
    def action_dispatch(self):
        for order in self:
            if order.state != 'shipping':
                raise ValidationError(
                    'Start shipping before dispatching the order.'
                )
            order.write({
                'state': 'dispatched',
                'dispatch_date': fields.Datetime.now(),
            })

    # 15. Confirm Delivery
    def action_deliver(self):
        for order in self:
            if order.state != 'dispatched':
                raise ValidationError(
                    'Only dispatched orders can be delivered.'
                )
            order.write({
                'state': 'delivered',
                'delivery_date': fields.Datetime.now(),
            })

    # 16. Cancel Order
    def action_cancel(self):
        for order in self:
            if order.state in ('dispatched', 'delivered'):
                raise ValidationError(
                    'Dispatched or delivered orders cannot be cancelled.'
                )
            order.state = 'cancelled'