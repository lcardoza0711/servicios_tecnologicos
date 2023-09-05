from odoo import api, fields, models, _


class CrmLeadConvert2Ticket_success(models.TransientModel):
    _name = 'crm2ticket.success.wizard'
    _description = 'El tictket fue creado'
    message = fields.Text(string="El ticket fue creado exitosamente", readonly=True, store=False)


class CrmLeadConvert2Ticket(models.TransientModel):
    _inherit='crm.lead.convert2ticket'
    lead_name= fields.Many2one("lead name","lead_id.name")
    stage_name= fields.Char("Nombre de etapa", readonly=True)
    responsable_id = fields.Many2one("hr.employee")
    tipo_entrega = fields.Selection(
        [('oficina', "Entrega desde oficina"), ("delivery", "Entrega delivery"), ("sin entrega", "Sin entrega")],
        string="Tipo de entrega")
    priority = fields.Selection(
        [('0', "Todos"), ("1", "Prioridad baja"), ("2", "Alta prioridad"),("3", "Urgente")],  string="Prioridad")
    description= fields.Html("Descripción")
    user_id = fields.Many2one('res.users', string="Responsable", store=True, readonly=False)


    def action_lead_to_helpdesk_ticket(self):
        self.ensure_one()
        # get the lead to transform
        lead = self.lead_id
        partner = self.partner_id
        if not partner and (lead.partner_name or lead.contact_name):
            lead._handle_partner_assignment(create_missing=True)
            partner = lead.partner_id

        # prepare new helpdesk.ticket values
        # Por solicitud piad-132, se agrega, en la creación del ticket, la oportunidad origen en el campo creado "Oportunidad"
        if self.tipo_entrega ==False:
            vals = {
                "name": lead.name,
                "description": lead.description,
                "oportunidad_id": lead.id,
                "team_id": self.team_id.id,
                "ticket_type_id": self.ticket_type_id.id,
                "partner_id": partner.id,
                "user_id": self.responsable_id.user_id.id,

            }
        else:
            vals = {
                "name": "Entrega "+self.tipo_entrega + " a " +partner.name,
                "description": lead.description,
                "team_id": self.team_id.id,
                "ticket_type_id": self.ticket_type_id.id,
                "partner_id": partner.id,
                "user_id": self.responsable_id.user_id.id,
                "priority": self.priority,
                "description": self.description
            }

        if lead.contact_name:
            vals["partner_name"] = lead.contact_name
        if lead.phone:  # lead phone is always sync with partner phone
            vals["partner_phone"] = lead.phone
        else:  # if partner is not on lead -> take partner phone first
            vals["partner_phone"] = partner.phone or lead.mobile or partner.mobile
        if lead.email_from:
            vals['email'] = lead.email_from

        # create and add a specific creation message
        ticket_sudo = self.env['helpdesk.ticket'].with_context(
            mail_create_nosubscribe=True, mail_create_nolog=True
        ).sudo().create(vals)
        ticket_sudo.message_post_with_view(
            'mail.message_origin_link', values={'self': ticket_sudo, 'origin': lead},
            subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
        )

        # move the mail thread
        lead.message_change_thread(ticket_sudo)
        # move attachments
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)])
        attachments.sudo().write({'res_model': 'helpdesk.ticket', 'res_id': ticket_sudo.id})
        # archive the lead

        # return to ticket (if can see) or lead (if cannot)
        try:
            self.env['helpdesk.ticket'].check_access_rights('read')
            self.env['helpdesk.ticket'].browse(ticket_sudo.ids).check_access_rule('read')

        except:
            message = 'Se creo satisfactoriamente el tickect para {}'.format(self.team_id.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                }

            }
            return {
                'name': _('Lead Converted'),
                'view_mode': 'form',
                'res_model': lead._name,
                'type': 'ir.actions.act_window',
                'res_id': lead.id
            }

        # return the action to go to the form view of the new Ticket
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')
        return {
            'name': _('Ticket created'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'res_id': ticket_sudo.id,
            'context': self.env.context
        }
        self.lead_id.action_unarchive()
        self.lead_id.active=True






class HelpdeskTicketConvert2Lead(models.TransientModel):
    _inherit = "helpdesk.ticket.to.lead"
    _description = "Convert Ticket to Lead"

    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicketConvert2Lead, self).default_get(fields)

        if not res.get('ticket_id') and self.env.context.get('active_id'):
            res['ticket_id'] = self.env.context['active_id']

        return res

    ticket_id = fields.Many2one('helpdesk.ticket', required=True, readonly=False)
    action = fields.Selection([
        ('create', 'Create a new customer'),
        ('exist', 'Link to an existing customer'),
        ('nothing', 'Do not link to a customer')
    ], string='Related Customer', compute='_compute_action', readonly=False, store=True)
    partner_id = fields.Many2one('res.partner', string="Customer", compute='_compute_partner_id', store=True, readonly=False)
    team_id = fields.Many2one('crm.team', string="Sales Team", compute='_compute_team_id', store=True, readonly=False)
    user_id = fields.Many2one('res.users', string="Salesperson", compute='_compute_user_id', store=True, readonly=False)
    responsable = fields.Many2one('hr.employee', string='Responsable de referencia')
    descripcion = fields.Html('Descripción')

    @api.depends('ticket_id')
    def _compute_action(self):
        for convert in self:
            if not convert.ticket_id:
                convert.action = 'nothing'
            else:
                partner = convert.ticket_id._find_matching_partner()
                if partner:
                    convert.action = 'exist'
                elif convert.ticket_id.partner_name:
                    convert.action = 'create'
                else:
                    convert.action = 'nothing'

    @api.depends('action', 'ticket_id')
    def _compute_partner_id(self):
        for convert in self:
            if convert.action == 'exist':
                convert.partner_id = convert.ticket_id._find_matching_partner()
            else:
                convert.partner_id = False

    @api.depends('ticket_id.user_id', 'user_id')
    def _compute_team_id(self):
        """ First, team id is chosen, then, user. If user from ticket have a
        team_id, use this user and his team."""
        for convert in self:
            user = convert.user_id or convert.ticket_id.user_id
            if not user or (convert.team_id and user in convert.team_id.member_ids | convert.team_id.user_id):
                continue
            team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=None)
            convert.team_id = team.id

    @api.depends('ticket_id', 'team_id')
    def _compute_user_id(self):
        for convert in self:
            user = convert.ticket_id.user_id
            convert.user_id = user if user and user in convert.team_id.member_ids else False

    def action_convert_to_lead(self):
        self.ensure_one()
        # create partner if needed
        if self.action == 'create':
            self.partner_id = self.ticket_id._find_matching_partner(force_create=True).id

        lead_sudo = self.env['crm.lead'].with_context(
            mail_create_nosubscribe=True,
            mail_create_nolog=True
        ).sudo().create({
            'referred': self.responsable.name,
            'name': self.ticket_id.name,
            'partner_id': self.partner_id.id,
            'team_id': self.team_id.id,
            'user_id': self.user_id.id,
            'description': self.descripcion,
            'email_cc': self.ticket_id.email_cc,
            'referred': self.responsable.id,

        })
        lead_sudo.message_post_with_view(
            'mail.message_origin_link', values={'self': lead_sudo, 'origin': self.ticket_id},
            subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
        )

        # move the mail thread and attachments
        self.ticket_id.message_change_thread(lead_sudo)
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', self.ticket_id.id)])
        attachments.sudo().write({'res_model': 'crm.lead', 'res_id': lead_sudo.id})
        #self.ticket_id.action_archive()


        # return to lead (if can see) or ticket (if cannot)
        try:
            self.env['crm.lead'].check_access_rights('read')
            self.env['crm.lead'].browse(lead_sudo.ids).check_access_rule('read')
        except:
            return {
                'name': _('Ticket Converted'),
                'view_mode': 'form',
                'res_model': self.ticket_id._name,
                'type': 'ir.actions.act_window',
                'res_id': self.ticket_id.id
            }

        # return the action to go to the form view of the new Ticket
        action = self.sudo().env.ref('crm.crm_lead_all_leads').read()[0]
        action.update({
            'res_id': lead_sudo.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
        })
        return action











