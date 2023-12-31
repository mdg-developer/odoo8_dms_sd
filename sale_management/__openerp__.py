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
    'name': 'Sale Management',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 30,
    'summary': 'Sale',
    'description': """
Sale Management

""",
    'author': 'Seventh Computing Developer Group',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'sale', 'crm_demarcation', 'account', 'account_accountant',
                'stock', 'sale_stock', 'ms_sale_plan_setting'
    ],
    'data': [
       # 'views/product_product_view.xml',
       'views/code_sequence.xml',
       'views/invoice_custom_layouts.xml',
       'views/sale_custom_layouts.xml',
       'views/report_saleorder.xml',
       'views/report_invoice.xml',
       'wizard/sale_team_date_view.xml',
        'wizard/location_assign_view.xml',
        'views/account_invoice_view.xml',
        'views/sale_team_view.xml',
        'views/sale_order_view.xml',
        'views/sale_return_view.xml',
        'views/sale_display_view.xml',
		'views/sales_retal_view.xml',
		'views/sales_denomation_view.xml',
		'views/sale_approvel_view.xml',
         'views/sale_promotion_history_view.xml',
        'views/sale_promotion_monthly_view.xml',
        'views/sale_target_view.xml',
        'views/sale_target_branch_view.xml',
        'views/sale_target_outlet_view.xml',
        'views/sale_target_nation_view.xml',
        'reports/qweb_view.xml',
        'reports/report_denomination.xml',
        'reports/custom_layout.xml',
        'reports/deliver_order_custom_layouts.xml',
        'reports/report_pre_sale_order.xml',
        'reports/credit_debit_note_layout.xml',
        'views/report_invoice_with_price.xml',
        'reports/report_credit_note.xml',
        'reports/report_debit_note.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
