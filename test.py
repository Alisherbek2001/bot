from datetime import datetime, timedelta

from api import get_order_id_api, get_product_prices
from src.handlers.schemas import OrderResponse
from src.handlers.utils import create_facture

telegram_id = 6924384720
id = 12
response = get_order_id_api(id=id)
product_response = get_product_prices(
    tg_user_id=telegram_id)
if response.status_code == 200 and product_response.status_code == 200:
    data = OrderResponse.model_validate(response.json())
    price_data = {item['name']: {'price': item['price'],
                                 'measure': item['measure']} for item in product_response.json()}
    # data.items.append(OrderItem)
    price_data.update({"test": {"price": 121212.45, 'measure': 'kg'}})
    buf_file = create_facture(id, data, price_data)


# def get_first_and_last_day_of_current_month():
#     # Hozirgi sanani olish
#     today = datetime.today()

#     # Oyning birinchi kunini olish
#     first_day = today.replace(day=1)

#     # Oyning oxirgi kunini olish
#     # Kelgusi oydan bir kun oldin
#     next_month = first_day.replace(day=28) + timedelta(days=4)
#     last_day = next_month - timedelta(days=next_month.day)

#     # Sanalarni formatlash
#     first_day_str = first_day.strftime("%d.%m")
#     last_day_str = last_day.strftime("%d.%m.%Y")

#     return f"{first_day}-{last_day}"
