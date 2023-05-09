from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class Properties(models.Model):
    _inherit = 'estate.properties'

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

    def action_sold(self):
        res = super(Properties, self).action_sold()
        _logger.info('Property %s has been sold', self.name)

        # Create empty account move
        move = self.env['account.move'].create({
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'price_unit': self.selling_price * 0.06
            }), (0, 0, {
                'name': 'Administrative Fees',
                'price_unit': 100.0
            })]
        })
        _logger.info('Created invoice %s for property %s', move.name, self.name)

        return res

    # def action_sold(self):
    #     invoice = self.env['account.move'].create({
    #         'partner_id': self.buyer_id.id,
    #         'property_id': self.id,
    #         'type': 'out_invoice',
    #         'invoice_line_ids': [(0, 0, {
    #             'name': self.name,
    #             'quantity': 1,
    #             'price_unit': self.selling_price,
    #             'account_id': self.env.ref('account.a_sale').id,
    #         })]
    #     })
    #     self.write({'state': 'sold', 'invoice_id': invoice.id})

    # def action_sold(self):
    #     # create invoice
    #     invoice = self.env['account.move'].create({
    #         'partner_id': self.buyer_id.id,
    #         'type': 'out_invoice',
    #         'invoice_line_ids': [(0, 0, {
    #             'name': 'Property sale',
    #             'quantity': 1.0,
    #             'price_unit': self.selling_price * 0.06 + 100.0,
    #             'account_id': self.env['account.account'].search([('code', '=', '705000')]).id,
    #         }), (0, 0, {
    #             'name': 'Administrative fees',
    #             'quantity': 1.0,
    #             'price_unit': 100.0,
    #             'account_id': self.env['account.account'].search([('code', '=', '706000')]).id,
    #         })]
    #     })
    #     return invoice