from ast import Str
from dataclasses import field
import string
from odoo import api, models, fields
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Partner(models.Model):
    _inherit='helpdesk.ticket'

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     team_id = self._context.get('default_team_id')
    #     stage_ids = self.env['helpdesk.stage'].search([])
    #     filtrado=[]
    #     for stage in stage_ids:
    #         if team_id in stage.team_ids.ids:
    #             filtrado.append(stage.id)
        
    #     return stages.browse(filtrado)

    @api.onchange('team_id')
    def _ocultar_equipos(self):
        if self.team_id.name== 'Odoo - Mesa de Ayuda':
            self.ocultar_equipos=True
        else:
            self.ocultar_equipos= False

    stage_id = fields.Many2one(
        'helpdesk.stage', string='Stage', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, ondelete='restrict', tracking=True, group_expand='_read_group_stage_ids',
        copy=False, index=True, domain="[('team_ids', '=', team_id)]")

    project_id = fields.Many2one("project.project",related='team_id.project_id',readonly=False, store=True, string="Proyecto")
    cliente= fields.Many2one("res.partner", "Campo de apoyo")
    empresa_relacionada= fields.Many2one("res.partner", string="Empresa relacionada", related="partner_id.parent_id", readonly=True)
    ocultar_equipos=fields.Boolean("Ocultar equipos", compute='_ocultar_equipos')
    modelo_id=fields.Many2one("equipo.entrust.contrato", string='Modelo')
    equipo_id=fields.Many2one("equipo.entrust",string="Equipo")
    contrato_id=fields.Many2one("equipo.entrust.contrato",string="Contrato")
    bitacoras=fields.One2many("bitacora.servicio","ticket",string="Bitacoras")
    fichas = fields.One2many("entrega.producto", "ticket", string="Fichas")
    persona_contacto_id = fields.Many2one("res.partner", string="Persona de contacto")
    persona_contacto_telefono = fields.Char(related='persona_contacto_id.mobile',string="Teléfono de contacto")
    tipo_contrato_id = fields.Selection([("1", " Plan Básico"), ("2", "Plan Plus"), ("3", "Plan Premiun")],string="Tipo de contrato")
    responsable = fields.Many2one("hr.employee", "Tecnico Servicios")
    tecnico = fields.Many2one("hr.employee", string="Comercial")
    fecha = fields.Date()
    modelo_id_ = fields.Many2one("product.template",related="equipo_id.modelo", string="Modelo")
    partner_email = fields.Char(string='Customer Email', related='partner_id.email', store=True, readonly=False)

    # Se agregan los siguientes campos por ticket 1893
    # encuesta = fields.Boolean(string = "¿La encuesta de satisfacción ya fue realizada?", compute = '_validar_encuesta', default = False)
    # calificacion_servicio = fields.Selection([
    #     ('5',"Excelente"),
    #     ('4',"Bueno"),
    #     ('3',"Regular"),
    #     ('2',"Malo"),
    #     ('1',"Pésimo")],
    #     string="¿Qué le pareció el servicio?"
    # )
    # probabilidad_recomendacion = fields.Integer(string = "Del 1 al 10, ¿qué tan probable es que nos recomiende?")

    # @api.depends('calificacion_servicio', 'probabilidad_recomendacion')
    # def _validar_encuesta(self):
    #     """
    #     ticket 1893: se agregan campos de encuesta de satisfacción al ticket por cambio de método en realizar esta
    #     """
    #     for record in self:
    #         if record.calificacion_servicio and record.probabilidad_recomendacion:
    #             record.encuesta = True
    #         else:
    #             record.encuesta = False

    @api.depends('timesheet_ids')
    def _compute_total_hours_spent(self):
        for ticket in self:
            total_hours_spent = 0.0
            for timesheet in ticket.timesheet_ids:
                if timesheet.contable:
                    total_hours_spent += timesheet.unit_amount
            ticket.total_hours_spent = round(total_hours_spent, 2)


    @api.depends("partner_id")
    def _actualizar_equipos(self):
        for record in self:
            #Limpia todas las filas
            record.equipos_disponibles=[(5,0,0)]

            #Si el cliente esta definido buscamos los equipos
            if record.partner_id:
                #Se utiliza el metodo search del ORM, provee 4 metodos base que son, search (SELECT), create (INSERT), write (UPDATE), unlink (DELETE), copy (duplica registro)
                #se accede mediante self.env['nombre.modelo']
                #las condiciones se ponen en tuplas
                #la funcion mas abajo en SQL se veria asi:
                # SELECT * from equipos_entrust where partner_id=%s

                contratos=self.env['equipo.entrust.contrato'].search([('cliente','=',record.partner_id.id)])

                #Si encuentra algo vendra un recordset, o lista/diccionario de objetos que encontro
                #si no encuentra nada, viene False, se prueba con un if

                if contratos:
                    #El cliente tiene contratos, al menos 1
                    # Vamos a crear las lineas
                    # para eso usamos un diccionario con los valores que vamos a agregar
                    # y se hace un create por cada valor

                    for contrato in contratos:
                        for equipo in contrato.equipos:
                            valor={
                                'ticket_id':record.id,
                                'contrato':contrato.id,
                                'modelo':contrato.modelo_equipo.id,
                                'serie':equipo.id,
                                'fecha_inicio':contrato.fecha_inicio,
                                'fecha_vencimiento':contrato.fecha_vencimiento
                            }
                            self.env['helpdesk.ticket.linea'].create(valor)




    
    
    equipos_disponibles=fields.One2many("helpdesk.ticket.linea","ticket_id",string="Equipos disponibles",compute=_actualizar_equipos,store=True)

    # Métodos específicos para AK Digital relacionados a helpdesk.ticket
    def check_last_update_and_notify(self):
        """
        ticket 1707:
        Se crea el método para agrupar los tickets que cumplan ciertos requisitos por responsable
        para posteriormente enviar esta info por correo
        """
        day = datetime.today().weekday()
        today = datetime.today()
        lapse = 0
        if day >= 5:
            return

        # Si se verifica entre jueves y viernes, los tres días hábiles estarán dentro de la misma semana.
        # Si se verifica entre lunes y miércoles, se tienen que sumar dos días más para no tomar en cuenta
        # los fines de semana.
        if day > 2: lapse = 3
        else: lapse = 5

        three_business_days_ago = fields.Datetime.now() - timedelta(days=lapse)

        tickets = self.search([('write_date', '<', three_business_days_ago),
                               ('team_id.id', 'in', [5, 6, 13]), # Equipo de mesa de asistencia: Odoo - Mesa de ayuda (5), Oracle BI - Mesa de ayuda (6) y Soportes internos AKD (13)
                               ('stage_id.id', 'not in', [17, 38]), # Estados de cerrado de tickets: Cerrada - MDA (Valoración) (17), Cerrado (38)
                               ('active', '=', True)])
        
        tickets_dict = {}
        tickets_dict_lider = {}

        # Agrupamos los tickets por responsables y los metemos todos en una lista para un correo general a Cynthia, Ramón y Róger
        for ticket in tickets:

            if ticket.user_id:

                # Si el encargado del ticket no está en el diccionario, se agrega con una lista vacía
                if ticket.user_id not in tickets_dict:
                    tickets_dict[ticket.user_id] = []

                # Y llenamos la lista con sus tickets
                tickets_dict[ticket.user_id].append(ticket)

                # Ahora, para los líderes, se llenará un diccionario, donde, agruparemos por cliente y por estado
                if ticket.partner_id:
                    
                    cliente = ticket.partner_id

                    # Agrupamos por cliente
                    if cliente not in tickets_dict_lider:
                        tickets_dict_lider[cliente] = {}

                    if ticket.stage_id:

                        etapa = ticket.stage_id

                        # Agrupamos por etapa
                        if etapa not in tickets_dict_lider[cliente]:
                            tickets_dict_lider[cliente][etapa] = []

                        # Por solicitud del ticket 1834, se agrega la cantidad de días en los que el ticket no ha sido trabajado
                        diferencia_fecha = today - ticket.write_date
                        diferencia_dias = diferencia_fecha.days

                        tickets_dict_lider[cliente][etapa].append((ticket, diferencia_dias))

        # Cuando termino de recorrer todos los tickets, se enviará el correo si hay al menos uno, tanto a los responsables, como a Cynthia, Ramón y Róger
        if len(tickets_dict) > 0:
            self.correo_por_responsables(tickets_dict)
        if len(tickets_dict_lider) > 0:
            self.correo_por_encargados(tickets_dict_lider)

    def correo_por_responsables(self, tickets):
        """
        ticket 1707:
        Se crea el método para enviar una notificación por correo de la inactividad de tickets en 3 días hábiles a sus responsables
        """
        for responsable in tickets:
            # Load the email template
            template = self.env.ref('servicios_tecnologicos.correo_responsable_seguimiento_tickets')
        
            # Render the template with custom variables
            template_ctx = {
                'responsable': responsable,
                'tickets': tickets[responsable],
            }

            # Compose the email
            mail_values = {
                'subject': 'Recordatorio diario',
                'email_from': 'odoo@akdigitales.com',
                'email_to': responsable.login,
            }

            template.with_context(template_ctx).send_mail(7, email_values = mail_values, force_send=True)

    def correo_por_encargados(self, tickets):
        """
        ticket 1707:
        Se crea el método para enviar una notificación por correo de la inactividad de tickets en 3 días hábiles a los indicados 
        """

        # Agregar o cambiar correos según decisiones futuras
        correos = ['carauz@akdigitales.com', 'rramirez@akdigitales.com','ysaenz@akdigitales.com']
        encargados = ['Cynthia', 'Ramón', 'Yuri']
        cant_correos = len(correos)

        for n in range(cant_correos):
            # Load the email template
            template = self.env.ref('servicios_tecnologicos.correo_encargado_seguimiento_tickets')
        
            # Render the template with custom variables 
            template_ctx = {
                'encargado': encargados[n],
                'tickets': tickets,
            }

            # Compose the email
            mail_values = {
                'subject': 'Recordatorio diario',
                'email_from': 'odoo@akdigitales.com',
                'email_to': correos[n],
            }

            template.with_context(template_ctx).send_mail(7, email_values = mail_values, force_send=True) 
                
class LineaTicket(models.Model):
    _name="helpdesk.ticket.linea"
    _description="Linea de ticket con equipos disponibles"

    ticket_id=fields.Many2one("helpdesk.ticket","Ticket al que pertenece")
    contrato=fields.Many2one("equipo.entrust.contrato","Contrato")
    modelo=fields.Many2one("product.template","Modelo")
    serie=fields.Many2one("equipo.entrust","Serie")
    fecha_inicio=fields.Date("Fecha de inicio")
    fecha_vencimiento=fields.Date("Fecha de vencimiento")


    def seleccionar(self):
        self.ticket_id.equipo_id=self.serie.id
        self.ticket_id.contrato_id=self.contrato.id





        
