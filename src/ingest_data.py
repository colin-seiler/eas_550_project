import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("SET search_path TO Commerce;")

# geolocation has duplicate zips so we average lat/lng and take first city/state
geo = pd.read_csv("data/olist_geolocation_dataset.csv")
geo.columns = ["Zip", "Lat", "Lng", "City", "State"]
geo["Zip"] = geo["Zip"].astype(str).str.zfill(5)
zips = geo.groupby("Zip").agg({"Lat": "mean", "Lng": "mean", "City": "first", "State": "first"}).reset_index()

for _, r in zips.iterrows():
    cur.execute("INSERT INTO Commerce.Zips VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (r.Zip, r.Lat, r.Lng, r.City, r.State))
print("zips done")

customers = pd.read_csv("data/olist_customers_dataset.csv")
for _, r in customers.iterrows():
    cur.execute("INSERT INTO Commerce.Customers (Reference) VALUES (%s) ON CONFLICT DO NOTHING",
                (r["customer_unique_id"],))
print("customers done")

sellers = pd.read_csv("data/olist_sellers_dataset.csv")
sellers["seller_zip_code_prefix"] = sellers["seller_zip_code_prefix"].astype(str).str.zfill(5)
valid_zips = set(zips["Zip"])
for _, r in sellers.iterrows():
    z = r["seller_zip_code_prefix"] if r["seller_zip_code_prefix"] in valid_zips else None
    cur.execute("INSERT INTO Commerce.Sellers (Reference, Zip) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (r["seller_id"], z))
print("sellers done")

products = pd.read_csv("data/olist_products_dataset.csv")
for _, r in products.iterrows():
    cur.execute("""INSERT INTO Commerce.Products
        (Reference, Category, NameLength, DescLength, PhotoCount, WeightG, LengthCM, HeightCM, WidthCM)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
        (r["product_id"], r.get("product_category_name"),
         int(r["product_name_lenght"]) if pd.notna(r.get("product_name_lenght")) else None,
         int(r["product_description_lenght"]) if pd.notna(r.get("product_description_lenght")) else None,
         int(r["product_photos_qty"]) if pd.notna(r.get("product_photos_qty")) else None,
         int(r["product_weight_g"]) if pd.notna(r.get("product_weight_g")) else None,
         int(r["product_length_cm"]) if pd.notna(r.get("product_length_cm")) else None,
         int(r["product_height_cm"]) if pd.notna(r.get("product_height_cm")) else None,
         int(r["product_width_cm"]) if pd.notna(r.get("product_width_cm")) else None))
print("products done")

# need the db-generated IDs to use as foreign keys
cur.execute("SELECT Reference, CustID FROM Commerce.Customers")
cust_map = dict(cur.fetchall())
cur.execute("SELECT Reference, SellerID FROM Commerce.Sellers")
seller_map = dict(cur.fetchall())
cur.execute("SELECT Reference, ProductID FROM Commerce.Products")
product_map = dict(cur.fetchall())

def clean_ts(val):
    if pd.isna(val) or str(val) == 'nan':
        return None
    return val

# orders csv uses customer_id not unique_id so need to map it
customers_df = pd.read_csv("data/olist_customers_dataset.csv")
cust_id_map = dict(zip(customers_df["customer_id"], customers_df["customer_unique_id"]))
cust_zip_map = dict(zip(customers_df["customer_id"], customers_df["customer_zip_code_prefix"].astype(str).str.zfill(5)))

valid_statuses = {"delivered", "canceled", "shipped", "invoiced", "unavailable"}
orders = pd.read_csv("data/olist_orders_dataset.csv")
for _, r in orders.iterrows():
    cid = cust_map.get(cust_id_map.get(r["customer_id"]))
    zip_code = cust_zip_map.get(r["customer_id"])
    zip_code = zip_code if zip_code in valid_zips else None
    status = r["order_status"] if r["order_status"] in valid_statuses else None
    cur.execute("""INSERT INTO Commerce.Orders
        (Reference, CustID, Zip, Status, OrderPurchaseTime, OrderApprovalTime,
         OrderDeliverCarrier, OrderDeliverCustomer, OrderDeliverEstimate)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
        (r["order_id"], cid, zip_code, status,
         clean_ts(r.get("order_purchase_timestamp")),
         clean_ts(r.get("order_approved_at")),
         clean_ts(r.get("order_delivered_carrier_date")),
         clean_ts(r.get("order_delivered_customer_date")),
         clean_ts(r.get("order_estimated_delivery_date"))))
print("orders done")

cur.execute("SELECT Reference, OrderID FROM Commerce.Orders")
order_map = dict(cur.fetchall())

items = pd.read_csv("data/olist_order_items_dataset.csv")
for _, r in items.iterrows():
    oid = order_map.get(r["order_id"])
    pid = product_map.get(r["product_id"])
    sid = seller_map.get(r["seller_id"])
    if not oid or not pid or not sid:
        continue
    cur.execute("""INSERT INTO Commerce.OrderItems
        (OrderID, OrderItemID, ProductID, SellerID, ShippingLimit, Price, Freight)
        VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
        (oid, r["order_item_id"], pid, sid, r.get("shipping_limit_date") or None,
         r.get("price"), r.get("freight_value")))
print("order items done")

reviews = pd.read_csv("data/olist_order_reviews_dataset.csv")
for _, r in reviews.iterrows():
    oid = order_map.get(r["order_id"])
    if not oid:
        continue
    cur.execute("""INSERT INTO Commerce.Reviews (OrderID, Score, Title, Comment, Creation, Answer)
        VALUES (%s,%s,%s,%s,%s,%s)""",
        (oid, r.get("review_score"), r.get("review_comment_title") or None,
         r.get("review_comment_message") or None, r.get("review_creation_date") or None,
         r.get("review_answer_timestamp") or None))
print("reviews done")

valid_pay = {"credit_card", "boleto", "voucher", "debit_card", "not_defined"}
payments = pd.read_csv("data/olist_order_payments_dataset.csv")
for _, r in payments.iterrows():
    oid = order_map.get(r["order_id"])
    if not oid:
        continue
    ptype = r["payment_type"] if r["payment_type"] in valid_pay else "not_defined"
    cur.execute("""INSERT INTO Commerce.Payments (OrderID, PaySeq, PayType, PayInstallments, PayAmount)
        VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
        (oid, r["payment_sequential"], ptype, r["payment_installments"], r.get("payment_value")))
print("payments done")

conn.commit()
cur.close()
conn.close()
print("all done!")