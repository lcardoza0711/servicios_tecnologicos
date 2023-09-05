import re
from odoo import api, models, fields
from dateutil.relativedelta import relativedelta
import locale
from datetime import datetime, date, timedelta



class EquipoEntrust(models.Model):
    _name="equipo.entrust"
    _description="Equipos Entrust"
    # _inherit = ['mail.thread']
    @api.depends('tickets')
    def _get_tickets(self):
        if self.tickets:
            for ticket in self.tickets:
                self.total_horas_dedicadas += ticket.total_hours_spent


    cant_dispositivos = fields.Integer("Cantidad")
    name = fields.Char("Serie del equipo")
    anio_fabricacion=fields.Char("Año de fabricación")
    responsable_cliente=fields.Char("Responsable del cliente")
    descripcion_equipo=fields.Char("Descripcion del equipo")
    primera_visita=fields.Boolean("Primera visita", tracking=True)
    segunda_visita=fields.Boolean("Segunda visita", tracking=True)
    tercera_visita=fields.Boolean("Tercera visita" , tracking=True)
    cuarta_visita=fields.Boolean("Cuarta visita" , tracking=True)
    quinta_visita=fields.Boolean("Quinta visita", tracking=True)
    sexta_visita=fields.Boolean("Sexta visita", tracking=True)
    
    modelo=fields.Many2one("product.template",string="Modelo del equipo") #CD800/Sigma ect

    marca=fields.Many2one("product.brand",string="Marca del equipo")                        
    modulos=fields.One2many("equipo.entrust.modulo", "equipo_id",string="Modulos disponibles")

    mantenimiento_id=fields.Many2one("equipo.mantenimiento",string="Mantenimientos realizados")           
    parte = fields.Char(string='Numero de Parte')
    categorias = fields.Many2one("equipo.categoria", "Categoria")

    garantia=fields.One2many("equipo.entrust.garantia","equipo_id",string="Garantia del Equipo")
    entregas = fields.Many2many("entrega.producto",string="Entregas")   
    contrato_id = fields.Many2one("equipo.entrust.contrato","Contrato al que pertenece")
    
    fecha_adquisicion=fields.Date("Fecha de adquisicion")        

    tickets=fields.One2many("helpdesk.ticket","equipo_id",string="Tickets de servicio")


    bitacoras=fields.One2many("bitacora.servicio","equipo",string="Bitacoras de servicio")
    fichas = fields.One2many("entrega.producto", "equipos",string="Fichas de entrega")
    tecnico = fields.Many2one("hr.employee", string="Comercial")
    total_horas_dedicadas = fields.Float(compute ="_get_tickets" ,string="Total de horas dedicadas")

    itemCode = fields.Char("Número de articulo") #
    status = fields.Char("Estado")
    InsID = fields.Char("Número de tarjeta de Equipo")
    itemName = fields.Char("Descripción del artículo")


    #Se necesita asociar el cliente sobre el equipo
    cliente=fields.Many2one("res.partner",string="Cliente")
    customer =fields.Char(string= "Codigo de cliente")
    cntctPhone = fields.Char(related='cliente.mobile',string="Teléfono de contacto")
    persona_contacto = fields.Many2one("res.partner", string="Persona Contacto")
    persona_contacto_telf = fields.Char(related="persona_contacto.phone", string="Telefono de Contacto")




