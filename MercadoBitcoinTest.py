# -*- coding: utf-8 -*-

import MercadoBitcoin
MB_TAPI_ID = '<API ID>'
MB_TAPI_SECRET = '<API KEY>'

mb = MercadoBitcoin.Trader(MB_TAPI_ID, MB_TAPI_SECRET)
print (mb.list_system_messages())
print (mb.list_system_messages(MercadoBitcoin.MessageType.INFO))
print (mb.list_system_messages(MercadoBitcoin.MessageType.WARNING))
print (mb.list_system_messages(MercadoBitcoin.MessageType.ERROR))
print (mb.get_account_info())
print (mb.list_orders(MercadoBitcoin.CoinPair.BRLBTC))
print (mb.list_orders(MercadoBitcoin.CoinPair.BRLLTC))
print (mb.get_order(MercadoBitcoin.CoinPair.BRLBTC,123))
print (mb.list_orderbook(MercadoBitcoin.CoinPair.BRLBTC))
print (mb.list_orderbook(MercadoBitcoin.CoinPair.BRLBTC,True))
print (mb.place_buy_order(MercadoBitcoin.CoinPair.BRLBTC,'1','0.01'))
print (mb.place_sell_order(MercadoBitcoin.CoinPair.BRLBTC,'1','99999.01'))
print (mb.cancel_order(MercadoBitcoin.CoinPair.BRLBTC, 123))
print (mb.get_withdrawal(MercadoBitcoin.Coin.BRL, 123))
print (mb.withdraw_coin_brl('50.00','123'))
print (mb.withdraw_coin_brl('50.00','123','descrição'))
print (mb.withdraw_coin_btc('asdasdasd','1','0.002'))
print (mb.withdraw_coin_btc('asdasdasd','1','0.002',True))
print (mb.withdraw_coin_btc('asdasdasd','1','0.002',True,False))
print (mb.withdraw_coin_btc('asdasdasd','1','0.002',True,False, 'descrição'))
print (mb.withdraw_coin_ltc('asdasdasd','123'))
print (mb.withdraw_coin_ltc('asdasdasd','123','descrição'))
