from odoo import models,fields


class PropertiesTags(models.Model):
    _name = 'estate.property.tag'

    name = fields.Char(string='Name')
    color = fields.Integer('Color Index', default=0)

    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Type must be unique !')
    ]
