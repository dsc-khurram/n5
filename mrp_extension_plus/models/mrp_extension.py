from datetime import datetime, date, timedelta
from odoo import api, fields,tools, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta

# class StockQuantInherit(models.Model):
#     _inherit = 'stock.quant'

#     @api.model
#     def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
       
#         self = self.sudo()
#         rounding = product_id.uom_id.rounding
#         quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
#         reserved_quants = []

#         if float_compare(quantity, 0, precision_rounding=rounding) > 0:
#             # if we want to reserve
#             available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
#             if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
#                 raise UserError(_('It is not possible to reserve more products of %s than you have in stock.', product_id.display_name))
#         elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
#             # if we want to unreserve
#             available_quantity = sum(quants.mapped('reserved_quantity'))
#             # if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
#             #     raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.', product_id.display_name))
#         else:
#             return reserved_quants

#         for quant in quants:
#             if float_compare(quantity, 0, precision_rounding=rounding) > 0:
#                 max_quantity_on_quant = quant.quantity - quant.reserved_quantity
#                 if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
#                     continue
#                 max_quantity_on_quant = min(max_quantity_on_quant, quantity)
#                 quant.reserved_quantity += max_quantity_on_quant
#                 reserved_quants.append((quant, max_quantity_on_quant))
#                 quantity -= max_quantity_on_quant
#                 available_quantity -= max_quantity_on_quant
#             else:
#                 max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
#                 quant.reserved_quantity -= max_quantity_on_quant
#                 reserved_quants.append((quant, -max_quantity_on_quant))
#                 quantity += max_quantity_on_quant
#                 available_quantity += max_quantity_on_quant

#             if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
#                 break
#         return reserved_quants


class StockMoveLineInherited(models.Model):
    _inherit ='stock.move.line'
    
    weight = fields.Float(string='Weight')
    width = fields.Float(string= 'Width', related='product_id.width')
    length = fields.Float(string='Length',related='product_id.length')



class StockAssignSerialNumbersInherited(models.TransientModel):
    _inherit = 'stock.assign.serial'


    def _assign_serial_numbers(self, cancel_remaining_quantity=False):
        serial_numbers = self._get_serial_numbers()
        productions = self.production_id._split_productions(
            {self.production_id: [1] * len(serial_numbers)}, cancel_remaining_quantity, set_consumed_qty=True)
        production_lots_vals = []
        for serial_name in serial_numbers:
            production_lots_vals.append({
                'product_id': self.production_id.product_id.id,
                'company_id': self.production_id.company_id.id,
                'name': serial_name,
            })
        production_lots = self.env['stock.production.lot'].create(production_lots_vals)
        for production, production_lot in zip(productions, production_lots):
            production.lot_producing_id = production_lot.id
            first_sep = '(240)'
            mystring = str(production_lot.name)

            if mystring[0:5] == first_sep: 

                mystring = mystring.replace(" ", "")
                workcenter =[]
                second_sep = '(10)'
                third_sep = '(11)'
                forth_sep = '(21)'
                date_string = mystring[mystring.find(third_sep)+len(third_sep):mystring.rfind(forth_sep)]
                production.top_record = mystring[mystring.find(first_sep)+len(first_sep):mystring.rfind(second_sep)]
                production.supplier_batch = mystring[mystring.find(second_sep)+len(second_sep):mystring.rfind(third_sep)]
                production.production_date = date_string[4:6]+'/'+date_string[2:4]+'/'+date_string[0:2]

                for rec in production.workorder_ids:
                    workcenter.append(rec.workcenter_id.name)
                

                if len(mystring[mystring.find(forth_sep)+len(forth_sep):]) == 1:
                    if workcenter and production.width:
                        production.material_serial = str(workcenter[0])+''+str(production.width)+''+'0000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif workcenter:
                        production.material_serial = str(workcenter[0])+''+'0000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif production.width:
                        production.material_serial = str(production.width)+''+'0000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    else:
                        production.material_serial = '0000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                elif len(mystring[mystring.find(forth_sep)+len(forth_sep):]) == 2:
                    if workcenter and production.width:
                        production.material_serial = str(workcenter[0])+''+str(production.width)+''+'000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif workcenter:
                        production.material_serial = str(workcenter[0])+''+'000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif production.width:
                        production.material_serial = str(production.width)+''+'000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    else:
                        production.material_serial = '000'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                elif len(mystring[mystring.find(forth_sep)+len(forth_sep):]) == 3:
                    if workcenter and production.width:
                        production.material_serial = str(workcenter[0])+''+str(production.width)+''+'00'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif workcenter:
                        production.material_serial = str(workcenter[0])+''+'00'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif production.width:
                        production.material_serial = str(production.width)+''+'00'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    else:
                        production.material_serial = '00'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                elif len(mystring[mystring.find(forth_sep)+len(forth_sep):]) == 4:
                    if workcenter and production.width:
                        production.material_serial = str(workcenter[0])+''+str(production.width)+''+'0'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif workcenter:
                        production.material_serial = str(workcenter[0])+''+'0'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif production.width:
                        production.material_serial = str(production.width)+''+'0'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    else:
                        production.material_serial = '0'+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                elif len(mystring[mystring.find(forth_sep)+len(forth_sep):]) == 5:
                    if workcenter and production.width:
                        production.material_serial = str(workcenter[0])+''+str(production.width)+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif workcenter:
                        production.material_serial = str(workcenter[0])+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    elif production.width:
                        production.material_serial = str(production.width)+''+ mystring[mystring.find(forth_sep)+len(forth_sep):]
                    else:
                        production.material_serial = mystring[mystring.find(forth_sep)+len(forth_sep):]
            else:
                mystring = str( production_lot.name)
                vendor = '90592'
                item_date = mystring[:mystring.rfind(vendor)]
                production.item_code = item_date[0:2]+'.'+item_date[2:-8]
                production.mfg_date =item_date[-7:-5]+'-'+item_date[-5:-3]+'-'+item_date[-3:-1]
                production.vendor = vendor
                production.mfg_ref = mystring[mystring.find(vendor)+len(vendor):]
                
            production.qty_producing = production.product_qty
            for workorder in production.workorder_ids:
                workorder.qty_produced = workorder.qty_producing

        if productions and len(production_lots) < len(productions):
            productions[-1].move_raw_ids.move_line_ids.write({'qty_done': 0})
            productions[-1].state = "confirmed"




