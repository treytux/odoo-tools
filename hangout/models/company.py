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
from openerp import models, fields, api, _
import logging
_log = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    hangout_email = fields.Char(string='Email')
    hangout_password = fields.Char(string='Password', password=True)
    hangout_notify_accounts = fields.Char(string='Notify accounts')

    @api.one
    def action_test_hangout(self):
        self.hangoutSendMessage(
            _('This messages is a test from Odoo %s') % self.env.cr.dbname)

    def hangoutSendMessage(self, message, accounts=None):
        company = self.env.user.company_id
        if accounts is None:
            accounts = company.hangout_notify_accounts

        try:
            import xmpp
            jid = xmpp.protocol.JID(company.hangout_email)
            cl = xmpp.Client(jid.getDomain(), debug=[])
            cl.connect()
            cl.auth(jid.getNode(), company.hangout_password)
            cl.send(xmpp.protocol.Message(
                company.hangout_notify_accounts,
                message, typ='chat'))
        except Exception as e:
            raise e
        else:
            _log.info('Message "%s" sended to %s' % (
                message[:12], company.hangout_notify_accounts))
