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
from openerp import api, models, fields
import logging

_log = logging.getLogger(__name__)


# @ TODO Anadir horas, min y seg

class Period(models.Model):
    _name = 'period'
    _description = 'Period'

    name = fields.Char(string='Name')
    days = fields.Integer(
        string='Days',
        translate=True)
    months = fields.Integer(
        string='Months',
        translate=True)
    years = fields.Integer(
        string='Years',
        translate=True)
    hours = fields.Integer(
        string='Hours',
        translate=True)
    minutes = fields.Integer(
        string='Minutes',
        translate=True)
    seconds = fields.Integer(
        string='Seconds',
        translate=True)


### Funcionalidades referentes al periodo para otras clases
# import datetime
# class MoDel(models.Model):
#     _name = 'mo.del'
#     _description = 'Model description'

#     @api.multi
#     def get_days_between_month(self, date_str):
#         # Obtener los dias necesarios para que cuadre el dia
#         date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
#         carry, new_month = divmod(date.month-1+1, 12)
#         new_month += 1
#         date_init = date
#         try:
#             date = date.replace(year=date.year+carry, month=new_month)
#         except:
#             last_day = calendar.monthrange(date.year, new_month)[1]
#             date = date.replace(
#                 year=date.year+carry, month=new_month, day=last_day)
#         return (date-date_init).days

#     @api.multi
#     def get_period_days(self, date_str, period):
#         # Pasar el periodo a dias
#         total_days = 0
#         if period.days:
#             total_days += period.days
#         if period.months:
#             total_days +=\
#                 period.months * self.get_days_between_month(date_str)
#         if period.years:
#             total_days += period.years*365
#             # @ TODO Hacerlo mismo o parecido con years (365 o 366)
#             # total_days +=\
#             #   self.period_id.months*self.get_days_between_month(date_str)
#         return total_days

