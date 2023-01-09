from odoo import api, fields, models, _


class StockMoveLineWizard(models.TransientModel):
    _name = 'stock.move.line.wizard'

    production_id = fields.Many2many('stock.move.line', string="Stock")

    weight = fields.Float(string='Weight')



    def apply(self):
        area = 0
        total_area = 0
        consumed_weight = 0
        for p in self.production_id:
            if p.width and p.length:
                total_area += (p.width * p.length)/1000

        for i in self.production_id:
            if i.width and i.length:
                area = (i.width * i.length)/1000
                consumed_weight= (area/total_area)*self.weight
            i.weight = consumed_weight

           