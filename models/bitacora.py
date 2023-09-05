from odoo import api, models, fields
from odoo.exceptions import ValidationError

class BitacoraServicio(models.Model):
    _name="bitacora.servicio"
    _description="Bitacora de servicio"

    def action_launch_survey(self):
        self.ensure_one()
        survey_id = 6
        survey = self.env['survey.survey'].browse(survey_id)
        partner = self.ticket.partner_id
        answer_token = survey.access_token
        prefill_vals = {
            '1': partner.name,  # Replace '1' with the correct question ID for the first question
            '2': partner.email,  # Replace '2' with the correct question ID for the second question
        }
        prefill_url = '&'.join([f"{key}={value}" for key, value in prefill_vals.items()])
        survey_url = "https://odoo.akdigitales.com/survey/start/"+answer_token
        return {
            'type': 'ir.actions.act_url',
            'url': survey_url,
            'target': 'new',
        }

    #Se agregan las lineas segun la plantilla
    @api.depends("ticket","plantilla")
    def _agregar_lineas_bitacora(self):
        for record in self:
            if record.plantilla:                        
                linea_plantilla = self.env['bitacora.servicio.linea']
                res=[]

                for linea in record.plantilla.lineas:                

                    linea_p={
                        'bitacora_id': record.id,
                        'name': linea.pregunta,
                        'seccion': linea.seccion
                    }
                    nueva=linea_plantilla.create(linea_p)
                    res.append(nueva.id)

                record.lineas_bitacora=[(6,0,res)]

            else:
                pass #Nada que hacer, no hay plantilla, salado pescado


    def actualizar_visita_equipo(self, id):
        bitacora = self.env['bitacora.servicio'].search([('id','=',id)])
        if bitacora.equipo.primera_visita == False:
            bitacora.equipo.primera_visita = True
        elif bitacora.equipo.segunda_visita == False:
            bitacora.equipo.segunda_visita = True

        elif bitacora.equipo.tercera_visita == False:
            bitacora.equipo.tercera_visita = True
        elif bitacora.equipo.cuarta_visita == False:
            bitacora.equipo.cuarta_visita = True
        elif bitacora.equipo.quinta_visita == False:
            bitacora.equipo.quinta_visita = True
        elif bitacora.equipo.sexta_visita == False:
            bitacora.equipo.sexta_visita = True


    @api.model
    def create(self, vals):

        print('Sobrecargado')
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('bitacora.entrust') or "Nuevo"
        re = super(BitacoraServicio, self).create(vals)
        self.actualizar_visita_equipo(re.id)

        return re


    @api.depends('plantilla')
    def _ocultar(self):

        #if self.plantilla['name']== 'Bitácora de inspección':
        #    self.ocultar=True
        #Se filtrar por nombre de plantilla, mas adelante pordemos hacerlo mas dinamico

        #elif self.plantilla['name']=='Seguridad Electrónica - Inspección':
        #     self.ocultar = True

        #else:
        #    self.ocultar= False
        self.ocultar = False




    #INSPECCIÓN
    completado=fields.Boolean("Completado")
    linea_op1= fields.Boolean("Control de acceso/asistencia")
    linea_op2= fields.Boolean("CCTV")
    linea_op3= fields.Boolean("Soluciones especiales")
    linea_op4= fields.Boolean("Casa inteligente")
    linea_op5= fields.Boolean("Software")
    linea_op6= fields.Boolean("Servicios")
    otra_linea_dis= fields.Text('Otra')
    pregunta_1= fields.Text('¿Qué podemos ofrecer?')
    lineas_dispositivos= fields.Many2many("equipo.entrust")
    telefono_partneer = fields.Char("Teléfono",related="cliente.mobile")
    trabajo_previo = fields.Boolean("Trabajos de acondicionamiento previo")
    servicio_terceros = fields.Boolean("¿Requiere servicios de terceros?")
    grado_dificultad = fields.Selection([('alto', "Alto"), ("medio", "Medio"), ("bajo", "Bajo")], string="Grado de dificultad de la instalación")
    horas_disponibles = fields.Float(string="Horas posibles de la instalación")
    dias_posibles = fields.Float(string="Días posibles de la instalación")

    detalle_trabajo_prev= fields.Text("Detalle")




    #SEGURIDAD ELECTRONICA
    name=fields.Char("Numero de bitacora", readonly=True,required=True, copy=False,default="Nuevo")
    cliente=fields.Many2one("res.partner","Cliente")
    fecha=fields.Date("Fecha")
    
    ticket=fields.Many2one("helpdesk.ticket","Ticket")

    contrato=fields.Many2one("equipo.entrust.contrato","Contrato",related="ticket.contrato_id",readonly=False, store=True)
    equipo=fields.Many2one("equipo.entrust","Equipo",related="ticket.equipo_id",readonly=False,store=True)
    # equipo_id=fields.Many2one("equipo.entrust","Equipo",compute="_equipos", store=True)

    #La plantilla sera dependiendo del tipo de bitacora
    plantilla=fields.Many2one("bitacora.servicio.plantilla","Plantilla",related="equipo.modelo.tipo_bitacora", store=True, readonly=False)
    ocultar=fields.Boolean(compute='_ocultar', readonly= False
                        )

    #Se toma del equipo
    descripcion_equipo=fields.Char(related="equipo.descripcion_equipo",string="Descripcion del equipo", readonly=False, store=True)
    fecha_adquisicion=fields.Date(related="equipo.fecha_adquisicion",string="Fecha de adquisicion", readonly=False, store=True)
    tecnico_responsable=fields.Many2one("hr.employee",related="equipo.tecnico",string="Tecnico", readonly=False, store=True)
    responsable_cliente=fields.Char(related="equipo.responsable_cliente", string="Responsable del equipo", readonly=False, store=True)

    #Se toma del ticket
    solicitud_visita=fields.Char("Motivo de visita", readonly= False)
    fecha_recepcion=fields.Date("Fecha de recepcion", readonly= False)
    estado_recepcion=fields.Text("Estado de recepcion del equipo", readonly= False)
    fecha_inspeccion=fields.Date("Fecha de inspeccion")
    estado_inspeccion=fields.Text("Estado de inspeccion")
    lineas_bitacora=fields.One2many("bitacora.servicio.linea","bitacora_id",string="Lineas",compute=_agregar_lineas_bitacora, store=True, copy=True, readonly=False)



    #Mantenimiento
    fecha_mantenimiento=fields.Date("Fecha de mantenimiento", readonly= False)
    estado_mantenimiento=fields.Text("Estado de mantenimiento del equipo")

    #Entrega
    fecha_entrega=fields.Date("Fecha de entrega")
    estado_entrega=fields.Text("Estado de entrega del equipo")

    notas=fields.Text("Notas")
    x_studio_firma_de_cliente = fields.Binary("Firma electrónica", store = True, copy = True, no_copy = False)


    #Fotos antes y despues del mantenimiento 

    img_antes1 = fields.Image("Fotos Antes del mantenimiento")
    img_antes2 = fields.Image("Fotos Antes del mantenimiento")
    img_antes3 = fields.Image("Fotos Antes del mantenimiento")
    img_despues1 = fields.Image("Fotos Despues del mantenimiento")
    img_despues2 = fields.Image("Fotos Despues del mantenimiento")
    img_despues3 = fields.Image("Fotos Despues del mantenimiento")



