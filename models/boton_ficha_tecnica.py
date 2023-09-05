# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EntregaProducto(models.Model):
    _inherit = 'helpdesk.ticket'

    def ver_entrega_producto(self):
        nombre = 'Ficha tecnica para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'entrega.producto',
            'type': 'ir.actions.act_window',
            'domain': [('ticket', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_ticket': self.id,
            'default_ticket': self.id,
        }

        action['domain'] = [('ticket', '=', self.id)]
        documentos = self.mapped('fichas')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action


    def _cuenta_entrega_producto(self):
        for record in self:
            record.cuenta_entrega_producto=len(self.env['entrega.producto'].search([('ticket','=',record.id)]))

    cuenta_entrega_producto = fields.Float('Cuenta de Ficha tecnica', compute="_cuenta_entrega_producto")

    def crear_entrega_producto(self):            
        nombre = 'Nuevo ficha tecnica para ' + self.name
        ticket=self.env['entrega.producto']
        data={
            'ticket':self.id,
            'cliente':self.partner_id,
            'equipos':self.equipo_id
        }
        ficha=ticket.create(data)

        action = {
        'name': nombre,
        'res_model': 'entrega.producto',
        'type': 'ir.actions.act_window',
        'domain': [('ticket', '=', ficha.id)],            
        'view_mode': 'form','res_id':ficha.id
        }
        action['context'] = {
        'search_default_ticket': self.id,
        'default_ticket': self.id,
        }        
        return action
