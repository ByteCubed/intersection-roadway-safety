-- You can ingest the EPA smart location database manually by right clicking the schema and selecting "Import Data", then proceeding through the wizard.

-- 0.0015625
-- Magic number to turn acres into square miles

select * from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%DC%';
select * from public.epa_smartlocationdatabase_v3_jan esvj where csa_name = '';
select distinct cbsa_name from public.epa_smartlocationdatabase_v3_jan esvj where csa_name = '';
select distinct csa_name from public.epa_smartlocationdatabase_v3_jan esvj;
select * from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%IA%';
select distinct csa, csa_name from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%DC%';
select sum(ac_unpr) from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%DC%';

select d3b * ac_unpr, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj where csa=548;
select (((D3bmm3 *0.667) + D3bmm4) * ac_unpr)::int, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj where csa=548;
select sum(intersection_count) from (
select (((D3bmm3 *0.667) + D3bmm4) * ac_unpr * 0.0015625)::int as intersection_count, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj where csa=548) sq;
select sum(intersection_count) from (
select (D3b * ac_unpr * 0.0015625)::int as intersection_count, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj where csa=548) sq;



select sum(big), sum(little) from
(select geoid20, max(ac_unpr) as big, min(ac_unpr) as little from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%DC%' group by geoid20) sq;

select geoid20 from
(select geoid20, min(ac_unpr) as little from public.epa_smartlocationdatabase_v3_jan esvj where csa_name like '%DC%' group by geoid20) sq;


select sum(intersection_count) from (
select (((D3bmm3 *0.667) + D3bmm4) * ac_unpr)::int as intersection_count, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj where csa=548 and shape_area =
min(select shape_area from public.epa_smartlocationdatabase_v3_jan esvj2 where csa_name like '%DC%' and esvj2.object_id = esvj.objectid) ssq
)) sq;

select sum(intersection_count) from (
select (((D3bmm3 *0.667) + D3bmm4) * ac_unpr * 0.0015625)::int as intersection_count, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj 
where csa=548 and shape_area = 
(select min(shape_area) from public.epa_smartlocationdatabase_v3_jan esvj2 where csa_name like '%DC%' and esvj2.geoid20 = esvj.geoid20)
)sq;

select sum(intersection_count) from (
select (D3b * ac_unpr * 0.0015625)::int as intersection_count, d3b, ac_unpr, * from public.epa_smartlocationdatabase_v3_jan esvj 
where csa=548 and shape_area = 
(select min(shape_area) from public.epa_smartlocationdatabase_v3_jan esvj2 where csa_name like '%DC%' and esvj2.geoid20 = esvj.geoid20)
)sq;

