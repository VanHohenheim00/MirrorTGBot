import httpx
from bs4 import BeautifulSoup
import logging
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


class EtherAPI:
    session = None
    ethp_api_key = None

    def __init__(self, ethp_api_key=None):
        self.session = httpx.AsyncClient(timeout=60)
        if ethp_api_key:
            self.ethp_api_key = ethp_api_key
        else:
            self.ethp_api_key = os.getenv("ETHPLORER_API_KEY")

    async def get_tx(self, tx_id):
        endpoint = f"https://api.ethplorer.io/getTxInfo/{tx_id}"
        try:
            result = await self.__make_request(endpoint, params={"apiKey": self.ethp_api_key})
            data = result.json()
            if not data.get("error"):
                return result.json()
        except Exception as e:
            log.info("Filed to get tx data")
            log.info(e)
            return None

    async def __make_request(self, endpoint, params=None):
        return await self.session.get(endpoint, params=params)

