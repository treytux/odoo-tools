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
from openerp import models, api, fields, _, exceptions
import logging

_log = logging.getLogger(__name__)


class WarningMessaging(models.Model):
    _inherit = 'warning.messaging'

    email_tmpl_id = fields.Many2one(
        comodel_name='email.template',
        string='Email Template')
    email_type = fields.Selection(
        selection=[
            ('with_template', 'With template'),
            ('without_template', 'Without template'),
        ],
        string='Email type',
        default='with_template',
        required=True)
    email_subject = fields.Char(string='Email subject')
    email_body_html = fields.Char(string='Email body html')
    email_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='warning_mess_attach_rel',
        column1='warning_mess_id',
        column2='attachment_id')

    @api.multi
    def send_mail_without_template(self, email_to):
        ''' Send a mail without template to email address indicated in
        'email_to'.'''
        cr, uid, context = self.env.args

        # 1 - Crear objeto mail.message (mail_message_id)
        email_from = self.env['ir.mail_server'].search(
            [('active', '=', True)])
        if not email_from:
            raise exceptions.Warning(_(
                'Not exist any mail in active state, the email can not sent.'))

        data_msg = {
            'subject': self.email_subject or '',
            'type': 'email',
            'email_from': email_from.smtp_user,
            'attachment_ids': [(6, 0, [attach.id for attach in
                                self.email_attachment_ids])]
        }
        mail_message = self.env['mail.message'].create(data_msg)

        # 2 - Crear objeto mail.mail (mail_id) y asignarle el mail_message_id
        mail_mail = self.env['mail.mail']
        data_mail = {
            'mail_message_id': mail_message.id,
            'body_html': self.email_body_html or '',
            'email_to': email_to
        }
        mail = mail_mail.create(data_mail)

        # 3 - Llamar a funcion send con ids = mail.id
        # Hay que llamar a send con la api antigua
        self.pool.get('mail.mail').send(cr, uid, [mail.id])

        return True

    @api.one
    def do_send_email(self, objs):
        try:
            for obj in objs:
                if hasattr(obj, 'message_post'):
                    # Si el aviso no tiene plantilla asignada
                    if not self.email_tmpl_id.exists():
                        email_to = obj.partner_id and obj.partner_id.email\
                            or None
                        self.send_mail_without_template(email_to)

                        # Notificar en el registro que se ha enviado el
                        # correo
                        partner_ids = [obj.user_id and obj.user_id.partner_id
                                       and obj.user_id.partner_id.id] or []
                        body = _('Mail sent to partner from warning \'%s\'.'
                                 % self.name)
                        obj.with_context(
                            mail_post_autofollow=False).message_post(
                            body=body, partner_ids=partner_ids)

                    # Si el aviso tiene plantilla asignada
                    else:
                        # Enviar directamente con la plantilla seleccionada
                        # por el usuario en el aviso

                        # Para que funcione el envio de correos, la llamada
                        # debe ser con la antigua api
                        cr, uid, context = self.env.args
                        self.pool.get('email.template').send_mail(
                            cr, uid, self.email_tmpl_id.id, obj.id,
                            force_send=True, raise_exception=True,
                            context=context)

                        # Notificar en el registro que se ha enviado el
                        # correo
                        partner_ids = [obj.user_id and obj.user_id.partner_id
                                       and obj.user_id.partner_id.id] or []
                        body = _('Mail sent to partner from warning \'%s\'.'
                                 % self.name)
                        obj.with_context(
                            mail_post_autofollow=False).message_post(
                            body=body, partner_ids=partner_ids)

                        return True

                else:
                    _log.error('%s model don\'t inherit mail.message, '
                               'not message sended.' % self.model_id.model)
            return True
        except Exception as e:
            _log.error('I can\'t to send the message for warning "%s": %s'
                       % (self.name, e))
            return False


class WarningAction(models.Model):
    _inherit = 'warning.action'

    # Anadir valores a campo selection
    def __init__(self, pool, cr):
        super(WarningAction, self).__init__(pool, cr)
        option = ('send_email', 'Send email')
        type_selection = self._columns['ttype'].selection

        if option not in type_selection:
            type_selection.append(option)
