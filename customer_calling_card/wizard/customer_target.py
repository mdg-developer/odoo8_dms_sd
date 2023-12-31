#-*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
from math import floor
_logger = logging.getLogger(__name__)
#header_fields = ['default_code', 'product_name', 'public_price', 'uom', 'balance_qty', 'cost_price']
header_fields = ['product',  'uom', 'real quantity', 'serial number','theoretical quantity','location','pack','serial']

class customer_target(osv.osv):
    _name = 'customer.target'
    _description = 'Customer Target'
    _columns = {
        'partner_id': fields.many2one('res.partner', string='Customer'),
        'outlet_type': fields.many2one('outlettype.outlettype',string="Outlet type"), 
        'address': fields.char(string='Address'), 
        'date': fields.date(string="Target Date",required=True), 
        'township': fields.many2one('res.township',string="Township"),          
        'branch_id': fields.many2one('res.branch',string="Branch"),
        'section_ids': fields.many2many('crm.case.section','customer_target_team_rel','target_id','section_id',string="Sale Team"),
        'delivery_team_id': fields.many2one('crm.case.section',string="Delivery Team"),
        'delivery': fields.char(string='Delivery'),   
        'updated_by': fields.many2one('res.users',string="Updated By"),
        'updated_time': fields.datetime(string='Updated Date Time'),
        #'target_id':fields.many2one('res.partner', 'Target Items'),                      
        'target_line_ids':fields.one2many('customer.target.line', 'line_id', 'Target Items'),
    }
    _defaults = {
       
    }
  
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    #_constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(customer_target, self).default_get(cr, uid, fields, context=context)
        partner_ids = context.get('partner_id', False)
        if partner_ids and 'partner_id' in fields:
            for partner_id in self.pool.get('res.partner').browse(cr,uid,partner_ids,context=context):
                partner = {'partner_id': partner_id.id,'outlet_type':partner_id.outlet_type.id,'township':partner_id.township.id,'address':partner_id.street,'delivery_team_id':partner_id.delivery_team_id.id,'branch_id':partner_id.branch_id.id}
                res.update(partner)
        return res
    
    
    def get_so_qty(self,cr,uid,ids,t_date,partner_id,outlet_type,context=None):
        month_count = 6
        start_date = end_date = first_t_date = None
        month_qty = []
        if t_date:
            year,month,date = t_date.split('-')
            end_date = year + '-' + month + '-' + '01'
            first_t_date = end_date
            cr.execute("select (%s::timestamp - '6 month'::interval)::date",(end_date,))
            start_date = cr.fetchone()[0]
            
            cr.execute("select (%s::timestamp - '1 day'::interval)::date",(end_date,))
            end_date = cr.fetchone()[0]
#             start_year,start_month,start_day = start_date.split('-')
#             if start_month not in ('10','11','12'):
#                start_month = start_month.replace('0','')
            customer_target_line_obj = self.pool.get('customer.target.line')
            line_ids = customer_target_line_obj.search(cr,uid,[('line_id','=',ids[0])],context=context)
            
            stock_check_setting_obj = self.pool.get('stock.check.setting')
            stock_check_id = stock_check_setting_obj.search(cr,uid,[('outlet_type','=',outlet_type.id)],context=context)
            stock_check_setting_line_obj = self.pool.get('stock.check.setting.line')
            stock_check_setting_ids = None
            if stock_check_id:
                stock_check_setting_ids = stock_check_setting_line_obj.search(cr,uid,[('stock_setting_ids','=',stock_check_id[0]),('available','=',True)],context=context)
            if not line_ids:
                if stock_check_setting_ids:
