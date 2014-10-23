# -*- coding: utf-8 -*-
##########################################################################
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
##########################################################################

from openerp import api, models, fields
import logging
from openerp.osv.orm import browse_null


class warning_condition(models.Model):
    _name = 'warning.condition'
    _description = 'Warning condition'

    name = fields.Char(
        string='Name',
        translate=True)
    period_id = fields.Many2one(
        comodel_name='warning.period',
        string='Period',
        translate=True)
    amount = fields.Float(
        string='Amount',
        translate=True)
    state = fields.Selection(
        selection=[
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancel'),
        ],
        string='State',
        translate=True)


class warning_action(models.Model):
    _name = 'warning.action'
    _description = 'Warning action'

    name = fields.Char(
        string='Name',
        translate=True)
    ttype = fields.Selection(
        selection=[
            ('send_mess', 'Send alert message'),
            ('create_call', 'Create call phone'),
            ('create_meeting', 'Create meeting'),
            ('create_opportunity', 'Create opportunity'),
        ],
        string='Type',
        translate=True)


class warning_messaging(models.Model):
    _name = 'warning.messaging'
    _description = 'Warning messaging'

    name = fields.Char(
        string='Name',
        translate=True)
    #@TODO Por ahora solo hay funcionalidad para crm.lead y sale.order, asi que mostrar solo esto
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        translate=True)
    # @TODO HAcer que se rellene automaticamente al seleccionar el modelo
    function_name = fields.Char(
        string='Function name',
        required=True,
        translate=True,
        help="Function executed by scheduled action associated.")
    cron_id = fields.Many2one(
        comodel_name='ir.cron',
        string='Cron Job',
        translate=True,
        readonly=True,
        help="Scheduled Action associated.")
    body = fields.Text(
        string='Body',
        translate=True,
        required=True,
        help="Text to include in the message sent.")
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        string='State',
        default='inactive',
        translate=True)
    condition_ids = fields.Many2many(
        comodel_name='warning.condition',
        relation='warning_condition_messsaging_rel',
        column1='condition_id',
        column2='messaging_id',
        translate=True,
        help="Conditions to be met the object registers.")
    action_ids = fields.Many2many(
        comodel_name='warning.action',
        relation='warning_action_messsaging_rel',
        column1='action_id',
        column2='messaging_id',
        translate=True,
        help="Actions to be executed if the condition are met.")

    # Crea una nueva accion planificada usando los valores del objeto aviso y lo
    # relaciona con el. De esta manera, el usuario no se tiene que preocupar de
    # tocar las acciones planificadas directamente y desde aqui es mas facil
    # para el
    # @api.multi
    # def to_active(self):
    # warning_mess = self.pool.get('warning.messaging').browse(cr, uid, id, context=context)
    #     warning_mess = self.env['warning.messaging'].browse(self.id)

    #     vals = {
    #         'function': '_check_lead_period',
    #         'interval_type': warning_mess.interval_type,
    #         'user_id': warning_mess.create_uid.id,
    #         'name': warning_mess.name,
    # 'args': [[warning_mess['id']]],
    #         'numbercall': 0,
    #         'nextcall': warning_mess.create_date,
    #         'priority': 6,
    #         'model': 'crm.lead',
    #         'interval_number': warning_mess.interval_number,
    # @TODO para las pruebas, desactivar
    #         'active': False
    #     }
    #     cron = self.env['ir.cron'].create(vals)

    # self.write({'cron_id': cron.id})
    # prueba para pasarle el id del aviso y tb el id del cron
    #     vals2 = {
    #         'cron_id': cron.id,
    # 'args': [[warning_mess['id']], [cron.id]],
    #         'args': [warning_mess['id'], cron.id],
    #     }
    #     print 'vals2', vals2
    #     print 'vals2[args]', vals2['args']

    # asignar id del cron creado
    # self.env['ir.cron'].ids = cron.id

    #     self.env['ir.cron'].write(vals2)

    #     logging.getLogger('warning_mess').info('Creando cron %s para oport %s.'
    #                                            % (cron.id, self.id))

    #     return True

    # OLD API
    # Activar el aviso:
    # Comprueba si ya tiene una accion planificada asociada.
    # Si la tiene, la activa
    # Si no la tiene, crea una nueva y se la asigna al aviso
    def to_active(self, cr, uid, ids, context={}):
        if ids:
            warning_mess = self.pool.get('warning.messaging').browse(
                cr, uid, ids[0], context=context)

            # Si no tiene una accion planificada asociada, la crea
            if isinstance(warning_mess.cron_id, browse_null):
                # Crear la accion planificada
                data = {
                    'name': warning_mess.name,
                    'model': warning_mess.model_id.model,
                    'function': warning_mess.function_name,
                    'user_id': warning_mess.create_uid.id,
                    'numbercall': -1,
                    'nextcall': warning_mess.create_date,
                    'priority': 6,
                    # Por defecto, ejecutar el cron una vez a la hora
                    'interval_number': 1,
                    'interval_type': 'hours',
                    'active': True
                }
                cron_id = self.pool.get('ir.cron').create(cr, uid, data)

                # Asignar los argumentos al cron:
                # [<aviso_id>, {'active_id': <cron_id>}]
                data2 = {
                    'args': [warning_mess['id'], {'active_id': cron_id}],
                }
                # @TODO REPASAR: OJO: Si le paso cron_id, peta porque espera una lista, pero por que????
                self.pool.get('ir.cron').write(cr, uid, [cron_id], data2)

                # Asignar el cron creado al aviso
                self.pool.get('warning.messaging').write(
                    cr, uid, ids[0], {'cron_id': cron_id})

            # Si ya tiene una asignada, la activa
            else:
                self.pool.get('ir.cron').write(
                    cr, uid, [warning_mess.cron_id.id], {'active': True})

            self.pool.get('warning.messaging').write(
                cr, uid, warning_mess.id, {'state': 'active'})
        return True

    # OLD API
    # Desactivar el aviso: desactiva el aviso y la accion planificada asociada
    def to_inactive(self, cr, uid, ids, context={}):
        if ids:
            warning_mess = self.pool.get('warning.messaging').browse(
                cr, uid, ids[0], context=context)

            self.pool.get('warning.messaging').write(
                cr, uid, ids[0], {'state': 'inactive'})

            self.pool.get('ir.cron').write(
                cr, uid, [warning_mess.cron_id.id], {'active': False})
        return True


class warning_period(models.Model):
    _name = 'warning.period'
    _description = 'Warning period'

    name = fields.Char(
        string='Name',
        translate=True)
    days = fields.Integer(
        string='Days',
        translate=True)
    months = fields.Integer(
        string='Months',
        translate=True,
        help="By default, the months consist of 30 days.")
    years = fields.Integer(
        string='Years',
        translate=True,
        help="By default, the years consist of 365 days.")