#TODO: Por hacer
class EquipoMantenimiento(models.Model):
    _name = "equipo.mantenimiento"
    _description = "Mantenimiento de equipos"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #JALAMOS los mantenimientos

    #Consecutivo autogenerado   
    name=fields.Char("Numero de visita")
 
    #Referente al equipo que esta en mantenimiento, revisarlo, esta al reves
    equipo_id = fields.One2many("equipo.entrust", "mantenimiento_id",string="Equipo")           
    equipo_visita= fields.Many2one("equipo.entrust", related ="ticket_id.equipo_id", string="Visita" )
    ticket_id= fields.Many2one("helpdesk.ticket")
    #Referente al mantenimiento
    # recuento=fields.Integer("Cuenta",default=1)
    # localizacion=fields.Char("Localizacion")
    # descripcion=fields.Char("Descripción")
    # numero_factura=fields.Char("Numero de factura")
    fecha_ultimo_mantenimiento=fields.Date("Último mantenimiento")
    # fecha_factura=fields.Date("Fecha de factura")
    # foto=fields.Image("Foto del equipo")
   
    #Si esta bien, pero son campos relacionales
    contrato_id=fields.Many2one("equipo.entrust.contrato",string="Contrato de servicio")
    garantia=fields.One2many("equipo.entrust.garantia","equipo_id",string="Garantia de servicio")
    cliente=fields.Many2one("res.partner",string="Cliente")

    tecnico=fields.Many2one("hr.employee",string="Empleado")
    estado_contrato=fields.Selection(string="Estatus de contrato",related="contrato_id.estado")


    visitas=fields.One2many('helpdesk.ticket',"equipo_id",string="Visitas")  #TODO Crear relacion


class OportunidadRenovacion(models.Model):
    _inherit = "crm.lead"

    contrato_soporte=fields.Many2one("equipo.entrust.contrato")

    def ver_contrato(self):

        view = self.env.ref('servicios_tecnologicos.view_equipo_entrust_contrato_form')
        
        return {            
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model':'equipo.entrust.contrato',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.contrato_soporte.id,
            'context': self.env.context,
        }


