# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

{
    'name': 'MDG- accounting',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'description': """
Chart of Accounts for Myanmar Distribution Group.
======================================

MDG accounting chart and localization.
    """,
    'author': 'Yin May',
    'website': 'http://7thcomputing.com/',
    'depends': ['account_chart', 'account_accountant'],
    'data': [ 'data/account.account.type.csv',
              'data/account.account.template.csv',
              'data/account.chart.template.csv',
              ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