class LineaBitacoraServicio(models.Model):
    #Estas lineas apareceran segun la plantilla
    _name="bitacora.servicio.linea"
    _description="Linea de bitacora de servicio"
    
    name=fields.Char("Pregunta")
    completado=fields.Boolean("Completado")
    incidencia=fields.Boolean("Incidencia")
    comentarios=fields.Char("Comentario")
    imagen=fields.Image("Imagen")


    seccion=fields.Boolean("Seccion")
    bitacora_id=fields.Many2one("bitacora.servicio","Bitacora a la que pertenece")



class PlantillaBitacoraServicio(models.Model):
    _name="bitacora.servicio.plantilla"
    _description="Plantilla de bitacora de servicio"
    #Esto se muestra en el formulario de bitacora
    name=fields.Char("Nombre de plantilla")
    equipos_incluidos=fields.One2many("product.template","tipo_bitacora",string="Modelos cubiertos")
    lineas=fields.One2many("bitacora.servicio.plantilla.linea","plantilla_id",string="Lineas de plantilla")


class PlantillaBitacoraServicioLinea(models.Model):
    _name="bitacora.servicio.plantilla.linea"
    _description="Plantilla de bitacora de servicio"

    
    plantilla_id=fields.Many2one("bitacora.servicio.plantilla","Plantilla de bitacora a la que pertenece")
    pregunta=fields.Char("Pregunta")    
    seccion=fields.Boolean("Seccion")

class lineaDispositivo(models.Model):
    _name="linea.dispositivo"
    # inspeccion campos
    linea_dispositivo = fields.Char()
    otro_dispositivo = fields.Text()



    
