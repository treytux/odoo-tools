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
import logging
import re
_log = logging.getLogger(__name__)


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.one
    def hangout_notify(self):
        def cleanhtml(raw_html):
            raw_html = raw_html.replace('<br/>', '\n').replace('<br>', '\n')
            raw_html = raw_html.replace('</p>', '\n').replace('<p/>', '\n')
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        try:
            for m in self.message_ids:
                if self.message_ids[1].author_id.company_id != self.company_id:
                    self.company_id.hangoutSendMessage('%s' % m.body)
        except Exception as e:
            _log.error('When notify issue to Hangout: %s' % e)
