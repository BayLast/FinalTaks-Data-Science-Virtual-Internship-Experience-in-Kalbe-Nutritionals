--Query 1: Berapa rata-rata umur customer jika dilihat dari marital statusnya?
--Age Average of each Marital Status
select "Marital Status", round(avg(age)) age_avg
from customer c
group by "Marital Status" 

--Query 2: Berapa rata-rata umur customer jika dilihat dari gender nya?
--Age average of each gender
SELECT 
    CASE 
        WHEN Gender = 1 THEN 'Male'
        WHEN Gender = 0 THEN 'Female'
        ELSE 'Other'
    END AS Gender_Type, 
    round (AVG(Age)) AS average_age
FROM 
    "customer"
GROUP BY 
    Gender_Type;

-- Query 3: Tentukan nama store dengan total quantity terbanyak!
--Store with highest Quantity Sales 
select sum(qty) total_qty, css.storename  
from "Transaction" cst  
join store css
on cst.storeid = css.storeid 
group by css.storename
order by 1 desc
limit 1

-- Query 4: Tentukan nama produk terlaris dengan total amount terbanyak!
-- Product with highest total amount sales
select sum(totalamount) total_amount_sum, csp."Product Name" 
from "Transaction" cst 
join product csp 
on cst.productid = csp.productid 
group by 2
order by 1 desc
limit 1