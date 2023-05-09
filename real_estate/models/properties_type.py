from odoo import models,fields,api


class PropertiesTypes(models.Model):
    _name = 'estate.property.type'

    def action_property_type(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Offers',
            'res_model': 'estate.property.offer',
            'domain': "[('property_type_id', '=', active_id)]",
            'view_mode': 'tree','form'
                                'context': "{'create': False}",
        }

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)

    name = fields.Char(string='Name')

    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Type must be unique !')
    ]
    property_ids = fields.One2many('estate.type','property_type_id',string='Properties Type')
    offer_ids = fields.One2many('estate.property.offer','property_type_id',string='Offers')
    offer_count = fields.Integer(string='Offer Count',compute='_compute_offer_count')


class EstateType(models.Model):
    _name = 'estate.type'

    property_type_id = fields.Many2one('estate.property.type',string='Property Type')
    property_id = fields.Many2one('estate.properties',string='Properties', domain="[('properties_type_id', '=', property_type_id)]")
    status = fields.Selection([('new', 'New'),
                               ('cancel', 'Canceled'),
                               ('sold', 'Sold')
                               ], string='Status', related='property_id.status')
    expected_price = fields.Float(string='Expected Price', related='property_id.expected_price')


