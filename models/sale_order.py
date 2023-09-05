from odoo import api, models, fields
import re
from dateutil.relativedelta import relativedelta

class Contrato(models.Model):
    _inherit = 'product.template'

    contrato = fields.Boolean("Es contrato?", default = False) 

    tipo_bitacora = fields.Many2one("bitacora.servicio.plantilla")

    contrato_id = fields.One2many("equipo.entrust.contrato", "nivel_contrato", string="Contratos")

    num_mantenimientos= fields.Integer("Número de visitas")
    num_certificaciones = fields.Integer("Número de certificaciones")
    num_horas_asesoria = fields.Integer("Número de horas de asesoría")
    num_design_card = fields.Integer("Número de diseño de tarjetas")


class SaleOrder(models.Model):
    _inherit='sale.order'
    
    contratos=fields.One2many("equipo.entrust.contrato","sale_order_id",string="Contratos de servicio")

    def action_confirm(self):
        #logica a ejecutarse antes de llamar al boton de confirm
        #validaciones de limites de credito
        res = super(SaleOrder, self).action_confirm()
        
        contrato_equipo=self.env['equipo.entrust.contrato']
        to_clean = re.compile('<.*?>')
        for record in self:
            for line in record.order_line:
                if line.product_id.product_tmpl_id.contrato:
                    #Llenamos el contrato
                    # El contrato no se debía de crear, se comenta por ticket 1965
                    # contrato=contrato_equipo.create(
                    #     {
                    #         "sale_order_id":record.id,
                    #         "name":self.env['ir.sequence'].next_by_code('contrato.entrust') or "Nuevo",
                    #         "estado":"1",
                    #         "cliente":record.partner_id.id,
                    #         "fecha_inicio": record.date_order,
                    #         "fecha_vencimiento":record.date_order+relativedelta(years=1),                  
                    #         "tipo_servicio":"regular",
                    #         "tipo_contrato":"entrust_e",
                    #         "nivel_contrato":"1",
                    #         "tecnico": self.env['hr.employee'].search([("name",'=',"Vladimir García")]).id,
                    #         "descripcion":re.sub(to_clean, '', record.note),
                    #         "responsable":self.env['hr.employee'].search([("name",'=',"Katherine Escalante")]).id
                    #     }
                    # )

                    ticket=self.env['helpdesk.ticket']
                    #Creamos el Ticket
                    ticket.create({
                        "name":"Ticket de Instalación",#+contrato.cliente+"/"+contrato.fecha_inicio,
                        "user_id":self.env['res.users'].search([("name",'=',"Vladimir García")]).id,
                        # Se agregan los siguientes valores por defecto por ticket 1888
                        "team_id": self.env['helpdesk.team'].search([("id", '=', 11)]).id,
                        "project_id": self.env['project.project'].search([("name", '=', "Mantenimiento Correctivo Entrust")]).id,
                        "description":'<h3>Por hacer:</h3><ul class="o_checklist"><li>Contactar al cliente</li><li>Agendar visita</li><li>Realizar mantenimiento</li><li>Entrega de bitacora</li></ul>',
                        # Se cambia, ya que no se creará el contrato, se tomará el cliente desde la orden de venta por ticket 1965
                        #"partner_id":contrato.cliente.id
                        "partner_id":record.partner_id.id                        
                    })
        return res