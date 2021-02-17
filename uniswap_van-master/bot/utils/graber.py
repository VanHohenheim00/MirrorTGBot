from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio
from models import UniSwaps, UniLiq, Token
from datetime import datetime
from config import eths
import logging
from decimal import Decimal
from utils.live_sender import live_sender
from models import TypeOfChains



async def swaps_worker(url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2', chain=TypeOfChains.uniswap, count=1000):
    logging.info(f"Starting grabbing {chain.name}...")

    ts_swaps = ts_mints = ts_burns = int(datetime.utcnow().timestamp())
    while True:
            try:
                request = '''
            {
                swaps(
                first: '''+str(count)+''',
                orderBy: timestamp,
                orderDirection: asc,
                where: {timestamp_gt: ''' + str(int(ts_swaps)) + '''}) {
                    id
                    timestamp
                    pair {
                      token0 {
                        id
                        symbol
                        name
                        decimals
                      }
                      token1 {
                        id
                        symbol
                        name
                        decimals
                      }
                    }
                    amount0In
                    amount0Out
                    amount1In
                    amount1Out
                    amountUSD
                    to
                    sender
                    transaction {
                        id
                    }
                    pair {
                        id
                    }
                    }
                mints(
                first: '''+str(count)+''',
                orderBy: timestamp,
                orderDirection: asc,
                where: {timestamp_gt: ''' + str(int(ts_mints)) + '''}) {
                    id
                    timestamp
                    pair {
                      token0 {
                        id
                        symbol
                        name
                        decimals
                      }
                      token1 {
                        id
                        symbol
                        name
                        decimals
                      }
                    }
                    amount0
                    amount1
                    amountUSD
                    to
                    sender
                    transaction {
                        id
                    }
                    pair {
                        id
                    }
                    }
                burns(
                first: '''+str(count)+''',
                orderBy: timestamp,
                orderDirection: asc,
                where: {timestamp_gt: ''' + str(int(ts_burns)) + '''}) {
                    id
                    timestamp
                    pair {
                      token0 {
                        id
                        symbol
                        name
                        decimals
                      }
                      token1 {
                        id
                        symbol
                        name
                        decimals
                      }
                    }
                    amount0
                    amount1
                    amountUSD
                    to
                    sender
                    transaction {
                        id
                    }
                    pair {
                        id
                    }
                    }
            }'''
                query = gql(request)
                async with Client(
                        transport=AIOHTTPTransport(url=url),
                        fetch_schema_from_transport=True,
                        execute_timeout=None,
                ) as session:
                    result = await session.execute(query)
                logging.info(f"Chain: {chain.name}")
                logging.info(f"Got {len(result['swaps'])} swaps,"
                             f" {len(result['mints'])} mints,"
                             f" {len(result['burns'])} burns")
                asyncio.create_task(parse_swaps(result['swaps'], chain))
                asyncio.create_task(parse_mints_burns(result['mints'], result['burns'], chain))
                if result['swaps']:
                    ts_swaps = result['swaps'][-1]['timestamp']
                if result['mints']:
                    ts_mints = result['mints'][-1]['timestamp']
                if result['burns']:
                    ts_burns = result['burns'][-1]['timestamp']
                logging.info(f"swaps ts: {ts_swaps}")
                await asyncio.sleep(10)
            except Exception as e:
                logging.info(f"Exception in Swaps Grabber, {chain}")
                logging.error(e, exc_info=True)
                await asyncio.sleep(10)


async def parse_swaps(swaps, chain):
    logging.info(f"Parsing {len(swaps)} swaps.")
    for trans in swaps:
        token0, _ = await Token.get_or_create(address=trans['pair']['token0']['id'],
                                              symbol=trans['pair']['token0']['symbol'],
                                              name=trans['pair']['token0']['name'],
                                              decimals=trans['pair']['token0']['decimals'])
        token1, _ = await Token.get_or_create(address=trans['pair']['token1']['id'],
                                              symbol=trans['pair']['token1']['symbol'],
                                              name=trans['pair']['token1']['name'],
                                              decimals=trans['pair']['token1']['decimals'])

        am0 = max(Decimal(trans["amount0In"]), Decimal(trans["amount0Out"]))
        am1 = max(Decimal(trans["amount1In"]), Decimal(trans["amount1Out"]))

        buy = bool(float(trans['amount0In']))
        if token1.symbol in ["WETH", "WBNB", "USDT", "USDC", "BUSD", "USD", "UST"]:
            am0, am1 = am1, am0
            token0, token1 = token1, token0
            buy = not buy
        try:
            s = await UniSwaps.create(uni_id=trans['id'],
                                      tx_id=trans['transaction']['id'],
                                      buy=buy,
                                      pair=trans['pair']['id'],
                                      timestamp=int(trans['timestamp']),#datetime.now(tz=pytz.utc),#datetime.fromtimestamp(int(trans['timestamp'])),
                                      from_user=a['from'] if False and chain == TypeOfChains.uniswap and
                                                             (a := await eths.get_tx(trans['transaction']['id']))
                                                          else trans['sender'],
                                      token0=token0,
                                      token0amount=am0,
                                      token1=token1,
                                      token1amount=am1,
                                      amount_usd=Decimal(trans['amountUSD']),
                                      price_usd=Decimal(trans['amountUSD'])/am1)
            asyncio.create_task(handle_new_swap(s, chain))
        except Exception as e:
            logging.info(f"{trans['id']} already exist.")
            logging.error(e, exc_info=True)


async def parse_mints_burns(mints, burns, chain):
    logging.info(f"Parsing {len(mints)} mints, {len(burns)} burns")
    mints_and_burns = {True: mints,
                       False: burns}
    for add, transactions in mints_and_burns.items():
        for trans in transactions:
            token0, _ = await Token.get_or_create(address=trans['pair']['token0']['id'],
                                                  symbol=trans['pair']['token0']['symbol'],
                                                  name=trans['pair']['token0']['name'],
                                                  decimals=trans['pair']['token0']['decimals'])
            token1, _ = await Token.get_or_create(address=trans['pair']['token1']['id'],
                                                  symbol=trans['pair']['token1']['symbol'],
                                                  name=trans['pair']['token1']['name'],
                                                  decimals=trans['pair']['token1']['decimals'])

            am0 = Decimal(trans['amount0'])
            am1 = Decimal(trans['amount1'])
            if token1.symbol in ["WETH", "WBNB", "BUSD", "USDT", "USDC", "USD", "UST"]:
                am0, am1 = am1, am0
                token0, token1 = token1, token0
            try:
                liq = await UniLiq.create(uni_id=trans['id'],
                                          tx_id=trans['transaction']['id'],
                                          add=add,
                                          pair=trans['pair']['id'],
                                          timestamp=int(trans['timestamp']),#datetime.utcfromtimestamp(int(trans['timestamp'])),
                                          from_user=trans['to'],
                                          token0=token0,
                                          token0amount=am0,
                                          token1=token1,
                                          token1amount=am1,
                                          amount_usd=Decimal(trans['amountUSD'])/2,
                                          price_usd=Decimal(trans['amountUSD']) / am1)
                asyncio.create_task(handle_new_liq(liq, chain))
            except Exception as e:
                logging.info(f"{trans['id']} already exist.")
                logging.error(e, exc_info=True)


async def handle_new_swap(swap: UniSwaps, chain):
    asyncio.create_task(live_sender(swap, chain))


async def handle_new_liq(liq: UniLiq, chain):
    await live_sender(liq, chain)
