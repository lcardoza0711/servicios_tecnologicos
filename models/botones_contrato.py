from odoo import api, models, fields
from datetime import date


class EquipoEntrust(models.Model):
    _inherit="equipo.entrust.contrato"

    def ver_helpdesk_ticket(self):
        nombre = 'Tickets de servicio para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain': [('contrato_id', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_contrato': self.id,
            'default_contrato': self.id,
        }

        action['domain'] = [('contrato_id', '=', self.id)]
        documentos = self.mapped('visitas')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_helpdesk_ticket(self):
        for record in self:
            record.cuenta_helpdesk_ticket=len(self.env['helpdesk.ticket'].search([('contrato_id','=',record.id)]))

    cuenta_helpdesk_ticket = fields.Float('Cuenta de Tickets de servicio', compute="_cuenta_helpdesk_ticket")

    def crear_helpdesk_ticket(self):
        nombre = 'Nuevo tickets de servicio para ' + self.name
         
        action = {
            'name': nombre,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain': [('contrato_id', '=', self.id)],            
            'view_mode': 'form'
        }
        action['context'] = {
            'search_default_contrato_id': self.id,
            'default_contrato_id': self.id,
            'default_partner_id': self.cliente.id,
            'default_fecha': date.today(),
            # 'default_team_id': 2 if date.today() == self.fecha_primera else 2 if  date.today() == self.fecha_segunda else 9,
            'default_user_id': self.responsable.user_id.id,
        }
        return action


    def ver_bitacora_servicio(self):
        nombre = 'Bitacoras de servicio para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'bitacora.servicio',
            'type': 'ir.actions.act_window',
            'domain': [('contrato', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_contrato': self.id,
            'default_contrato': self.id,
        }

        action['domain'] = [('contrato', '=', self.id)]
        documentos = self.mapped('bitacoras')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_bitacora_servicio(self):
        for record in self:
            record.cuenta_bitacora_servicio=len(self.env['bitacora.servicio'].search([('contrato','=',record.id)]))

    cuenta_bitacora_servicio = fields.Float('Cuenta de Bitacoras de servicio', compute="_cuenta_bitacora_servicio")

    def crear_bitacora_servicio(self):
        nombre = 'Nuevo bitacoras de servici para ' + self.name
        action = {
            'name': nombre,
            'res_model': 'bitacora.servicio',
            'type': 'ir.actions.act_window',
            'domain': [('contrato', '=', self.id)],            
            'view_mode': 'form'
        }
        action['context'] = {
            'search_default_contrato': self.id,
            'default_contrato': self.id,
        }        
        return action

    def get_encuestas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'view_mode': 'tree',
            'res_model': 'fleet.vehicle',
            'domain': [('driver_id', '=', self.id)],
            'context': "{'create': False}"
        }

