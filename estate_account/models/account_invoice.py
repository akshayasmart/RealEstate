from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    property_id = fields.Many2one('estate.properties', string='Property', readonly=True, copy=False)