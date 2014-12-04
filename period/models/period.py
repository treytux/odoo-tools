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
from dateutil.relativedelta import relativedelta


class Period(models.Model):
    _name = 'period'
    _description = 'Period'

    name = fields.Char(string='Name')
    seconds = fields.Integer(
        string='Seconds',
        translate=True)
    minutes = fields.Integer(
        string='Minutes',
        translate=True)
    hours = fields.Integer(
        string='Hours',
        translate=True)
    days = fields.Integer(
        string='Days',
        translate=True)
    weeks = fields.Integer(
        string='Weeks',
        translate=True)
    months = fields.Integer(
        string='Months',
        translate=True)
    years = fields.Integer(
        string='Years',
        translate=True)

    @api.multi
    def next(self, date):
        if isinstance(date, str):
            date = fields.Datetime.from_string(date)

        return date + relativedelta(
            years=self.years,
            months=self.months,
            days=self.days,
            weeks=self.weeks,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds)
