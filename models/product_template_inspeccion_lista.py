from odoo import api, models, fields
from odoo.exceptions import ValidationError

class ListaProductosInspeccion(models.Model):
    _name="product.template.inspeccion.lista"
    _description="Productos contemplados en la inspección"

    producto = fields.Many2one("product.product", string = "Producto")
    cantidad = fields.Float("Cantidad")
    reporte_inspeccion_id = fields.Many2one("reporte.inspeccion")
    