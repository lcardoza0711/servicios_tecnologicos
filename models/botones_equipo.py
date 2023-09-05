from odoo import api, models, fields
from odoo.exceptions import ValidationError


class EquipoEntrust(models.Model):
    _inherit="equipo.entrust"

    def ver_bitacora_servicio(self):
        if self.name:
            nombre = 'Bitacoras de servicio para ' + self.name
        else:
            raise ValidationError("No se puede crear ticket si no digita la serie del equipo")

        action = {
            'name': nombre,
            'res_model': 'bitacora.servicio',
            'type': 'ir.actions.act_window',
            'domain': [('equipo', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_equipo': self.id,
            'default_equipo': self.id,
        }

        action['domain'] = [('equipo', '=', self.id)]
        documentos = self.mapped('bitacoras')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_bitacora_servicio(self):
        for record in self:
            record.cuenta_bitacora_servicio=len(self.env['bitacora.servicio'].search([('equipo','=',record.id)]))

    cuenta_bitacora_servicio = fields.Float('Cuenta de Bitacoras de servicio', compute="_cuenta_bitacora_servicio")

    def crear_bitacora_servicio(self):
        nombre = 'Nuevo bitacoras de servicio para ' + self.name
        action = {
        'name': nombre,
        'res_model': 'bitacora.servicio',
        'type': 'ir.actions.act_window',
        'domain': [('equipo', '=', self.id)],            
        'view_mode': 'form'
    }
        action['context'] = {
        'search_default_equipo': self.id,
        'default_equipo': self.id,

    }        
        return action


    def ver_helpdesk_ticket(self):
        nombre = 'Tickets de soporte para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain': [('equipo_id', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_equipo_id': self.id,
            'default_equipo_id': self.id,

        }

        action['domain'] = [('equipo_id', '=', self.id)]
        documentos = self.mapped('tickets')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_helpdesk_ticket(self):
        for record in self:
            record.cuenta_helpdesk_ticket=len(self.env['helpdesk.ticket'].search([('equipo_id','=',record.id)]))

    cuenta_helpdesk_ticket = fields.Float('Cuenta de Tickets de soporte', compute="_cuenta_helpdesk_ticket")

    def crear_helpdesk_ticket(self):
        if self.name:
            nombre = 'Nuevo tickets de soporte para ' + self.name
        else:
            raise ValidationError("No se puede crear ticket si no digita la serie del equipo")
        action = {
        'name': nombre,
        'res_model': 'helpdesk.ticket',
        'type': 'ir.actions.act_window',
        'domain': [('equipo_id', '=', self.id)],            
        'view_mode': 'form'}
        action['context'] = {
        'default_contrato_id': self.contrato_id.id,
        'search_default_equipo_id': self.id,
        'default_equipo_id': self.id,
        'default_user_id': self.tecnico.id,
        'default_partner_id': self.cliente.id,
        'default_fecha': fields.Date.today(),
        }
        return action
