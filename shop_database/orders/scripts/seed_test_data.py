from decimal import Decimal
import random

from django.db import transaction

from orders.models import Article, Category, Client, ItemInOrder, Order


@transaction.atomic
def run(*args):
    """
    Заполняет БД тестовыми данными для проверки API.

    Запуск:
      python manage.py runscript seed_test_data
    """
    if Client.objects.exists() or Article.objects.exists():
        print("Тестовые данные уже существуют.")
        return

    random.seed(42)

    # 1) Клиент
    client = Client.objects.create(
        name="Test Client",
        address="123 Test Street, Test City",
    )

    # 2) Категории: 2 первого уровня и 5 второго
    top_categories = []
    for position, idx in enumerate(range(1, 3), start=1):
        top_categories.append(
            Category.objects.create(
                title=f"Top Category {idx}",
                parent=None,
                position=position,
            )
        )

    second_level_categories = []
    # распределим 5 подкатегорий по двум верхним категориям
    position_by_parent = {cat.id: 0 for cat in top_categories}
    for idx in range(1, 6):
        parent = random.choice(top_categories)
        position_by_parent[parent.id] += 1
        second_level_categories.append(
            Category.objects.create(
                title=f"Sub Category {idx}",
                parent=parent,
                position=position_by_parent[parent.id],
            )
        )

    # 3) Артикулы: ~15 штук
    articles = []
    for idx in range(1, 16):
        category = random.choice(second_level_categories)
        price = Decimal(random.randint(100, 1000)) / Decimal("10.0")
        quantity = random.randint(100, 1000)
        articles.append(
            Article.objects.create(
                title=f"Article {idx}",
                description=f"Test article #{idx} in {category.title}",
                category=category,
                price=price,
                quantity=quantity,
            )
        )

    # 4) Заказы: 10 штук
    orders = []
    for _ in range(10):
        orders.append(
            Order.objects.create(
                client=client,
                status=Order.StatusChoice.CREATED,
            )
        )

    # 5) Позиции в заказах:
    # 30 штук (по 3 на каждый заказ, уникальные артикулы)
    for order in orders:
        # Для каждого заказа выбираем 3 разных артикула
        for article in random.sample(articles, 3):
            ItemInOrder.objects.create(
                order=order,
                article=article,
                quantity=random.randint(1, 3),
                price_in_order=article.price,
            )

    print("Тестовые данные созданы.")
