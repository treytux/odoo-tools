# -*- coding: utf-8 -*-
###############################################################################
#
#    Trey, Kilobytes de Soluciones
#    Copyright (C) 2014-Today Trey, Kilobytes de Soluciones <www.trey.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import models, api
import datetime
import logging

_log = logging.getLogger(__name__)


class WarningMessaging(models.Model):
    _inherit = 'warning.messaging'

    @api.one
    def do_send_msg(self, objs, action):
        if self.model_id.name == 'crm.lead':
            for crm_lead in objs:
                partner_ids = [crm_lead.user_id and crm_lead.user_id.partner_id
                               and crm_lead.user_id.partner_id.id] or []

                crm_lead.with_context(mail_post_autofollow=False).message_post(
                    body=self.body, partner_ids=partner_ids)
            return True
        else:
            return super(WarningMessaging, self).do_send_msg(objs, action)

    @api.one
    def do_create_call(self, objs, action):
        if self.model_id.name == 'sale.order':
            for sale_order in objs:
                self.env['crm.phonecall'].create({
                    'name': '[AVISO] Llamada generada desde presupuesto \'%s\''
                    % (sale_order.name),
                    'partner_id': sale_order.partner_id and
                    sale_order.partner_id.id or None,
                    'user_id': sale_order.user_id and sale_order.user_id.id
                    or None,
                    # 'description': ,
                })
        return True

    @api.one
    def do_create_meeting(self, objs, action):
        if self.model_id.name == 'sale.order':
            for sale_order in objs:
                # @TODO Para cuando hay que planificar la reunion?
                # Por ahora, al dia siguiente y duracion=1hora. Luego,
                # poner configurable en la accion
                format_date = '%Y-%m-%d %H:%M:%S'
                start = (
                    datetime.datetime.now() +
                    datetime.timedelta(days=1)).strftime(format_date)
                stop = (
                    datetime.datetime.now() +
                    datetime.timedelta(days=1, hours=1)).strftime(format_date)

                self.env['calendar.event'].create({
                    'name': '[AVISO] Reunion generada desde presupuesto \'%s\''
                    % (sale_order.name),
                    'start': start,
                    'stop': stop,
                    'user_id': sale_order.user_id and sale_order.user_id.id or
                    None,
                    # 'description': , # Reunion con el cliente...
                })

        return True

    @api.one
    def do_create_opportunity(self, objs, action):
        if self.model_id.name == 'sale.order':
            for sale_order in objs:
                self.env['crm.lead'].create({
                    'name': '[AVISO] Oportunidad generada desde presupuesto '
                    '\'%s\'' % (sale_order.name),
                    'partner_id': sale_order.partner_id and
                    sale_order.partner_id.id or None,
                    'user_id': sale_order.user_id and sale_order.user_id.id or
                    None,
                    'type': 'opportunity',
                    # 'description': ,
                })
        return True


class WarningAction(models.Model):
    _inherit = 'warning.action'

    @api.model
    def _setup_fields(self):
        '''Anadir valores a campo selection.'''
        res = super(WarningAction, self)._setup_fields()

        options = [
            ('create_call', 'Create call phone'),
            ('create_meeting', 'Create meeting'),
            ('create_opportunity', 'Create opportunity'),
        ]

        for option in options:
            if 'ttype' in self._fields and \
               option not in self._fields['ttype'].selection:
                    self._fields['ttype'].selection.append(option)
        return res