#                     for rec in self.pool.get('product.product').browse(cr, uid, product, context=context):
#                         uom_id = rec.product_id.product_tmpl_id.report_uom_id.id or rec.product_id.product_tmpl_id.uom_id.id
                    for stock_setting_id in stock_check_setting_line_obj.browse(cr,uid,stock_check_setting_ids,context):
                        data ={
                               'product_id':stock_setting_id.product_id.id,
                               'line_id':ids[0],
                               #'product_uom':uom_id,
                               }
                        new_id = customer_target_line_obj.create(cr,uid,data,context=context)
            else:
                if stock_check_id: 
                    cr.execute("""select product_id from stock_check_setting_line where stock_setting_ids =%s and product_id not in (select product_id from customer_target_line where line_id=%s)
                    and available='t'""",(stock_check_id[0],ids[0],))
                    product_data = cr.fetchall()
                    for p_id in product_data:
                        data ={
                                   'product_id':p_id[0],
                                   'line_id':ids[0],
                                   #'product_uom':uom_id,
                                   }
                        new_id = customer_target_line_obj.create(cr,uid,data,context=context)            
            #cr.execute("""select *  from customer_target_data(%s,%s,%s)""",(start_date,t_date,ids,))
            #cr.execute("SELECT * FROM customer_target_data( %s,%s,%s); ",(start_date,t_date,ids))
            cr.execute("""
            SELECT * FROM crosstab(
                       $$
                       SELECT product_id,rn,qty
                         FROM  (
                        select a.product_id,sum(a.qty)as qty,a.yyyy,a.mm,row_number() OVER (PARTITION BY a.product_id
                                    ORDER BY a.yyyy,a.mm) AS rn     from(
                        SELECT d.product_id,extract(year from date_order::date) as yyyy,extract(month from date_order::date) as mm,
                        sum(d.product_uom_qty) * floor(round(1/u.factor,2)) as qty 
                        from sale_order h,sale_order_line d,product_product p,product_template t,product_uom u
                        where h.id=d.order_id and d.product_id=p.id and p.product_tmpl_id=t.id and d.product_uom=u.id
                        and h.date_order::date>=%s and h.date_order::date<=%s and h.partner_id=%s and h.state in('progress','manual','done')
                        group by d.product_id,u.factor,extract(year from date_order::date),extract(month from date_order::date)
                        union
                        
                        select c.product_id as product_id,extract(year from i::date) as yyyy,extract(month from i::date) as mm,0::numeric as qty 
                        from generate_series(%s,%s, '1 day'::interval) i,customer_target_line c
                        where c.line_id=%s
                        )a
                        group by a.product_id,a.yyyy,a.mm order by a.yyyy,a.mm
                        --order by yyyy,mm
                        ) sub
                        
                       $$
                      , 'VALUES (1),(2),(3),(4),(5),(6)'
                       ) AS t (product_id integer,month1 numeric,month2 numeric,month3 numeric,month4 numeric,month5 numeric,month6 numeric);
            """,(start_date,end_date,partner_id,start_date,end_date,ids[0],))
            for product_line in cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
                print 'product_line>>>',product_line
                for key, value in product_line.items():
                    if not value:
                        product_line[key] = 0
               
                if product_line['product_id']:
                    cr.execute("""
                    select sum(a.qty)as qty    
                    from(
                        SELECT d.product_id,
                        sum(d.product_uom_qty) * floor(round(1/u.factor,2)) as qty 
                        from sale_order h,sale_order_line d,product_uom u
                        where h.id=d.order_id and d.product_uom=u.id
                        and h.date_order::date>=%s and h.date_order::date<=%s and h.partner_id=%s
                        and h.state in('progress','manual','done')
                        and d.product_id=%s
                        group by d.product_id,u.factor)a
                    """,(first_t_date,t_date,partner_id,product_line['product_id'],))
                    ach_data=cr.fetchone()
                    achieve =0
                    if ach_data:
                        achieve = ach_data[0]
                    product = month1 = month12 = month3 = month4 = month5 = month6 = None
                    total = 0
                    product = product_line['product_id']
                    month1 = product_line['month1']
                    month2 = product_line['month2']
                    month3 = product_line['month3']
                    month4 = product_line['month4']
                    month5 = product_line['month5']
                    month6 = product_line['month6']
                    #print 'product>>>',product
                    line_ids = customer_target_line_obj.search(cr,uid,[('line_id','=',ids[0]),('product_id','=',product)],context=context)
                              
                    for target in customer_target_line_obj.browse(cr, uid, line_ids, context):
                        
                        if month1 is not None and month1 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month1 = month1 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month1':month1                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        if month2 is not None and month2 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month2 = month2 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month2':month2                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        if month3 is not None and month3 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month3 = month3 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month3':month3                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        if month4 is not None and month4 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month4 = month4 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month4':month4                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        if month5 is not None and month5 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month5 = month5 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month5':month5                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        if month6 is not None and month6 > 0:
                            if target.product_id.product_tmpl_id.uom_id != target.product_uom:
                                month6 = month6 / floor(round(1/target.product_uom.factor))
                            value = {
                                 'month6':month6                                     
                                 }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                        new_id = customer_target_line_obj.browse(cr,uid,target.id,context=context)
                        if new_id:
                            total = new_id.month1 + new_id.month2 + new_id.month3 + new_id.month4 + new_id.month5 + new_id.month6
                        if achieve > 0:
                            ach_percent = 0
                            gap_qty =0
                            if target.target_qty > 0:
                                ach_percent = (achieve / target.target_qty) * 100
                                gap_qty =  target.target_qty -  achieve   
                            customer_target_line_obj.write(cr, uid, target.id, {'ach_qty':achieve,'ach_percent':ach_percent,'gap_qty':gap_qty}, context=context)
                        if total > 0:
                            total = total / 6    
                            value = {
                                     
                                     '6ams' : total,
                                     }
                            customer_target_line_obj.write(cr, uid, target.id, value, context=context)
                                                       
    def close(self,cr,uid,ids,context=None):
        return {'type': 'ir.actions.act_window_close'}
    
    def update(self, cr, uid, ids, context=None):
        
        
        data = self.browse(cr, uid, ids)[0]
        if data:
            self.get_so_qty(cr, uid, ids, data.date,data.partner_id.id,data.outlet_type,context=None)
            self.write(cr, uid, ids, {'updated_by':uid,'updated_time':fields.datetime.now()}, context=context)
        #import_file = data.sl_data
        # print 'file',data.sl_data
                   
