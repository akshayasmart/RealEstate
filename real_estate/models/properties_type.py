from odoo import models,fields


class PropertiesTypes(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(string='Name')

    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Type must be unique !')
    ]
