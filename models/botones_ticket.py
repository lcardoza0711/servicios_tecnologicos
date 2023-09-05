from odoo import api, models, fields

class EquipoEntrust(models.Model):
    _inherit="helpdesk.ticket"
    
    def ver_bitacora_servicio(self):
        nombre = 'Bitacoras de servicio para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'bitacora.servicio',
            'type': 'ir.actions.act_window',
            'domain': [('ticket', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_ticket': self.id,
            'default_ticket': self.id,
        }

        action['domain'] = [('ticket', '=', self.id)]
        documentos = self.mapped('bitacoras')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_bitacora_servicio(self):
        for record in self:
            record.cuenta_bitacora_servicio=len(self.env['bitacora.servicio'].search([('ticket','=',record.id)]))

    cuenta_bitacora_servicio = fields.Float('Cuenta de Bitacoras de servicio', compute="_cuenta_bitacora_servicio")

    def crear_bitacora_servicio(self):
        nombre = 'Nuevo bitacoras de servicio para ' + self.name
        action = {
        'name': nombre,
        'res_model': 'bitacora.servicio',
        'type': 'ir.actions.act_window',
        'domain': [('ticket', '=', self.id)],
        'view_mode': 'form'
    }
        action['context'] = {
        'search_default_ticket': self.id,
        'default_ticket': self.id,
        'default_cliente': self.partner_id.id,
        'default_contrato': self.contrato_id.id
    }        
        return action


