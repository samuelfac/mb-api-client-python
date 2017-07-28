# -*- coding: utf-8 -*-

import hashlib
import hmac
import http.client
import json
import urllib
import time

from collections import OrderedDict


# Constantes
MB_TAPI_ID = '<user_tapi_id>'
MB_TAPI_SECRET = '<user_tapi_secret>'
REQUEST_HOST = 'www.mercadobitcoin.com.br'
REQUEST_PATH = '/tapi/v3/'

# Nonce
# Para obter variação de forma simples
# timestamp pode ser utilizado:
tapi_nonce = int(time.time()*1000)
#tapi_nonce = 1

# Parâmetros
params = {
    'tapi_method': 'list_orders',
    'tapi_nonce': tapi_nonce,
    'coin_pair': 'BRLBTC'
}
params = urllib.parse.urlencode(params)

# Gerar MAC
params_string = REQUEST_PATH + '?' + params
H = hmac.new(bytearray(MB_TAPI_SECRET.encode()), digestmod=hashlib.sha512)
H.update(params_string.encode())
tapi_mac = H.hexdigest()

# Gerar cabeçalho da requisição
headers = {
    'Content-type': 'application/x-www-form-urlencoded',
    'TAPI-ID': MB_TAPI_ID,
    'TAPI-MAC': tapi_mac
}

# Realizar requisição POST
conn = ''
try:
    conn = http.client.HTTPSConnection(REQUEST_HOST)
    conn.request("POST", REQUEST_PATH, params, headers)

    # Print response data to console
    response = conn.getresponse()
    response = response.read()

    # É fundamental utilizar a classe OrderedDict para preservar a ordem dos elementos
    response_json = json.loads(response, object_pairs_hook=OrderedDict)
    print ("status: %s" % response_json['status_code'])
    print(json.dumps(response_json, indent=4))
finally:
    if conn:
        conn.close()