customer_target()
  
class customer_target_line(osv.osv):
    _name = 'customer.target.line'
    
    
    def _get_uom_from_product(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.product_id.product_tmpl_id.report_uom_id.id or rec.product_id.product_tmpl_id.uom_id.id
        return result  
    def _get_price_from_product(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.product_id.product_tmpl_id.list_price
        return result      
    
    def _amount_6ams(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0)

#         res=dict(cr.fetchall())
        for target in self.browse(cr, uid, ids, context):
#             company_currency =  self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#             current_currency = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#             amount = self.pool['res.currency'].compute(cr, uid, company_currency, current_currency, res.get(target.id, 0.0), context=context)
            cr.execute("""SELECT
                SUM(abs(l.month1+l.month2+l.month3+l.month4+l.month5+l.month6))/6 AS amount
            FROM
                customer_target_line l
            WHERE
                l.id IN %s GROUP BY l.line_id,l.product_id """, (tuple(ids),))
            data = cr.fetchall() 
            if data:
                amount = data[0][0]
            res[target.id] =  amount 
#         for id in ids:
#             res.setdefault(id, 0.0)
        return res
    
    _columns = {
                
                'line_id':fields.many2one('customer.target', 'Target Items'),
               
                'product_id':fields.many2one('product.product', 'Product Name'),
                #'product_uom':fields.many2one('product.uom', 'UOM',readonly=True,required=True),            
                'product_uom':fields.function(_get_uom_from_product, type='many2one', relation='product.uom', string='UOM'),
                'price':fields.function(_get_price_from_product, type='float', string='Unit Price'),
                'month1':fields.float('Month1'),
                'month2':fields.float('Month2'),
                'month3':fields.float('Month3'),
                'month4':fields.float('Month4'),
                'month5':fields.float('Month5'),
                'month6':fields.float('Month6'),
                '6ams':fields.float('6 A.M.S'),                
#                 '6ams': fields.function(_amount_6ams, type='float', method=True, store=True,                                            
#                                              string='6 A.M.S'),
                'target_qty':fields.float('Target Qty'),
                'ach_qty':fields.float('Achieve Qty'),
                'ach_percent':fields.float('Ach %'), 
                'gap_qty':fields.float('Gap'),  
                }
    def onchange_product(self, cr, uid, ids, product_id=False,context=False):
        if not context:
            context = {}
        val = {}
#         if type_id:
        p = self.pool.get('product.product').browse(cr, uid, product_id)
        if p:
            val['product_uom'] =  p.product_tmpl_id.report_uom_id.id or p.product_tmpl_id.uom_id.id
                
        return {'value': val}