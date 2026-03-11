CREATE SCHEMA IF NOT EXISTS Commerce;
SET search_path TO Commerce;

CREATE TABLE Commerce.Zips (
    Zip VARCHAR(5) PRIMARY KEY,
    Lat NUMERIC(9, 6) NOT NULL,
    Lng NUMERIC(9, 6) NOT NULL,
    City VARCHAR(50) NOT NULL,
    State VARCHAR(20) NOT NULL
);

CREATE TABLE Commerce.Customers (
    CustID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Reference VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE Commerce.Sellers (
    SellerID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Reference VARCHAR(32) NOT NULL UNIQUE,
    Zip VARCHAR(5) REFERENCES Zips(Zip)
);

CREATE TABLE Commerce.Products (
    ProductID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Reference VARCHAR(32) NOT NULL UNIQUE,
    Category VARCHAR(100),
    NameLength INT,
    DescLength INT,
    PhotoCount INT,
    WeightG INT,
    LengthCM INT,
    HeightCM INT,
    WidthCM INT
);

CREATE TYPE Commerce.Status_ENUM AS ENUM (
    'delivered',
    'canceled',
    'shipped',
    'invoiced',
    'unavailable'
);

CREATE TABLE Commerce.Orders (
    OrderID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Reference VARCHAR(32) NOT NULL UNIQUE,
    CustID BIGINT REFERENCES Customers(CustID),
    Zip VARCHAR(5) REFERENCES Zips(Zip),
    Status Status_ENUM,
    OrderPurchaseTime TIMESTAMPTZ NOT NULL,
    OrderApprovalTime TIMESTAMPTZ,
    OrderDeliverCarrier TIMESTAMPTZ,
    OrderDeliverCustomer TIMESTAMPTZ,
    OrderDeliverEstimate TIMESTAMPTZ
);

CREATE TABLE Commerce.OrderItems (
    OrderID BIGINT REFERENCES Orders(OrderID),
    OrderItemID INT NOT NULL,
    ProductID BIGINT REFERENCES Products(ProductID),
    SellerID BIGINT REFERENCES Sellers(SellerID),
    ShippingLimit TIMESTAMPTZ,
    Price NUMERIC(10, 2),
    Freight NUMERIC(10, 2),
    PRIMARY KEY (OrderID, OrderItemID)
);

CREATE TABLE Commerce.Reviews (
    ReviewID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OrderID BIGINT REFERENCES Orders(OrderID),
    Score INT CHECK (Score BETWEEN 1 AND 5),
    Title VARCHAR,
    Comment VARCHAR,
    Creation TIMESTAMPTZ,
    Answer TIMESTAMPTZ
);

CREATE TYPE Commerce.Payment_ENUM AS ENUM (
    'credit_card',
    'boleto',
    'voucher',
    'debit_card',
    'not_defined'
);

CREATE TABLE Commerce.Payments (
    OrderID BIGINT REFERENCES Orders(OrderID),
    PaySeq INT NOT NULL,
    PayType Payment_ENUM,
    PayInstallments INT NOT NULL,
    PayAmount NUMERIC(10, 2),
    PRIMARY KEY (OrderID, PaySeq)
);