try:
    import simplejson as json
except ImportError:
    import json     # noqa
import urllib

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

def geo_find(addr):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise osv.except_osv(_('Network error'),
                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))

class outlet_type(osv.osv):
    _name = 'outlettype.outlettype'
    _columns = {
                'name':fields.char('Outlet Name'),
                }

    
outlet_type()

class res_partner(osv.osv):

    _inherit = 'res.partner'                           
    _columns = {  
                'customer_code':fields.char('Code', required=True),  
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type', required=True),                
                'temp_customer':fields.char('Contact Person'),                
                'class_id':fields.many2one('sale.class', 'Class'),  
                'old_code': fields.char('Old Code'), 
                'sales_channel':fields.many2one('sale.channel', 'Sale Channels'),
                'address':fields.char('Address'),   
                'branch_id':fields.many2one('sale.branch', 'Branch'),               
                'demarcation_id': fields.many2one('sale.demarcation', 'Demarcation'),                 
                'mobile_customer': fields.boolean('Mobile Customer', help="Check this box if this contact is a mobile customer. If it's not checked, purchase people will not see it when encoding a purchase order."),
    } 
    
    _sql_constraints = [        
        ('customer_code_uniq', 'unique (customer_code)', 'Customer code must be unique !'),
    ]
    
    def geo_localize(self, cr, uid, ids, context=None):
        # Don't pass context to browse()! We need country names in english below
        for partner in self.browse(cr, uid, ids):
            if not partner:
                continue
            result = geo_find(geo_query_address(street=partner.street,
                                                zip=partner.zip,
                                                city=partner.city.name,
                                                state=partner.state_id.name,
                                                country=partner.country_id.name))
            if result:
                print 'result',result
                print 'result_latitude',result[0]
                print 'resul_longitude',result[1]
                self.write(cr, uid, [partner.id], {
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.date.context_today(self, cr, uid, context=context)
                }, context=context)
        return True
    
    def partner_id_from_sale_plan_day(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('select RP.id from sale_plan_day SPD , res_partner_sale_plan_day_rel RPS , res_partner RP where SPD.id = RPS.sale_plan_day_id and RPS.res_partner_id = RP.id and SPD.sale_team = %s ', (sale_team_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def partner_id_from_sale_plan_trip(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('select RP.id from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP where SPT.id = RPT.sale_plan_trip_id and RPT.res_partner_id = RP.id and SPT.sale_team =  %s ', (sale_team_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def partner_id_from_section_id(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('select id from res_partner where section_id = %s ', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def res_partners_return(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''
                    

 select A.id,A.name,A.image,A.is_company,
                     A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude  from (

                     select RP.id,RP.name,RP.image,RP.is_company,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_day SPD ,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP ,res_country_state RS
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and  RS.id = RP.state_id
                                            and RPS.res_partner_id = RP.id 
                                            and SPD.sale_team = %s
                                            union

                                            select RP.id,RP.name,RP.image,RP.is_company,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory ,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP ,res_country_state RS 
                                            where SPT.id = RPT.sale_plan_trip_id 
                        and RPT.res_partner_id = RP.id 
                        and  RS.id = RP.state_id
                        and SPT.sale_team = %s
                        )A 
                        where A.shop_name is not null
                    and A.customer_code is not null 
            ''', (section_id, section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    #kzo Eidt
    def res_partners_return_day(self, cr, uid, section_id, day_id , context=None, **kwargs):
        print'res_partners_return_day'
        cr.execute('''
                    

 select A.id,A.name,A.image,A.is_company,
                     A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id  from (

                     select RP.id,RP.name,RP.image,RP.is_company,RPS.sale_plan_day_id,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_day SPD ,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP ,res_country_state RS
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and  RS.id = RP.state_id
                                            and RPS.partner_id = RP.id 
                                            and SPD.sale_team = %s
                                            and RPS.sale_plan_day_id = %s
                                            
                        )A 
                        where A.customer_code is not null
            ''', (section_id,day_id, ))
        datas = cr.fetchall()
        return datas
        #kzo Edit add Sale Plan Trip and Day ID
    def res_partners_return_trip(self, cr, uid, section_id, day_id , context=None, **kwargs):
        cr.execute('''
                    

 select A.id,A.name,A.image,A.is_company,
                     A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_trip_id   from (

                     select RP.id,RP.name,RP.image,RP.is_company,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory ,RPT.sale_plan_trip_id,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP ,res_country_state RS 
                                            where SPT.id = RPT.sale_plan_trip_id 
                        and RPT.partner_id = RP.id 
                        and  RS.id = RP.state_id
                        and SPT.sale_team = %s
                        and RPT.sale_plan_trip_id = %s                   
                        )A 
                        where A.customer_code is not null 
            ''', (section_id,day_id, ))
        datas = cr.fetchall()
        cr.execute
        return datas
res_partner()



  





     


    
    
    
