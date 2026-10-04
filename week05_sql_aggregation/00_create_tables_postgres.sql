BEGIN;
CREATE SCHEMA IF NOT EXISTS bdai13;

CREATE TABLE bdai13.customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT, region TEXT, joined_date DATE
);
CREATE TABLE bdai13.products (
    product_id INTEGER PRIMARY KEY,
    name TEXT, category TEXT, price INTEGER
);
CREATE TABLE bdai13.orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES bdai13.customers(customer_id),
    order_date DATE, order_total INTEGER
);
CREATE TABLE bdai13.order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES bdai13.orders(order_id),
    product_id INTEGER REFERENCES bdai13.products(product_id),
    qty INTEGER, unit_price INTEGER
);
CREATE TABLE bdai13.logins (
    login_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES bdai13.customers(customer_id),
    login_date DATE
);

ALTER TABLE bdai13.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bdai13.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE bdai13.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE bdai13.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE bdai13.logins ENABLE ROW LEVEL SECURITY;
COMMIT;