class EquipoEntrustContrato(models.Model):
    _name = "equipo.entrust.contrato"
    _description = "Contrato de equipo"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def gestionar_renovacion(self):
        for record in self:
            oportunidad=self.env['crm.lead'].create(
                {
                    'contrato_soporte':record.id,
                    'date_deadline':record.fecha_vencimiento-timedelta(days=15),
                    'partner_id':record.cliente.id,
                    'team_id':21,
                    'user_id':13,
                    'linea':3,
                    'source_id':33,
                    'stage_id':254,
                    'company_id':1,
                    'type':'opportunity',
                    'name':record.descripcion
                }
            )


    @api.model
    def send_email(self):
        contratos = self.env['equipo.entrust.contrato'].search([('fecha_primera','>=',datetime.today())])
        print(contratos)
        for contrato in contratos:
            diferencia = contrato.fecha_primera - datetime.today().date()
            #TODO Escalabilidad de envios de correos
            if contrato.primera_correo == False:
                if diferencia.days == 7:
                    mail_template = self.env.ref('servicios_tecnologicos.email_template_akad_tecnico_reminder_mantenimiento_semana')
                    mail_template.send_mail(self.id, force_send=True)
                    contrato.primera_correo= True
            if contrato.segundo_correo == False:
                if diferencia.days == 0:
                    mail_template = self.env.ref('servicios_tecnologicos.email_template_akad_tecnico_reminder_mantenimiento_due')
                    mail_template.send_mail(self.id, force_send=True)
                    contrato.segundo_correo= True



    @api.depends("fecha_inicio")
    def mes_espanol(self):
        if self.fecha_inicio:
            loc = locale.setlocale(locale.LC_ALL, 'es-ES')
            return self.fecha_inicio.strftime("%B")


    now = fields.Date(string="From Date" ,default=datetime.now())
    estado_mantenimiento = fields.Char("Estado de mantenimiento")
    
    recuento=fields.Integer("Cuenta",default=1)
    equipo_id = fields.Many2one("equipo.entrust")
    name = fields.Char("Numero de contrato", readonly=False,required=True, copy=False,default="Nuevo")
    descripcion=fields.Char("Observaciones")
    codigo_cliente = fields.Char(string= "Codigo de socio de negocios", readonly=False )
    codigo_cliente_sap = fields.Char(string= "Codigo de socio de negocios", readonly=False )
    Descriptio = fields.Char(string= "Nivel de contrato ",  tracking=True)
    cliente=fields.Many2one("res.partner","Cliente")
    #nivel_contrato=fields.Many2one("product.template","Tipo de contrato")
    persona_contacto= fields.Many2one( "res.partner",string="Persona Contacto",  tracking=True)
    persona_contacto_telf= fields.Char( related="persona_contacto.phone",string="Telefono de Contacto")
    nivel_contrato=fields.Selection([("1"," Plan Básico"),("2","Plan Plus"),("3","Plan Premiun")], string="Tipo de contrato")
    responsable=fields.Many2one("hr.employee","Tecnico Servicios",  tracking=True)
    sale_order_id=fields.Many2one("sale.order","Orden de venta")
    tecnico=fields.Many2one("hr.employee",string="Técnico a cargo",  tracking=True)
    tipo_servicio=fields.Selection([('regular',"Regular"),('garantia',"Garantía")], string="Tipo de servicio")
    tipo_contrato=fields.Selection([("entrust_e","Entrust escritorio"),("entrust_f","Entrust financieros"),("entrust_c","Entrust centralizado"),("entrust_p","Entrust pasaporte"),("seguridad_c","SE Camaras"),("seguridad_a","SE Control de Acceso"),("dmd","Soporte DMD")],string="Tipo de contrato")

    @api.depends('dia','fecha_inicio')
    def _calcular_dia(self):
        day = date.fromisoformat(str(self.env['equipo.entrust.contrato'].search([('name','=',self.name)])))
        self.dia = self.fecha_inicio.day
 
    fecha_inicio = fields.Date("Fecha de inicio del contrato",  tracking=True)
    dia=fields.Char(string="Día")
    mes=fields.Char(string="Mes")
    anio=fields.Char(string="Año")
    fecha_vencimiento = fields.Date("Fecha vencimiento",  tracking=True)

    @api.depends('fecha_vencimiento', 'fecha_primera')
    def _calculo_fecha(self):
        for record in self:
            if record.fecha_vencimiento != False:
                record.fecha_primera = record.fecha_vencimiento - relativedelta(months=7)
            if record.fecha_primera != False:
                record.fecha_segunda = record.fecha_primera + relativedelta(months=5)






    @api.depends('fecha_vencimiento')
    def _calculo_fecha_aviso(self):
        for record in self:
            if record.fecha_vencimiento:
                record.fecha_aviso_v = record.fecha_vencimiento - relativedelta(months=7)
            else:
                record.fecha_aviso_v = False
    visitas=fields.One2many('helpdesk.ticket',"contrato_id",string="Visitas")
    equipos = fields.One2many("equipo.entrust", "contrato_id", string="Serie de los equipos") #Campo en Notebook
    modelo_equipo = fields.Many2many("product.template",default="", string="Modelo")
    mantenimientos = fields.One2many("bitacora.servicio", "contrato", string="Mantenimientos registrados")
    mantenimientos_id = fields.Many2many("bitacora.servicio", string="Mantenimientos registrados")
    fecha_mantenimiento= fields.Date(string="Fecha De mantenimiento", related="mantenimientos_id.fecha_mantenimiento")
    fecha_entrega= fields.Date(string="Fecha De mantenimiento", related="mantenimientos_id.fecha_entrega")
    bitacoras=fields.One2many("bitacora.servicio","contrato",string="Bitacoras de servicio")

    @api.onchange('fecha_inicio')
    def renovar_contrato(self):
        for record in self:
            record.message_notify(body="Contrato renovado")
            for equipo in record.equipos:
                equipo.primera_visita=False
                equipo.segunda_visita=False
                equipo.tercera_visita=False
                equipo.cuarta_visita=False
                equipo.quinta_visita=False
                equipo.sexta_visita=False


    @api.depends('equipos.primera_visita','equipos.segunda_visita','equipos.tercera_visita','equipos.cuarta_visita','equipos.quinta_visita','equipos.sexta_visita')
    def _validar_visita(self):
        for record in self:
            record.primera_visita=True
            record.segunda_visita=True
            record.tercera_visita=True
            record.cuarta_visita=True
            record.quinta_visita=True
            record.sexta_visita=True

            for equipo in record.equipos:
                record.primera_visita=record.primera_visita and equipo.primera_visita
                record.segunda_visita=record.segunda_visita and equipo.segunda_visita
                record.tercera_visita=record.tercera_visita and equipo.tercera_visita
                record.cuarta_visita=record.cuarta_visita and equipo.cuarta_visita
                record.quinta_visita=record.segunda_visita and equipo.quinta_visita
                record.sexta_visita=record.segunda_visita and equipo.sexta_visita
            
            if not record.equipos:
                record.primera_visita=False
                record.segunda_visita=False
                record.tercera_visita=False
                record.cuarta_visita=False
                record.quinta_visita=False
                record.sexta_visita=False


    primera_visita=fields.Boolean("Primera visita", tracking=True, compute=_validar_visita,store=True,readonly=True)
    segunda_visita=fields.Boolean("Segunda visita", tracking=True, compute=_validar_visita,store=True,readonly=True)

    tercera_visita=fields.Boolean("Tercera visita" , tracking=True, compute=_validar_visita,store=True,readonly=True)
    cuarta_visita=fields.Boolean("Cuarta visita" , tracking=True, compute=_validar_visita,store=True,readonly=True)
    quinta_visita=fields.Boolean("Quinta visita", tracking=True, compute=_validar_visita,store=True,readonly=True)
    sexta_visita=fields.Boolean("Sexta visita", tracking=True, compute=_validar_visita,store=True,readonly=True)

    primera_correo=fields.Boolean("Primera correo")
    segundo_correo=fields.Boolean("Segundo correo")
    tipo_visita=fields.Selection([('Mensual',"Mensual"),("BiMensual","BiMensual"),("Trimestral","Trimestral")], string="Tipo de visita")
    InsID = fields.Char(related= "equipos.InsID")
    modelo = fields.Char(related="equipos.modelo.name")
    itemCode= fields.Char(related="equipos.itemCode")
    parte = fields.Char(related="equipos.parte")
    estado_cont = fields.Selection([("Cancelado", "Cancelado"),("renovacion", "Renovación"), ("vigente", "Vigente"), ("retrasado", "Retrasado"),
                                    ("Pendiente los dos mantenimiento", "Pendiente los dos mantenimiento"),
                                    ("Pendiente un Mantenimiento", "Pendiente un Mantenimiento")], string="Estado")  # ,compute=_estado, store=True,string="Estado")
    estado = fields.Selection([("0", "Cancelado"), ("1", "Pendiente de firma"), ("2", "Autorizado")],
                              string="Estado de contrato")

    fecha_primera = fields.Date("Primera fecha de mantenimiento", compute=_calculo_fecha, store=True, readonly=False)
    fecha_segunda = fields.Date("Segunda fecha de mantenimiento", compute=_calculo_fecha, store=True, readonly=False)


    """"
    change_state_contrato contralará el estado de el contrato entre la siguiente lista de estado 
    -> Cuando este Authorizado y agendado las dos citas (con sus fechas establecidas) y tenga mas de 150 dias para realizar la primera visita ->  Pendiente los dos mantenimiento
    -> Cuando este Authorizado y agendado las dos citas (con sus fechas establecidas) y tenga mas de 150 dias para realizar la segunda visita -> Pendiente un Mantenimiento
    -> Cuando este Autorizado y no se ha agendado las dos primeras visitas y esta
    """

    # Métodos AK Digital
    def check_future_maintenance(self):
        """
        ticket 1805:
        Se crea el método para agrupar los contratos según la fecha de mantenimiento se acerca, a modo de recordatorio
        para el técnico y el encargado 
        """
        hoy = date.today()
        quince_dias = hoy + timedelta(days=15)
        treinta_dias = hoy + timedelta(days=30)

        # Tomar los contratos donde la fecha de alguno de los dos mantenimientos esté pactada para dentro de 15 días
        # Y que no se haya dado, además, que el estado del contrato no esté en cancelado
        contratos_quince_dias = self.search([
                                            '|',
                                            '&', ('fecha_primera', '=', quince_dias), ('primera_visita', '=', False),
                                            '&', ('fecha_segunda', '=', quince_dias), ('segunda_visita', '=', False),
                                            ('estado', '!=', '0')
                                        ])
        
        # Exactamente lo mismo, pero ahora los que estén pactados para dentro de 30 días exactamente
        contratos_treinta_dias = self.search([
                                                '|',    
                                                '&', ('fecha_primera', '=', treinta_dias), ('primera_visita', '=', False),
                                                '&', ('fecha_segunda', '=', treinta_dias), ('segunda_visita', '=', False),
                                                ('estado', '!=', '0')
                                            ])
        
        contratos_quince_dict = {}
        contratos_treinta_dict = {}
        clientes_quince_dict = {}

        # Agrupamos los contratos que tienen visitas pactadas dentro de 15 días, por técnico, y por cliente
        for contrato in contratos_quince_dias:

            if contrato.tipo_contrato in ['entrust_e', 'entrust_f', 'entrust_c', 'entrust_p']:
                if contrato.responsable:
                    
                    # Si el encargado del contrato no está en el diccionario, se agrega con una lista vacía
                    if contrato.responsable not in contratos_quince_dict:
                        contratos_quince_dict[contrato.responsable] = []

                    # Y llenamos la lista con sus contratos, pero, en forma de tupla, donde, en la primera posición validaré si el
                    # mantenimiento que falta es el primero, o el segundo
                    contratos_quince_dict[contrato.responsable].append(
                        ("primer" if contrato.fecha_primera == quince_dias else "segundo", contrato))
                
            # Si el contrato tiene cliente, se hace la misma lógica que arriba
            if contrato.cliente:

                if contrato.cliente not in clientes_quince_dict:
                    clientes_quince_dict[contrato.cliente] = []
                
                clientes_quince_dict[contrato.cliente].append(
                    ("primer" if contrato.fecha_primera == quince_dias else "segundo", contrato))

        # Agrupamos los contratos que tienen visitas pactadas dentro de 30 días, por técnico
        for contrato in contratos_treinta_dias:

            if contrato.tipo_contrato in ['entrust_e', 'entrust_f', 'entrust_c', 'entrust_p']:
                if contrato.responsable:
                    
                    # Si el encargado del contrato no está en el diccionario, se agrega con una lista vacía
                    if contrato.responsable not in contratos_treinta_dict:
                        contratos_treinta_dict[contrato.responsable] = []

                    # Y llenamos la lista con sus contratos, pero, en forma de tupla, donde, en la primera posición validaré si el
                    # mantenimiento que falta es el primero, o el segundo
                    contratos_treinta_dict[contrato.responsable].append(
                        ("primer" if contrato.fecha_primera == treinta_dias else "segundo", contrato))

        # Cuando termino de recorrer todos los contratos, se enviará el correo si hay al menos uno
        if len(contratos_quince_dict) > 0 or len(contratos_treinta_dict) > 0:
            self.correos_mantenimiento_proximo(contratos_quince_dict, contratos_treinta_dict)

        if len(clientes_quince_dict) > 0:
            self.correos_mantenimiento_proximo_cliente(clientes_quince_dict)

    def correos_mantenimiento_proximo(self, contrato_quince, contrato_treinta):
        """
        ticket 1805:
        Se crea el método para enviar una notificación por correo de que un mantenimiento preventivo se acerca en un lapso de 15 o 30 días
        """

        lider = "ghernandez@akdigitales.com"

        if len(contrato_quince) > 0:
            for responsable in contrato_quince:
                # Load the email template
                template = self.env.ref('servicios_tecnologicos.correo_mantenimiento_quince')
            
                # Render the template with custom variables
                template_ctx = {
                    'responsable': responsable,
                    'contratos': contrato_quince[responsable],
                }

                # Compose the email
                mail_values = {
                    'subject': '¡Los siguientes mantenimientos son dentro de 15 días!',
                    'email_from': 'odoo@akdigitales.com',
                    'email_to': responsable.work_email,
                    'email_cc': lider,
                }

                template.with_context(template_ctx).send_mail(1, email_values = mail_values, force_send=True)

        if len(contrato_treinta) > 0:
            for responsable in contrato_treinta:
                # Load the email template
                template = self.env.ref('servicios_tecnologicos.correo_mantenimiento_treinta')
            
                # Render the template with custom variables
                template_ctx = {
                    'responsable': responsable,
                    'contratos': contrato_treinta[responsable],
                }

                # Compose the email
                mail_values = {
                    'subject': '¡Los siguientes mantenimientos son dentro de 30 días!',
                    'email_from': 'odoo@akdigitales.com',
                    'email_to': responsable.work_email,
                    'email_cc': lider,
                }

                template.with_context(template_ctx).send_mail(1, email_values = mail_values, force_send=True)

    def correos_mantenimiento_proximo_cliente(self, contrato_quince):
        """
        ticket 1805:
        Se crea el método para enviar una notificación por correo de que un mantenimiento preventivo se acerca dentro de 15 días, al cliente
        """

        test_email = "ghernandez@akdigitales.com"

        if len(contrato_quince) > 0:
            for cliente in contrato_quince:
                # Load the email template
                template = self.env.ref('servicios_tecnologicos.correo_mantenimiento_quince_cliente')
            
                # Render the template with custom variables
                template_ctx = {
                    'cliente': cliente,
                    'contratos': contrato_quince[cliente],
                }

                # Compose the email
                mail_values = {
                    'subject': '¡El mantenimiento se acerca!',
                    'email_from': 'odoo@akdigitales.com',
                    'email_to': test_email,
                }

                template.with_context(template_ctx).send_mail(1, email_values = mail_values, force_send=True)



