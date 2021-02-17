from config import bot
from models import LiveGate, UniSwaps, TypeOfChains
import decimal
import logging

# create a new context for this task
ctx = decimal.Context()

# 20 digits should be enough for everyone :D
ctx.prec = 20


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    #d1 = format(d1, 'f')
    return f"{d1:,}"


def round_to(x, to, now=0):
    a = round(x, to)
    if a == 0 and now < 20:
        return round_to(x, to+1, now+1)
    else:
        return a


async def live_sender(trans, chain):
    if isinstance(trans, UniSwaps):
        trans_type = "swap"
    else:
        return
    if trans.amount_usd < 1000:
        return
        # if trans.add == True:
        #     trans_type = "mint"
        # else:
        #     trans_type = "burn"
    # emoji = ""
    # if trans_type == "swap":
    #     emoji = ('🔴', '🟢')[trans.buy]
    # elif trans_type == "mint":
    #     emoji = "💧"
    # elif trans_type == "burn":
    #     emoji = "🩸"

    token0 = await trans.token0
    token1 = await trans.token1
    msg = ""
    price_divide = 1

    emoji_count = 0
    if 5000 <= trans.amount_usd < 10000:
        emoji_count = 1
    elif 10000 <= trans.amount_usd < 50000:
        emoji_count = 2
    elif 50000 <= trans.amount_usd < 100000:
        emoji_count = 3
    elif trans.amount_usd >= 100000:
        emoji_count = 4

    if chain == TypeOfChains.uniswap:
        trade_url = "https://app.uniswap.org/#/swap?outputCurrency="
        chain_url = "https://etherscan.io/tx/"
        chain_name = "Etherscan"
        name_of_chain = "🦄 Uniswap"
    elif chain == TypeOfChains.pancakeswap:
        trade_url = "https://exchange.pancakeswap.finance/#/swap?outputCurrency="
        chain_url = "https://bscscan.com/tx/"
        chain_name = "Bscscan"
        name_of_chain = "🥞 Pancakeswap"
    else:
        trade_url = chain_url = name_of_chain = chain_name = "None"

    msg += f"{('🐻{{emoji}} Sold', '🐂{{emoji}} Bought')[trans.buy]}" \
           f" <b>{float_to_str(round_to(trans.token1amount, 2))}</b> #{token1.symbol} for" \
           f" <b>${float_to_str(round_to(trans.token0amount, 2))}</b> {token0.symbol} " \
           f"@ ${float_to_str(round_to(trans.token0amount/trans.token1amount, 2))}\n" \
           f"<a href='{chain_url}{trans.tx_id}'>{chain_name} | {trans.tx_id[:6]}...</a>".replace('{{emoji}}',
                                                                                              '🚨'*emoji_count)
    # elif trans_type == "mint":
    #     msg += f"🐂{{emoji}} Provided Liquidity" \
    #            f" <b>{float_to_str(trans.token1amount)} {token1.symbol}</b> |" \
    #            f" <b>{float_to_str(round_to(trans.token0amount, 8))} {token0.symbol}</b>"
    #     price_divide = 2
    # elif trans_type == "burn":
    #     msg += f"Liquidity Removed" \
    #            f" <b>{float_to_str(trans.token1amount)} {token1.symbol}</b> |" \
    #            f" <b>{float_to_str(round_to(trans.token0amount, 8))} {token0.symbol}</b>"
    #    price_divide = 2
    # if chain == TypeOfChains.uniswap:
    #     trade_url = "https://app.uniswap.org/#/swap?outputCurrency="
    #     chain_url = "https://etherscan.io/tx/"
    #     name_of_chain = "🦄 Uniswap"
    # elif chain == TypeOfChains.pancakeswap:
    #     trade_url = "https://exchange.pancakeswap.finance/#/swap?outputCurrency="
    #     chain_url = "https://bscscan.com/tx/"
    #     name_of_chain = "🥞 Pancakeswap"
    # else:
    #     trade_url = chain_url = name_of_chain = "None"
    # msg += f" <code>(${trans.amount_usd:.2f})</code> on" \
    #        f" <a href='{trade_url}{token1.address}'>{name_of_chain}</a>\n\n" \
    #        f"{emoji * max(1, int(trans.amount_usd/1000))}\n\n" \
    #        f"<a href='{chain_url}{trans.tx_id}/'>See TX here</a>\n" \
    #        f"<code>@Price {float_to_str(round_to(trans.token0amount / (trans.token1amount*price_divide), 8))} {token0.symbol}" \
    #        f" (${float_to_str(round_to(trans.price_usd/price_divide, 5))})</code>\n\n"
    async for gate in LiveGate.filter(pair=trans.pair, active=True):
        try:
            await bot.send_message(gate.chat_id, msg, parse_mode='html', disable_web_page_preview=True)
        except Exception as e:
            logging.info(e)
