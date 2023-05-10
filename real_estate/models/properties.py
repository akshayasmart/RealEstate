from datetime import timedelta

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError


class Properties(models.Model):
    _name = 'estate.properties'

    # selling price cannot be lower than 90% of the expected price.
    @api.constrains('expected_price', 'selling_price')
    def check_selling_price(self):
        for record in self:
            if record.selling_price > 0 and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError("Selling price cannot be lower than 90% of expected price!")

    def unlink(self):
        for record in self:
            if record.status not in ('new', 'canceled'):
                raise ValidationError("Error: This property cannot be deleted.")
        return super(Properties, self).unlink()

    # added tags
    @api.model
    def _get_default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    @api.model
    def _get_default_buyer(self):
        return self.env.context.get('buyer_id', self.env.user.id)

    # Add the total_area field It is defined as the sum of the living_area and the garden_area.

    @api.depends('living_area', 'garden_area')
    def total_area(self):
        for rec in self:
            rec.total = 0
            rec.total = rec.living_area + rec.garden_area

    # add the price amount which amount is grater the amount will add in the best price field

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for property in self:
            best_offer = 0.0
            for offer in property.offer_ids:
                best_offer = max(best_offer, offer.price)
            property.best_offer = best_offer

    # Amounts should be positive

    @api.constrains('expected_price')
    def constrains_expected_price(self):
        for rec in self:
            if rec.expected_price < 0:
                raise UserError(_(' The the unexpected Price must be strictly Positive'))


    # garden will set a default area of 10 and an orientation to North.

    @api.onchange('garden')
    def onchange_orientation(self):
        if self.garden:
            self.garden_area = 20
            self.garden_orientation = 'south'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # You should be able to cancel and sold:

    def action_cancel(self):
        if self.status == 'sold':
            raise UserError('A sold property cannot be canceled.')
        else:
            self.status = 'cancel'

    def action_sold(self):
        if self.status == 'cancel':
            raise UserError('A canceled property cannot be set as sold.')
        else:
            self.status = 'sold'
            self.write({
                'status_bar':'sold'
            })


    name = fields.Char(string='Title')
    tag_ids = fields.Many2many('estate.property.tag',string='Tags')
    properties_type_id = fields.Many2one('estate.property.type',string='Properties Type')
    status_bar = fields.Selection([
        ('new', 'NEW'),
        ('offer_received', 'OFFER RECEIVED'),(
            'offer_accepted','OFFER ACCEPTED'),
        ('sold','SOLD') ],
        'Status Bar', default='new')
    post_code = fields.Char(string='Post Code')
    expected_price = fields.Float(string='Expected Price')
    available_from = fields.Date(string='Available From')
    best_offer = fields.Integer(string='Best Offer',compute='_compute_best_price')
    selling_price = fields.Float(string='Selling Price')
    description = fields.Text(string='Description')
    bedroom = fields.Integer(string='Bedrooms')
    living_area = fields.Integer(string='Living Area(sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(stringt='Garden Area(sqm)')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Garden Orientation')
    status = fields.Selection([('new', 'New'),
                               ('cancel', 'Canceled'),
                               ('sold', 'Sold')
                               ], string='Status',default='new', readonly=True)

    total= fields.Integer(string='Total Area(sqm)' , compute='total_area')
    offer_ids = fields.One2many('estate.property.offer','properties_id',string='Properties')
    color = fields.Integer('Color Index', default=0)
    user_id = fields.Many2one('res.users',string='Salesman',default=_get_default_user)
    buyer_id = fields.Many2one('res.partner',string='Buyer',default=_get_default_buyer)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

class Offer(models.Model):
    _name = 'estate.property.offer'

    # the validity date should be computed and can be updated:

    @api.depends('validity')
    def _compute_validity_date(self):
        for rec in self:
            rec.deadline = fields.Date.today() + timedelta(days=rec.validity)

    def _set_deadline(self):
        for rec in self:
            rec.validity = (rec.deadline - fields.Date.today()).days

    @api.onchange('validity')
    def onchange_validity_days(self):
        self.deadline = fields.Date.today() + timedelta(days=self.validity)

    # Once an offer is accepted, the selling price and the buyer should be set:

    def accept_button(self):
        for record in self:
            for rec in record.properties_id:
                self.status = 'accepted'
                if self.status == 'accepted':
                    rec.write({
                        'selling_price': self.price,
                        'buyer_id': self.partner_id.id,
                        'status_bar': 'offer_accepted',
                    })

    def refused_button(self):
        for record in self:
            for rec in record.properties_id:
                self.status = 'refused'
                if self.status == 'refused':
                    rec.write({
                        'selling_price': 0,
                        'buyer_id': [('buyer_id', '=', '')],
                        'status_bar': 'offer_received'
                    })

    # click the buttons ‘Accept’ and ‘Refuse’ the status will change

    @api.model
    def create(self, vals):
        # create the offer record
        offer = super(Offer, self).create(vals)
        # update the property state to 'Offer Received'
        property_id = vals.get('properties_id')
        if property_id:
            property = self.env['estate.properties'].browse(property_id)
            property.write({'status_bar': 'offer_received'})
        return offer

    @api.constrains('price', 'properties_id')
    def check_offer_price(self):
        for record in self:
            existing_offers = self.search([('properties_id', '=', record.properties_id.id), ('id', '!=', record.id)])
            for offer in existing_offers:
                if record.price < offer.price:
                    raise ValidationError('Cannot create offer with price lower than existing offer!')

    properties_id = fields.Many2one('estate.properties',string='Offers')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner',string='Partner')
    validity = fields.Integer(string='validity(days)')
    status = fields.Selection([('refused','Refused'),
                               ('accepted','Accepted')],string='Status'
                              )
    deadline = fields.Date(string='Deadline',compute='_compute_validity_date', inverse='_set_deadline', store=True)
    property_type_id = fields.Many2one(related='properties_id.properties_type_id',string='Property Type')
