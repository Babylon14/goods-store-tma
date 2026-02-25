import httpx


class ShopAPI:
    def __init__(self, base_url: str = "http://backend:8000/api/v1"):
        self.base_url = base_url

    async def get_products(self):
        url = f"{self.base_url}/products/"

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            
            except Exception as err:
                print(f"Ошибка при запросе к API: {err}")
                return []


shop_api = ShopAPI()
            



