-- ====================
-- Запрос 1: Получение информации о сумме товаров заказанных под каждого клиента 
-- ====================
SELECT 
  c.id,
    c.name,
    SUM(i.quantity * i.price_in_order) AS total_amount
FROM orders_client c
LEFT JOIN orders_order o ON c.id = o.client_id
LEFT JOIN orders_iteminorder i ON o.id = i.order_id
WHERE o.status IN ('paid', 'done')
GROUP BY c.id
ORDER BY total_amount DESC;


-- ====================
-- Запрос 2: Получение количества дочерних элементов первого уровня вложенности для категорий номенклатуры.
-- ====================
SELECT 
    oc.id AS category_id,
    oc.title AS category_name,
    COUNT(oc2.id) AS children_count
FROM orders_category oc
LEFT JOIN orders_category oc2 ON oc.id = oc2.parent_id
GROUP BY oc.id, oc.title
ORDER BY oc.id;


-- ====================
-- Запрос 3: Топ-5 самых покупаемых товаров за последний месяц.
-- ====================
SELECT
    a.title AS article_title,
    COALESCE(parent_cat.title, cat.title) AS category_level_1,
    SUM(iio.quantity) AS total_quantity_sold
FROM orders_iteminorder AS iio
JOIN orders_order AS o
    ON o.id = iio.order_id
JOIN orders_article AS a
    ON a.id = iio.article_id
JOIN orders_category AS cat
    ON cat.id = a.category_id
LEFT JOIN orders_category AS parent_cat
    ON parent_cat.id = cat.parent_id
WHERE o.created_at >= NOW() - INTERVAL '1 month'
  AND o.status IN ('paid', 'done')
GROUP BY
    a.id,
    a.title,
    category_level_1
ORDER BY total_quantity_sold DESC
LIMIT 5;
-- ====================
-- Что можно улучшить для данного запроса "ТОП-5":
-- 1) создать materialized view или закэшировать запрос (по ситуации)
-- 2) партиционировать таблицу по дате (при объемах данных от нескольких сотен тысяч записей ежемесячно)
-- или добавить индексы на дату заказа (при объемах данных до 100к\мес)
-- 3) настроить репликацию для разделения нагрузки по чтению и CUD (в дальнейшем)
-- ====================

