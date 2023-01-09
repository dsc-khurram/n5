from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateDetail(models.Model):
    _inherit = 'product.template'

    length = fields.Float(string= 'Length')
    width = fields.Float(string='Width')
    is_mother = fields.Boolean(string = 'Mother Reel', default = False)
    is_waste = fields.Boolean(string = 'Wasted', default = False)


    @api.constrains('uom_id')
    def _check_uom_not_in_invoice(self):
        for template in self:
            invoices = self.env['account.move.line'].sudo().search([('product_id.product_tmpl_id.id', '=', template.id)], limit=1)
            # if invoices:
            #     raise ValidationError(_('The product "%s" is used in invoices. You cannot change its Unit of Measure.', template.display_name))