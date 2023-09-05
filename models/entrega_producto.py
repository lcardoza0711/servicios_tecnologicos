from datetime import datetime
from odoo import api, models, fields

class EntregaProducto(models.Model):
    _name = "entrega.producto"
    _description = "Ficha Técnica de recepción de equipos"

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('ficha.recepcion') or "Nuevo"
        re = super(EntregaProducto, self).create(vals)
        return re
    
    #Datos generales
    ticket=fields.Many2one("helpdesk.ticket","Ticket")
    cliente = fields.Many2one("res.partner", string="Empresa/Cliente:", related="ticket.partner_id")

    contacto = fields.Char("Contacto:")
    name = fields.Char("Orden de recepción:", readonly=True,required=True, copy=False,default="Nuevo")
    telefono_contacto = fields.Char("Teléfono del contacto:")
    entrega = fields.Char("Entrega:")
    recibe = fields.Char("Retira:")
    area= fields.Char("Área solicitante:")

    acesor = fields.Many2one("hr.employee",string="Asesor a cargo:")

    fecha_entrega = fields.Date("Fecha de recepción:", default=datetime.today())
    fecha = fields.Date("Fecha:", default=datetime.today())
    fecha_devolucion = fields.Date("Fecha estimada de devolución:", default=datetime.today())
    
    #Detalle del prodcuto    
    equipos = fields.Many2one("equipo.entrust",string="Serie del equipo",related ="ticket.equipo_id")
    marca = fields.Many2one("product.brand",string="Marca",related="equipos.marca")
    modelo = fields.Many2one("product.template",string="Modelo")
    modulos = fields.One2many("equipo.entrust.modulo", "fichas" ,related="equipos.modulos")
    tecnico = fields.Many2one("hr.employee", string="Técnico a cargo", related="equipos.tecnico")    

    parte = fields.Char(related="equipos.parte",string="Número de parte") 
   
    #Accesorios
    cant_transformador = fields.Integer(string='Cantidad:')
    cant_cables_poder = fields.Integer(string='Cantidad:')
    cant_tarjetas_pvc = fields.Integer(string='Cantidad:')
    cant_porta_cinta = fields.Integer(string='Cantidad:')
    cant_porta_laminador = fields.Integer(string='Cantidad')
    cant_cinta_laminador = fields.Integer(string='Catidad')

    color_porta_cinta = fields.Selection(string='Color', selection=[('azul', 'Azul'),('negro','Negro'),('gris','Gris'),('azul_negro','Negro con azul')])
    
    tipo_cinta = fields.Selection(string= 'Tipo:', selection=[('ymck', 'YMCK'),('ymckt','YMCKT'),('ymcktkt','YMCKT-KT'),('ymcktk','YMCKT-K')])

    tipo_de_equipo = fields.Selection(string="Tipo de equipo", selection=[("entrust", "Entrust"), ("seguridad", "Seguridad electrónica")], default="entrust")

    tipo_de_ficha = fields.Selection(string="Tipo de documento", selection=[("prestamo", "Prestamo"), ("recepcion", "Recepción")], default="recepcion")


    tipo_de_estado = fields.Selection(string="Estado", selection=[("entrada", "Entrada"), ("salida", "Salida")], default="entrada")
    tipo_de_cinta_laminador = fields.Selection(string="Tipo de cinta", selection=[("holografico", "Holográfico"),("dgc", "Dura Gard Clear"), ("trc", "TopCoat Ribbon Clear"), ("trh", "TopCoat Robbon Holográfico")])
    equipo_laminacion = fields.Selection(selection=[("cd800clm","CD800/CLM"), ("cp80", "CP80"), ("sigma", "Sigma"), ("sr300", "SR300")])
    tipo_tarjeta = fields.Selection(string="Tipo de tarjeta", selection=[("estandar", "PVC Estandar"), ("milimetrica", "Milimetrica"), ("acceso", "Tarjeta de acceso"), ("pvcbm", "PVC Banda Magnética"), ("pvccolores", "PVC Colores"), ("pvcadecivas", "PVC Adecivas")])

    descripcion = fields.Text("Observaciones")

    ok_transformador = fields.Boolean("Transformador")
    ok_cables_poder = fields.Boolean("Cables de poder")
    ok_tarjetas_pv = fields.Boolean("Tarjetas")
    ok_porta_cinta = fields.Boolean("Porta Cinta") 
    ok_cinta = fields.Boolean("Cinta")
    ok_porta_laminador = fields.Boolean("Porta Laminador")
    ok_cinta_laminador = fields.Boolean("Cinta Laminador")
    ok_equipo_laminacion = fields.Boolean("Equipo de lamninación")

    recepcion_img = fields.Image("Imagen de recepcion del equipo")
    prestamo_img = fields.Image("Imagen del equipo a prestar")

    acceso = fields.Boolean(string='Acceso')
    asistencia = fields.Boolean(string='Asistencia')
    bloqueado = fields.Boolean(string='Bloqueado')
    cd_desbloqueo = fields.Boolean(string='CD desbloqueo')
    contrasena = fields.Boolean(string='Contraseña')
    soporte_equipo = fields.Boolean(string='Soporte de equipo')
    empaque_bolsas = fields.Boolean(string='Empaque Bolsas')
    transformador = fields.Boolean(string='Transformador')
    cantidad = fields.Boolean(string='Cantidad')
    caja = fields.Boolean(string='Caja')
    manuales = fields.Boolean(string='Manuales')