# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Invoice Customization',
    'version': '1.0',
    'category': 'Invoice',
    'sequence': 30,
    'summary': 'Invoice For Tax',
    'description': """
Invoice Customization For Tax Exclusive or Inclusive Customer.

""",
    'author': 'Seventh Computing Developer Group',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base','sale','report'],
    'data': [

        'views/invoice_custom_layouts.xml',
        'views/report_invoice.xml',
        'views/invoice_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
