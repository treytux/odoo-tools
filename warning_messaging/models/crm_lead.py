# -*- coding: utf-8 -*-
################################################################################
#
#    Trey, Kilobytes de Soluciones
#    Copyright (C) 2014-Today Trey, Kilobytes de Soluciones (http://www.trey.es)
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
################################################################################
from openerp import models, fields, api, _
import logging
import time
from datetime import datetime
import datetime as dt
from openerp.osv.orm import browse_null


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Indica si se ha ejecutado algun aviso sobre este registro
    # active_message_lead_rel: tiene que indicar para una oportunidad (p.ej), el
    # id del aviso que se ha ejecutado (porque puede haber varios avisos que
    # afecten a un unico registro)
    active_mess_ids = fields.Many2many(
        comodel_name='warning.messaging',
        relation='active_message_lead_rel',
        column1='lead_id',
        column2='warning_id',
        translate=True)

    #     NEW API----error:
    # @api.multi
    # def send_warning_message(self):
    #     context = self._context

    #     crm_lead = self.env['crm.lead'].browse(self.id)  # id de la oportunidad
    #     crm_lead = crm_lead.with_context(mail_post_autofollow=False)  # mail_post_autofollow: sera para que lo siga yo

    #     # Enviar notificacion al partner_id del usuario 'usuario'
    #     partner_ids = [11]
    #     # crm_lead.message_post(body=_("probandooooo"), partner_ids=[11])
    #     crm_lead.message_post(body=_("probandooooo2"), partner_ids=partner_ids)
    #     ###

    #     # if context.get('default_model') == 'crm.lead' and \
    #     #         context.get('default_res_id') and context.get('mark_invoice_as_sent'):
    #     #     crm_lead = self.env['crm.lead'].browse(context['default_res_id'])
    #     #     crm_lead = crm_lead.with_context(mail_post_autofollow=True)
    #     #     crm_lead.write({'sent': True})
    #     #     crm_lead.message_post(body=_("probandooooo"))
    #     # return super(mail_compose_message, self).send_mail()

    #     return True

    # OLD API
    def send_warning_message(self, cr, uid, cron_id, lead_id, context):
        if lead_id and cron_id:
            crm_lead = self.pool.get('crm.lead').browse(cr, uid, lead_id, context)
            cron = self.pool.get('ir.cron').browse(cr, uid, cron_id, context=context)

            # Obtener los pedidos que no hayan sido ya avisados con anterioridad, es
            # decir, todos los pedidos excepto los que esten en la tabla
            # active_message_sale_rel relacionados con este aviso
            sql = '''
                SELECT warning_id
                FROM active_message_lead_rel
                WHERE lead_id = %s
            ''' % (lead_id)
            cr.execute(sql)
            res = cr.fetchall()

            # Si la consulta no devuelve nada, es que este pedido aun no ha
            # generado aviso => HACER QUE LO GENERE
            if res == []:
                # Indica si se ha generado accion para el registro
                active_mess = False

                # Buscar el aviso asociado a esta accion planificada
                warning_ids = self.pool.get('warning.messaging').search(cr, uid, [('cron_id', '=', cron_id)])

                if warning_ids:
                    warning = self.pool.get('warning.messaging').browse(cr, uid, warning_ids[0], context=context)

                    # Leer las condiciones
                    for condition in warning.condition_ids:
                        # Si tiene periodo asignado
                        if not isinstance(condition.period_id, browse_null):
                            # Pasar el periodo a dias y convertirlo a timedelta
                            total_days = 0
                            if condition.period_id.days:
                                total_days += condition.period_id.days
                            if condition.period_id.months:
                                total_days += condition.period_id.months*30
                            if condition.period_id.years:
                                total_days += condition.period_id.years*365
                            total_days = dt.timedelta(days=total_days)

                            time_format = "%Y-%m-%d %H:%M:%S"

                            # Comprobar si se cumple la condicion de tiempo
                            if (datetime.now() - datetime.fromtimestamp(time.mktime(time.strptime(crm_lead.write_date, time_format)))) >= total_days:

                                # Aplicar las acciones del aviso (puede haber mas de una)
                                for action in warning.action_ids:
                                    # Si la accion es enviar mensaje de alerta
                                    if action.ttype == 'send_mess':
                                        # mail_post_autofollow: para que lo siga el usuario que llama a la
                                        # accion (desactivado porque lo lanzara el sistema)
                                        crm_lead = crm_lead.with_context(mail_post_autofollow=False)

                                        # Enviar notificacion al partner_id del usuario asignado
                                        # como comercial
                                        partner_ids = [crm_lead.user_id and crm_lead.user_id.partner_id and
                                                       crm_lead.user_id.partner_id.id] or []
                                        crm_lead.message_post(body=warning.body, partner_ids=partner_ids)

                                        # logging.getLogger('warning_mess').info('ENVIADO MENSAJE con texto \'%s\' a usuario %s (%s).'
                                        #                                        % (warning.body, partner_ids,
                                        #                                        crm_lead.user_id.partner_id.name))
                                        active_mess = True

                                    # Si la accion es programar llamada
                                    elif action.ttype == 'create_call':
                                        data = {
                                            'name': '[AVISO] Llamada generada desde oportunidad \'%s\'' % (crm_lead.name),
                                            'partner_id': crm_lead.partner_id and crm_lead.partner_id.id or None,
                                            'opportunity_id': crm_lead.id,
                                            'user_id': crm_lead.user_id and crm_lead.user_id.id or None,
                                            # 'description': ,
                                        }
                                        phonecall_id = self.pool.get('crm.phonecall').create(cr, uid, data)
                                        phonecall = self.pool.get('crm.phonecall').browse(cr, uid, phonecall_id, context=context)
                                        # logging.getLogger('warning_mess').info('Llamada programada: \'%s\' (id=%s) a usuario %s.'
                                        #                                        % (phonecall.name, phonecall_id, phonecall.user_id.name))

                                        # Registrar nota interna de creacion automatica de llamada desde oportunidad
                                        crm_lead.message_post(body='[AVISO] Se ha programado una llamada.')
                                        active_mess = True

                                    # Si la accion es programar reunion
                                    elif action.ttype == 'create_meeting':
                                        data = {
                                            'name': '[AVISO] Reunion generada desde oportunidad \'%s\'' % (crm_lead.name),
                                            # @TODO Para cuando hay que planificar la reunion?
                                            # Por ahora, al dia siguiente y duracion=1hora. Luego, poner configurable en la accion
                                            'start': (datetime.now() + dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                            'stop': (datetime.now() + dt.timedelta(days=1, hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                            'opportunity_id': crm_lead.id,
                                            'user_id': crm_lead.user_id and crm_lead.user_id.id or None,
                                            # 'description': , # Reunion con el cliente...
                                        }
                                        calendar_event_id = self.pool.get('calendar.event').create(cr, uid, data)
                                        calendar_event = self.pool.get('calendar.event').browse(cr, uid, calendar_event_id, context=context)
                                        # logging.getLogger('warning_mess').info('Reunion programada: \'%s\' (id=%s) a usuario %s.'
                                        #                                        % (calendar_event.name, calendar_event_id, calendar_event.user_id.name))
                                        active_mess = True

                                        # Registrar nota interna de creacion automatica de reunion desde oportunidad (ya se anade de forma automatica)

                                    # # Si la accion es crear oportunidad
                                    # elif action.ttype == 'create_opportunity':
                                    #     data = {
                                    #         'name': '[AVISO] Reunion generada desde oportunidad \'%s\'' % (crm_lead.name),
                                    #         # @TODO Para cuando hay que planificar la reunion?
                                    #         # Por ahora, al dia siguiente y duracion=1hora. Luego, poner configurable en la accion
                                    #         # 'start': datetime.now() + dt.timedelta(days=1),
                                    #         # 'stop': datetime.now() + dt.timedelta(days=1, hours=1),
                                    #         'start': (datetime.now() + dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                    #         'stop': (datetime.now() + dt.timedelta(days=1, hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                    #         'opportunity_id': crm_lead.id,
                                    #         'user_id': crm_lead.user_id and crm_lead.user_id.id or None,
                                    #         # 'description': , # Reunion con el cliente...
                                    #     }
                                    #     calendar_event_id = self.pool.get('calendar.event').create(cr, uid, data)
                                    #     calendar_event = self.pool.get('calendar.event').browse(cr, uid, calendar_event_id, context=context)
                                    #     logging.getLogger('warning_mess').info('Reunion programada: \'%s\' (id=%s) a usuario %s.'
                                    #                                            % (calendar_event.name, calendar_event_id, calendar_event.user_id.name))

                                    #     ## NO, ya se anade
                                    #     # @TODO Registrar nota interna de creacion automatica de reunion desde oportunidad

                                    # En otro caso
                                    else:
                                        logging.getLogger('warning_mess').error('Accion \'%s\' no contemplada.' % (action.name))

                        # # Si tiene cantidad asignada
                        # elif condition.amount != 0:

                        else:
                            logging.getLogger('warning_mess').warn('El aviso \'%s\' (id=%s) no tiene asignado periodo ni cantidad.' % (warning.name, warning.id))
                else:
                    logging.getLogger('warning_mess').warn('No se ha encontrado ningun aviso asociado a la accion planificada %s (id=%s).' % (cron.name, cron_id))

                if active_mess is True:
                    # Insertar un registro en la tabla active_message_sale_rel para indicar que ya se ha creado la accion
                    data = {
                        'active_mess_ids': [(4, warning.id)],
                    }
                    self.pool.get('crm.lead').write(cr, uid, lead_id, data)

            # @TODO Solo para debug, luego se puede quitar
            # ###
            # else:
            #     logging.getLogger('warning_mess').info('La oportunidad %s ya ha generado acciones para el cron %s => NO HACER NADA' % (lead_id, cron_id))
            # ###

        return True

#     NEW API----error: TypeError: old_api() takes at least 4 arguments (3 given)
#     @api.multi
#     def _check_lead_period(self, ids=False, context=None):
#         print '/////_check_lead_period//////'
#         return True
    # OLD API
    # En los argumentos (context) viene el id del aviso y el del cron
    # [<warning_messs_id>, {'active_id': <cron_id>}]
    def _check_lead_period(self, cr, uid, ids, context):
        # Obtener todas las oportunidades
        # @TODO filtrar por estado para dejar solo las activas
        # Se filtraran por periodo en la funcion 'send_warning_message', ya que,
        # desde aqui no tenemos acceso al aviso para obtener el periodo y hacer
        # la condicion
        lead_ids = self.pool.get('crm.lead').search(cr, uid, [('type', '=', 'opportunity')])

        for lead_id in lead_ids:
            lead = self.pool.get('crm.lead').browse(cr, uid, lead_id)
            # logging.getLogger('warning_mess').info('Iterando oportunidad \'%s\'\
            #     (id=%s)' % (lead.name, lead_id))

            # Comprobar que context sea un diccionario (por si viniera otra cosa)
            if isinstance(context, dict):
                cron_id = context.get('active_id', None)
                # Enviar mensaje
                self.pool.get('crm.lead').send_warning_message(cr, uid, cron_id, lead_id,
                                                               context)
            else:
                logging.getLogger('warning_mess').error('Error en los argumentos\
                    pasados en la accion automatica. Se espera: [<warning_messaging_id>,\
                    {\'active_id\': <cron_id>}]')
        return True
