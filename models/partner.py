from odoo import api, models, fields
class Partner(models.Model):
    _inherit='res.partner'

    equipos=fields.One2many("equipo.mantenimiento","cliente",string="Equipos")
    contratos=fields.One2many("equipo.entrust.contrato","cliente",string="Contratos")
    fichas = fields.One2many("entrega.producto", "cliente", string="Fichas")