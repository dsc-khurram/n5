from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError




class ConsumProductionDistribution(models.TransientModel):
    _name = 'consume.production.distribution'

    overwrite_half = fields.Boolean(string='OverWrite Half Record', default =False)
    production_id = fields.Many2many('mrp.production', string='Production')
    prod_consumption = fields.One2many('consume.production.distribution.two','consumption_id',string='abcd')

    def overwrite_record(self):
        self._update_record()
        self.apply()
      

    def _update_record(self):       
        for prod in self.prod_consumption:
            if prod.product_id.is_mother == True:
                for i in self.production_id:
                    if i.half_reel == True:
                        for m in i.move_raw_ids:
                            if prod.product_id.id == m.product_id.id:
                                if self.overwrite_half == True:    
                                    if m.move_line_ids:
                                        m.move_line_ids.unlink()
                    else:
                        for m in i.move_raw_ids:
                            if prod.product_id.id == m.product_id.id:
                                if m.move_line_ids:
                                    m.move_line_ids.unlink()

                                
                    
            elif prod.product_id.is_waste == True:
                for p in self.production_id:
                    for by in p.move_byproduct_ids:
                        if prod.product_id.id == by.product_id.id:
                            if by.move_line_ids:
                                by.move_line_ids.unlink()

    
            else:
                
                for rec in self.production_id:
                    for move in rec.move_raw_ids:
                        if prod.product_id.id == move.product_id.id:
                            if move.move_line_ids:
                                move.move_line_ids.unlink()
                           
                            
    

    def apply(self):        
        area = 0
        total_area = 0
        consumption = 0
        for con in self.production_id:
            if con.state == 'done':
                con.check_automation = True
            if con.half_reel == False:
                total_area += ((con.width* con.length) * con.reel/100)/1000
            else:
                total_area += ((con.width* con.length) * (100 - con.reel)/100)/1000


       
        for prod in self.prod_consumption:
            if prod.product_id.is_mother == True:
                for i in self.production_id:
                    if i.half_reel == False:
                        area = ((i.width* i.length) * i.reel/100)/1000
                    else:
                        area = ((i.width* i.length) * (100-i.reel)/100)/1000
                    if total_area and prod.qty:
                        consumption = prod.qty*area/total_area
                        for m in i.move_raw_ids:
                            if prod.product_id.id == m.product_id.id:
                                m.update({'forecast_availability':m.product_uom_qty})

                                stock_line = self.env['stock.move.line'].search([('move_id','=',m.id),('lot_id','=',prod.lot_id.id)])
                                if stock_line:
                                    stock_line.update({'product_uom_qty': m.product_uom_qty,
                                                        'qty_done': consumption,})
                                else:
                                    vals = {'move_id':m.id,
                                            'location_id':m.location_id.id,
                                            'location_dest_id':m.location_dest_id.id, 
                                            'product_id': prod.product_id.id,
                                            'lot_id':prod.lot_id.id,
                                            'qty_done': consumption,
                                            'product_uom_id':prod.qty_measure.id
                                            }


                                    self.env['stock.move.line'].create(vals)

                                
                    
            elif prod.product_id.is_waste == True:
                cost = 0
                for p in self.production_id:
                    if p.half_reel == False:
                        area = ((p.width* p.length) * p.reel/100)/1000
                    else:
                        area = ((p.width* p.length) * (100-p.reel)/100)/1000
                    if total_area and prod.qty:
                        consumption = prod.qty*area/total_area
                        if prod.cost_share:
                            cost = prod.cost_share
                            # cost = prod.cost_share*area/total_area
                        for by in p.move_byproduct_ids:
                            if prod.product_id.id == by.product_id.id:
                                by.update({
                                    # 'quantity_done':consumption,
                                            'cost_share':cost,
                                        })
                                # stock_line = self.env['stock.move.line'].search([('product_id','=',prod.product_id.id),('move_id','=',by.id),])
                                stock_line = self.env['stock.move.line'].search([('lot_id','=',prod.lot_id.id),('move_id','=',by.id),])
                                if stock_line:
                                    stock_line.update({'qty_done':consumption,
                                                        
                                                    })
                                else:

                                    vals = {'move_id': by.id,
                                            'location_id':by.location_id.id,
                                            'location_dest_id':by.location_dest_id.id, 
                                            'product_id': prod.product_id.id,
                                            'lot_id':prod.lot_id.id,
                                            'qty_done': consumption,
                                            'product_uom_id':prod.qty_measure.id
                                                }

                                    self.env['stock.move.line'].create(vals)

            else:
                value = 0
                count = 0
                count = len(self.production_id.ids)
                value = prod.qty/count
                for rec in self.production_id:
                    for move in rec.move_raw_ids:
                        if prod.product_id.id == move.product_id.id:
                            move.update({'forecast_availability':move.product_uom_qty})
                            stock_line = self.env['stock.move.line'].search([('move_id','=',move.id),('lot_id','=',prod.lot_id.id)])
                            if stock_line:
                                stock_line.update({'product_uom_qty': move.product_uom_qty,
                                                'qty_done': value,})
                            else:
                                vals = {
                                            
                                            'move_id':move.id,
                                            'location_id':move.location_id.id,
                                            'location_dest_id':move.location_dest_id.id, 
                                            'product_id': prod.product_id.id,
                                            'lot_id':prod.lot_id.id,
                                           
                                            'qty_done': value,
                                            'product_uom_id':prod.qty_measure.id
                                            }


                                self.env['stock.move.line'].create(vals)

   

class ConsumProductionDistributionTwo(models.TransientModel):
    _name = 'consume.production.distribution.two'
    

    consumption_id = fields.Many2one('consume.production.distribution', string='Consumption')

    product_id =fields.Many2one('product.product',string="Product")
    lot_id = fields.Many2one('stock.production.lot',string='serial/Lot')
    qty = fields.Float(string='Consume')
    cost_share = fields.Float(string= "Cost Share")
    qty_measure = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=False)

    production_id = fields.Many2many('mrp.production', related="consumption_id.production_id",string="Budget")
    production_id_temp = fields.Many2many('mrp.production', string="Running Budget")
    cost_boolean = fields.Boolean(string="Cost", default=False)



    @api.onchange('product_id')
    def cost_share_visibility(self):
        if self.product_id.is_waste == True:
            self.cost_boolean = True
        else:
            self.cost_boolean = False
        


   



    @api.onchange('consumption_id')
    def _get_production_id(self):
       if self.production_id:
            self.production_id_temp = self.consumption_id.production_id.ids


    @api.onchange('production_id_temp')
    def _get_production_id_temp(self):
        if  self.consumption_id.production_id.ids:
            product_list = []
            reserved_product = []

            for mrp in self.production_id:
                for move in mrp.move_raw_ids:
                    product_id = self.env['product.product'].search([('id','=',move.product_id.id)])
                    product_list.append(product_id.id)
                for by in mrp.move_byproduct_ids:
                    byproduct = self.env['product.product'].search([('id','=',by.product_id.id)])
                    product_list.append(byproduct.id)
            domain_accounts = [('id', 'in', product_list)]
            if self.production_id:
                return {'domain': {'product_id': domain_accounts}}
            else:
                return {'domain': {}}
    

    @api.onchange('product_id')
    def _get_product_lot_number(self):
        lot_list =[]
        lot_id = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)])
        for lot in lot_id:
            lot_list.append(lot.id)
        domain_lots = [('id', 'in', lot_list)]
        if self.product_id:
                return {'domain': {'lot_id': domain_lots}}
        else:
            return {'domain': {}}
        
