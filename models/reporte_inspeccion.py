from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo import _

class ReporteInspeccion(models.Model):
    _name="reporte.inspeccion"
    _description="Bitacora de seguridad electrónica"
    _inherit = ['mail.thread', 'mail.activity.mixin']    

    name = fields.Char("Numero de inspección", readonly=True, required=True, default=lambda self: _('New'))
    ticket = fields.Many2one("helpdesk.ticket")
    oportunidad_origen = fields.Many2one(related = "ticket.oportunidad_id", string = "Oportunidad origen")
    cliente = fields.Many2one(related = "oportunidad_origen.partner_id", string = "Cliente", store = True)
    
    # Por solicitud piad-132, se cambia el contacto, de char, a many2one
    contacto = fields.Char(related = "oportunidad_origen.contact_name", string = "Contacto", store = True, readonly = False)
    # contacto = fields.One2many(related = "cliente.child_ids", string = "Contacto", store = True, readonly = False)
    
    telefono = fields.Char(related = "oportunidad_origen.phone", string = "Número de teléfono", store = True, readonly = False)
    email = fields.Char(related = "oportunidad_origen.email_from", string = "Correo electrónico", store = True, readonly = False)

    lineas_producto = fields.Many2many("linea.producto", string = "Líneas de producto")
    lista_producto = fields.One2many("product.template.inspeccion.lista", "reporte_inspeccion_id", string = "Lista de productos")
    equipos_adicionales = fields.Text(string = "Notas de equipos adicionales")

    materiales = fields.One2many("reporte.inspeccion.materiales.lista", "reporte_inspeccion_id", string = "Materiales a utilizar")
    horas_instalacion = fields.Float(string = "Horas posibles de instalación")
    dias_instalacion = fields.Float(string = "Dias posibles de instalación")
    observaciones_adicionales = fields.Text(string = "Observaciones adicionales")

    img_estado1 = fields.Image(string = "Imagen 1")
    img_estado2 = fields.Image(string = "Imagen 2")
    img_estado3 = fields.Image(string = "Imagen 3")
    img_estado4 = fields.Image(string = "Imagen 4")
    img_estado5 = fields.Image(string = "Imagen 5")
    img_estado6 = fields.Image(string = "Imagen 6")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'reporte.inspeccion') or _('New')
        res = super(ReporteInspeccion, self).create(vals)
        return res
    
class ReporteInspeccionTicket(models.Model):
    _inherit = "helpdesk.ticket"

    inspecciones = fields.One2many("reporte.inspeccion", "ticket", string = "Inspecciones")
    cuenta_inspecciones = fields.Float('Cuenta de inspecciones', compute="_cuenta_inspecciones")
    oportunidad_id = fields.Many2one("crm.lead") 

    def _cuenta_inspecciones(self):
        for record in self:
            record.cuenta_inspecciones = len(self.env['reporte.inspeccion'].search([('ticket','=',record.id)]))     

    def crear_reporte_inspeccion(self):
        nombre = 'Reporte de inspección ' + self.name
        action = {
        'name': nombre,
        'res_model': 'reporte.inspeccion',
        'type': 'ir.actions.act_window',
        'view_mode': 'form'
        }
        action['context'] = {
        'default_ticket': self.id,
        'default_oportunidad': self.oportunidad_id.id
        }        
        return action

    def ver_inspecciones(self):
        nombre = 'Inspecciones para ' + self.name

        action = {
            'name': nombre,
            'res_model': 'reporte.inspeccion',
            'type': 'ir.actions.act_window',
            'domain': [('ticket', '=', self.id)],           
            'view_mode': 'tree,form'
        }

        action['context'] = {
            'search_ticket': self.id,
            'default_ticket': self.id,
        }

        action['domain'] = [('ticket', '=', self.id)]
        documentos = self.mapped('inspecciones')
        if len(documentos) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = documentos.id
        return action