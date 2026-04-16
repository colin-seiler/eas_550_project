SELECT
    ReviewID AS review_key,
    OrderID AS order_key,
    Score AS review_score,
    Title AS review_title,
    Comment AS review_comment,
    Creation::DATE AS review_creation_date,
    Answer::DATE AS review_answer_date
FROM commerce.reviews