class EquipoEntrustGarentia(models.Model):
    _name = "equipo.entrust.garantia"
    _description = "Garantia de equipo"

    name = fields.Char("Garantia del equipo")    
    fecha_inicio = fields.Date("Fecha de inicio")
    fecha_vencimiento = fields.Date("Fecha de vencimiento")
    descripcion=fields.Char(string="Descripcion de cobertura")
    tipo=fields.Selection([('0','Equipo'),('1','Repuesto'),('2','Software')])
    
    equipo_id = fields.Many2one("equipo.entrust", string="Garantias registradas")
    estado_garantia=fields.Selection([("1","Activo"),("0","Inactivo")],string="Estatus de garantía")
class EquipoEntrustModulos(models.Model):
    _name="equipo.entrust.modulo"
    _description="Modulos de equipos Entrust"

    name=fields.Char("Nombre")
    serie = fields.Char("Número de serie")
    #Configuracion de campo many2one en modelo destino
    equipo_id = fields.Many2one("equipo.entrust", string="Equipo al que pertenece el modulo")
    fichas = fields.Many2one("entrega.producto", string="Ficha del modulo")
class EquipoCategoria(models.Model):
    _name = "equipo.categoria"
    _description = "Categorias de los equipos"
    name = fields.Char("Categoria")
    categoria = fields.One2many("equipo.entrust", "categorias", string = "Categorias registradas")
class EquipoEntrustModelo(models.Model):
    _name="equipo.entrust.modelo"
    _description="Modelo de equipos Entrust"

    name=fields.Char("Nombre del modelo")
    equipos=fields.One2many("equipo.entrust.modelo","name",string="Equipos registrados")
