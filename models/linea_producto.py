from odoo import api, models, fields
from odoo.exceptions import ValidationError

class LineaProducto(models.Model):
    _name="linea.producto"
    _description="Lineas de producto"

    name = fields.Char(string = "Nombre de la línea")
    descripcion = fields.Text(string = "Descripción de la línea")