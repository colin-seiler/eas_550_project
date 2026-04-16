SELECT
    OrderID AS order_key,
    PaySeq AS order_pay_num,
    PayType AS order_pay_type,
    PayInstallments AS order_pay_installments,
    PayAmount AS order_pay_amount
FROM commerce.payments