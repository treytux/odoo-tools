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

# @ TODO Poner texto en inglessss
{
    'name': 'warning_messaging',
    'category': 'Warning',
    'summary': 'Warning messaging',
    'version': '0.1',
    'description': """
Modulo para gestionar avisos de mensajeria automaticos.
    """,
    'author': 'Trey Kilobytes de Soluciones (www.trey.es)',
    'depends': [
        'base',
        'cron_ir_execute_now',
        'crm',
        'sale',
    ],
    'data': [

        'views/data.xml',
        'views/warning_view.xml',
        'views/crm_lead_view.xml',
        'views/menu.xml',
        # @TODO
        # 'security/ir.model.access.csv',
    ],
    'demo': [
        # 'data/demo.xml',
    ],
    'test': [
        'test/sale_order.yml',
        'test/warning_messaging.yml',
    ],
    'installable': True,
}
