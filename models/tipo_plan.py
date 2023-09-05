from odoo import api, models, fields

class TipoPlan(models.model):
    _name = "tipo.plan"
    _description = "Modelo para almacenar los tipos de planes creados en SAP"

    name = fields.Char("Tipo de plan")
    amount = fields.Integer("Cantidad de visitas del plan")

class RegistroVisitas(models.model):
    _name = "registro.visitas"
    _description = "Modelo para registrar las visitas completadas por contrato"

    contrato_id = fields.Many2One("equipo.entrust.contrato")
    ticket_id = fields.Char("Ticket de la visita")