class MrpProductionInherited(models.Model):
    _inherit = 'mrp.production'

    item_code = fields.Char(string='Item Code')
    mfg_date = fields.Char(string=' MFG Date')
    mfg_ref = fields.Char(string='MFG REF')
    vendor = fields.Char(string='Vendor')

    top_record = fields.Char(string='Top Field')
    supplier_batch= fields.Char(string='Supplier Batch Number')
    material_serial = fields.Char(string='Material Serial Number')
    production_date = fields.Char(string='Production Date')

    length = fields.Float(string="Length", related='product_id.length')
    width = fields.Float(string="Width", related='product_id.width', readonly=False)
    reel = fields.Float(string="% Completion", default = 100.00)
    half_reel = fields.Boolean(string='Half Done')
    check_automation = fields.Boolean(string='Automation')


    
    def action_consume_product_distribution_wizard(self):
        for rec in self:
            if rec.state == 'done' and rec.is_locked == True and rec.check_automation == True or rec.state == 'done' and rec.is_locked == False and rec.check_automation == True   or rec.state == 'cancel':
                raise ValidationError(_('Sorry! Record is in Done state, in which Automation is False, or may be in cancel state'))
        action = self.env["ir.actions.actions"]._for_xml_id("mrp_extension.act_consume_product_distribution_wizard")
        action['context'] = {
            'default_production_id': self.ids,
        }
        return action

    def action_serial_mass_produce_wizard(self):
        self.ensure_one()
        self._check_company()
        if self.state != 'confirmed':
            return
        if self.product_id.tracking != 'serial':
            return
        # dummy, dummy, missing_components, multiple_lot_components = self._check_serial_mass_produce_components()
        # message = ""
        # if missing_components:
        #     message += _("Make sure enough quantities of these components are reserved to carry on production:\n")
        #     message += "\n".join(component.name for component in missing_components)
        # if multiple_lot_components:
        #     if message:
        #         message += "\n"
        #     message += _("Component Lots must be unique for mass production. Please review consumption for:\n")
        #     message += "\n".join(component.name for component in multiple_lot_components)
        # if message:
        #     raise UserError(message)
        next_serial = self.env['stock.production.lot']._get_next_serial(self.company_id, self.product_id)
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.act_assign_serial_numbers_production")
        action['context'] = {
            'default_production_id': self.id,
            'default_expected_qty': self.product_qty,
            'default_next_serial_number': next_serial,
            'default_next_serial_count': self.product_qty - self.qty_produced,
        }
        return action


            

class MrpWorkorder(models.Model):
    
    _inherit = "mrp.workorder"

    
    # @api.depends('time_ids.duration')
    # def _compute_duration_bobbins(self):
    #     center_list = []
    #     value = {}
    #     record = None
    #     for order in self:
    #         # order.duration_bobbins = sum(order.time_ids.mapped('duration'))
    #         center_list.append({'workcenter_id':order.workcenter_id.id,'expected_duration': order.duration_expected ,'duration': sum(order.time_ids.mapped('duration'))})
            
    #     for x in center_list:
    #             if x["workcenter_id"] in value:
    #                 value[x["workcenter_id"]].update(x)
    #             else: 
    #                 value[x["workcenter_id"]] = x
    #             record = list(value.values())
    #     if record:
    #         for rec in record:
    #             order.duration_bobbins = rec.get('duration')
    #             order.duration_expected_bobbins = rec.get('expected_duration')


    # duration_bobbins= fields.Float('Duration Bobbins', compute=_compute_duration_bobbins, store=True, default=False)
    # duration_expected_bobbins = fields.Float('Expected Duration-Bobbins', compute=_compute_duration_bobbins ,store=True, default=False,help="Expected duration (in minutes)")
    

    def button_start_all(self):
        for rec in self:
            rec.button_start()

    def done_all(self):
        for rec in self:
            rec.button_finish()
   

# class MrpWorkcenterProductivityInherited(models.Model):
#     _inherit = "mrp.workcenter.productivity"
    

#     duration_bobbins = fields.Float('Duration-Bobbins', compute='_compute_duration_bobbins', store=True, default=False)

#     @api.depends('date_end', 'date_start')
#     def _compute_duration_bobbins(self):
        
#         for blocktime in self:
#             workcenter = self.env['mrp.workorder'].search([('workcenter_id','=',blocktime.workcenter_id.id)]).ids 
#             if workcenter:
#                 count = len(workcenter)
#                 blocktime.duration_bobbins = blocktime.duration/count
                
    
          
    
   