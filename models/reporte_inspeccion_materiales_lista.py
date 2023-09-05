from odoo import api, models, fields
from odoo.exceptions import ValidationError

class ReporteInspeccionMaterialesLista(models.Model):
    _name="reporte.inspeccion.materiales.lista"
    _description="Lista de materiales"

    descripcion = fields.Char(string = "Descripción")
    cantidad = fields.Float(string = "Cantidad")
    unidad_de_medida = fields.Char(string = "Unidad de medida")
    observacion = fields.Text(string = "Observación adicional")
    reporte_inspeccion_id = fields.Many2one("reporte.inspeccion")