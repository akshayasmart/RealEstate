from odoo import models,fields


class PropertiesMoveLine(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.properties', 'user_id', string='Properties')