from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit='sale.order'

    create_date=fields.Datetime(readonly=False)

    def ver_equipo_entrust_contrato(self):
        nombre = 'Contratos de servicio para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'equipo.entrust.contrato',
            'type': 'ir.actions.act_window',
            'domain': [('sale_order_id', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_sale_order_id': self.id,
            'default_sale_order_id': self.id,
        }

        action['domain'] = [('sale_order_id', '=', self.id)]
        documentos = self.mapped('contratos')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_equipo_entrust_contrato(self):
        for record in self:
            record.cuenta_equipo_entrust_contrato=len(self.env['equipo.entrust.contrato'].search([('sale_order_id','=',record.id)]))

    cuenta_equipo_entrust_contrato = fields.Float('Cuenta de Contratos de servicio', compute="_cuenta_equipo_entrust_contrato")

    def crear_equipo_entrust_contrato(self):
        nombre = 'Nuevo contratos de servici para ' + self.name
        action = {
        'name': nombre,
        'res_model': 'equipo.entrust.contrato',
        'type': 'ir.actions.act_window',
        'domain': [('sale_order_id', '=', self.id)],            
        'view_mode': 'form'
    }
        action['context'] = {
            'search_default_sale_order_id': self.id,
            'default_sale_order_id': self.id,
        }        
        return action
