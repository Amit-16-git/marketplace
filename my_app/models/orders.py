from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RetailerOrder(models.Model):
    _name = 'my_app.order'
    _description = 'Retailer Order'
    _order = 'create_date desc, id desc'

    # Automatically generated order number.
    name = fields.Char(
        string='Order Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        index=True,
    )

    # Linked retailer.
    retailer_id = fields.Many2one(
        'my_app.shop',
        string='Retailer',
        required=True,
        ondelete='restrict',
        index=True,
    )

    # Order workflow status.
    state = fields.Selection(
        [
            ('new', 'New'),
            ('checking_inventory', 'Checking Inventory'),
            ('inventory_checked', 'Inventory Checked'),
            ('processing', 'Processing Order'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold'),
            ('ready_to_ship', 'Ready to Ship'),
            ('shipped', 'Shipped'),
        ],
        string='Status',
        required=True,
        default='new',
        index=True,
    )

    # Department responsible for the order.
    department = fields.Selection(
        [
            ('inventory', 'Inventory'),
            ('processing', 'Order Processing'),
            ('shipping', 'Shipping'),
            ('management', 'Management'),
        ],
        string='Department',
        default='inventory',
        required=True,
        index=True,
    )

    # Staff member handling the order.
    assigned_user_id = fields.Many2one(
        'res.users',
        string='Assigned Staff',
        index=True,
    )

    # Order product lines.
    order_line_ids = fields.One2many(
        'my_app.order.line',
        'order_id',
        string='Order Lines',
        copy=True,
    )

    # Automatically calculated order total.
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        store=True,
    )

    # Reason for putting an order on hold.
    hold_reason = fields.Text(
        string='Hold Reason',
    )

    # Status-change audit history.
    history_ids = fields.One2many(
        'my_app.order.history',
        'order_id',
        string='Status History',
        readonly=True,
    )

    @api.depends('order_line_ids.quantity', 'order_line_ids.rate')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(
                line.quantity * line.rate
                for line in order.order_line_ids
            )

    # Generate the order number and record initial status.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('my_app.order')
                    or 'New'
                )

        orders = super().create(vals_list)

        for order in orders:
            order._log_status_change(False, order.state)

        return orders

    # Record status changes.
    def write(self, vals):
        old_states = {
            order.id: order.state
            for order in self
        }

        result = super().write(vals)

        if 'state' in vals:
            for order in self:
                old_state = old_states.get(order.id)

                if old_state != order.state:
                    order._log_status_change(old_state, order.state)

        return result

    # Create a history record with elevated permissions.
    def _log_status_change(self, old_state, new_state):
        self.ensure_one()

        self.env['my_app.order.history'].sudo().create({
            'order_id': self.id,
            'old_state': old_state or False,
            'new_state': new_state,
            'changed_by_id': self.env.user.id,
            'changed_on': fields.Datetime.now(),
        })

    # Claim an order for the current staff member.
    def action_claim_order(self):
        for order in self:
            if (
                order.assigned_user_id
                and order.assigned_user_id != self.env.user
            ):
                raise UserError(
                    _('This order is already assigned to another staff member.')
                )

            order.assigned_user_id = self.env.user

    # Start inventory checking.
    def action_start_inventory_check(self):
        self.write({
            'state': 'checking_inventory',
            'department': 'inventory',
        })

    # Complete inventory checking and send to processing.
    def action_inventory_checked(self):
        self.write({
            'state': 'inventory_checked',
            'department': 'processing',
            'assigned_user_id': False,
        })

    # Start order processing.
    def action_start_processing(self):
        self.write({
            'state': 'processing',
            'department': 'processing',
        })

    # Complete order processing.
    def action_complete_processing(self):
        self.write({
            'state': 'completed',
            'department': 'management',
        })

    # Put an order on hold.
    def action_put_on_hold(self):
        for order in self:
            if not order.hold_reason:
                raise UserError(
                    _('Enter a hold reason before putting an order on hold.')
                )

            order.state = 'on_hold'

    # Resume an order according to its department.
    def action_resume_order(self):
        for order in self:
            if order.department == 'inventory':
                order.state = 'checking_inventory'
            elif order.department == 'shipping':
                order.state = 'ready_to_ship'
            else:
                order.state = 'processing'

    # Mark the order ready for shipping.
    def action_ready_to_ship(self):
        self.write({
            'state': 'ready_to_ship',
            'department': 'shipping',
            'assigned_user_id': False,
        })

    # Mark the order as shipped.
    def action_mark_shipped(self):
        self.write({
            'state': 'shipped',
            'department': 'shipping',
        })


class RetailerOrderLine(models.Model):
    _name = 'my_app.order.line'
    _description = 'Retailer Order Line'
    _order = 'id'

    order_id = fields.Many2one(
        'my_app.order',
        string='Order',
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
        required=True,
        default=1.0,
    )

    rate = fields.Float(
        string='Unit Price',
        required=True,
        default=0.0,
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
    )

    @api.depends('quantity', 'rate')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.rate

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.rate = line.product_id.lst_price
            else:
                line.rate = 0.0

    @api.constrains('quantity', 'rate')
    def _check_quantity_and_rate(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    _('Quantity must be greater than zero.')
                )

            if line.rate < 0:
                raise ValidationError(
                    _('Unit price cannot be negative.')
                )


class RetailerOrderHistory(models.Model):
    _name = 'my_app.order.history'
    _description = 'Retailer Order Status History'
    _order = 'changed_on desc, id desc'

    order_id = fields.Many2one(
        'my_app.order',
        string='Order',
        required=True,
        ondelete='cascade',
        index=True,
    )

    old_state = fields.Selection(
        [
            ('new', 'New'),
            ('checking_inventory', 'Checking Inventory'),
            ('inventory_checked', 'Inventory Checked'),
            ('processing', 'Processing Order'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold'),
            ('ready_to_ship', 'Ready to Ship'),
            ('shipped', 'Shipped'),
        ],
        string='Previous Status',
    )

    new_state = fields.Selection(
        [
            ('new', 'New'),
            ('checking_inventory', 'Checking Inventory'),
            ('inventory_checked', 'Inventory Checked'),
            ('processing', 'Processing Order'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold'),
            ('ready_to_ship', 'Ready to Ship'),
            ('shipped', 'Shipped'),
        ],
        string='New Status',
        required=True,
    )

    changed_by_id = fields.Many2one(
        'res.users',
        string='Changed By',
        required=True,
        ondelete='restrict',
    )

    changed_on = fields.Datetime(
        string='Changed On',
        required=True,
        default=fields.Datetime.now,
    )
