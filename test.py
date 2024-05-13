from api import get_order_id_api, get_product_prices
from src.handlers.schemas import OrderResponse
from src.handlers.utils import create_facture

telegram_id = 6924384720
id = 118
response = get_order_id_api(id=id)
product_response = get_product_prices(
    tg_user_id=telegram_id)
if response.status_code == 200 and product_response.status_code == 200:
    data = OrderResponse.model_validate(response.json())
    price_data = {item['name']: {'price': item['price'],
                                 'measure': item['measure']} for item in product_response.json()}
    buf_file = create_facture(id, data, price_data)
