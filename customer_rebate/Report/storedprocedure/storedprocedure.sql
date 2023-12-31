-- Function: customer_rebate_report(date, date)
--select * from customer_rebate_report('2016-01-01','2016-12-31')
-- DROP FUNCTION customer_rebate_report(date, date);

CREATE OR REPLACE FUNCTION customer_rebate_report(IN param_from_date date, IN param_to_date date)
  RETURNS TABLE(id bigint, customer_id integer, customer_name character varying, product_name character varying, qty integer, rebate_amount numeric, promotion character varying, product_id integer, state character varying, rebate_date date, section_id integer, user_id integer, name character varying, date_order date) AS
$BODY$
declare 
	so_data record ;
	rebate_data record;
	amount numeric;	
	max_qty integer;
	begin  
			
		DELETE FROM rebate_temp;
		
		FOR so_data IN
			select (so.date_order+'6 hour'::interval+'30 minutes'::interval)::date as sale_order_date,so.state,so.name,so.section_id,so.user_id as saleman_name,res.id as customer_id,res.name as customer_name,pp.id as product_id,pp.name_template as product_name,product_uos_qty,uom.name as uom
			from sale_order so,res_partner res,sale_order_line sol,product_product pp,product_template pt,product_uom uom
			where so.partner_id=res.id
			and sol.order_id=so.id
			and sol.product_id=pp.id
			and pp.product_tmpl_id=pt.id
			and pt.uom_id=uom.id
			and so.state in ('progress','manual','done')
			and (so.date_order+'6 hour'::interval+'30 minutes'::interval)::date between param_from_date and param_to_date

		LOOP				
			FOR rebate_data IN	 
				select config.code as promotion,sale_qty,uom.name,comparator,exps.rebate_amount,config.date
				from customer_rebate_config config,customer_rebate_config_conditions_exps exps,product_uom uom
				where config.id=exps.rebate
				and uom.id=exps.product_uom_id
				and so_data.sale_order_date between config.from_date and config.to_date
				and exps.product_id=so_data.product_id
				and uom.name=so_data.uom
				
			LOOP
				select max(sale_qty) into max_qty
				from customer_rebate_config config,customer_rebate_config_conditions_exps exps,product_uom uom
				where config.id=exps.rebate
				and uom.id=exps.product_uom_id
				and so_data.sale_order_date between config.from_date and config.to_date
				and exps.product_id=so_data.product_id
				and uom.name=so_data.uom
				and comparator=rebate_data.comparator;
				
				IF LOWER(so_data.uom)=LOWER('Viss') AND LOWER(rebate_data.name)=LOWER('Viss') THEN						
					IF rebate_data.comparator= '==' THEN						
						IF so_data.product_uos_qty = rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '!=' THEN
						IF so_data.product_uos_qty != rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;						
					ELSEIF rebate_data.comparator= '<' THEN
						IF so_data.product_uos_qty < rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '<=' THEN
						IF so_data.product_uos_qty <= rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '>' THEN
						IF so_data.product_uos_qty > max_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '>=' THEN
						IF so_data.product_uos_qty >= rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					END IF;
				END IF;
				IF LOWER(so_data.uom)=LOWER('Paper') AND LOWER(rebate_data.name)=LOWER('Paper') THEN						
					IF rebate_data.comparator= '==' THEN						
						IF so_data.product_uos_qty = rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '!=' THEN
						IF so_data.product_uos_qty != rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;						
					ELSEIF rebate_data.comparator= '<' THEN
						IF so_data.product_uos_qty < rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '<=' THEN
						IF so_data.product_uos_qty <= rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '>' THEN
						IF so_data.product_uos_qty > rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					ELSEIF rebate_data.comparator= '>=' THEN
						IF so_data.product_uos_qty >= rebate_data.sale_qty THEN
							amount=so_data.product_uos_qty*115*rebate_data.rebate_amount;							
							insert into rebate_temp(promotion,rebate_date,product_id,state,customer_id,customer_name,product_name,qty,rebate_amount,section_id,user_id,name,date_order) values (rebate_data.promotion,rebate_data.date,so_data.product_id,so_data.state,so_data.customer_id,so_data.customer_name,so_data.product_name,so_data.product_uos_qty,amount,so_data.section_id,so_data.saleman_name,so_data.name,so_data.sale_order_date);	
						END IF;	
					END IF;
				END IF;
			END LOOP; 
		END LOOP; 
			
		RETURN QUERY select row_number() over (order by temp.customer_id) as seq,* from rebate_temp temp;
			  
	end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION customer_rebate_report(date, date)
  OWNER TO postgres;
  
-- Table: rebate_temp

-- DROP TABLE rebate_temp;
-- select * from sale_order

--CREATE TABLE rebate_temp
--(
--  customer_id integer,
--  customer_name character varying,
--  product_name character varying,
--  qty integer,
--  rebate_amount numeric,
--  promotion character varying,
--  product_id integer,
--  state character varying,
--  rebate_date date,
--  section_id integer,
--  user_id integer,
--  name character varying,
--  order_date date
  
--)
--WITH (
--  OIDS=FALSE
--);