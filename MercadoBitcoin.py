# -*- coding: utf-8 -*-

import hashlib
import hmac
import http.client
import json
import urllib
import time
from enum import Enum
from collections import OrderedDict

REQUEST_HOST = 'www.mercadobitcoin.com.br'
REQUEST_PATH = '/tapi/v3/'

class MessageType(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

class CoinPair(Enum):
    BRLBTC = 'BRLBTC'
    BRLLTC = 'BRLLTC'

class OrderType(Enum):
    BUY = 'buy'
    SELL = 'sell'

class Coin(Enum):
    BRL = 'BRL'
    BTC = 'BTC'
    LTC = 'LTC'

class Trader():
    '''API de Negociações v3
MERCADO BITCOIN

Essa página é direcionada a desenvolvedores de software que desejem operar no Mercado Bitcoin de forma automatizada. A documentação abaixo descreve, com exemplos, como utilizar a interface de negociações (também chamada de TAPI, acrônimo de Trade API). 

Em caso de dúvidas nos termos consulte o Glossário (https://www.mercadobitcoin.com.br/trade-api/#glossário) ou entre em contato com o nosso Suporte (https://www.mercadobitcoin.com.br/suporte/).'''
    
    def __init__(self, MB_TAPI_ID, MB_TAPI_SECRET):
        self.MB_TAPI_ID = MB_TAPI_ID
        self.MB_TAPI_SECRET = MB_TAPI_SECRET

    def __post(self, method, params, nomeRetorno = ''):
        params['tapi_method'] = method
        # Nonce
        # Para obter variação de forma simples
        # timestamp pode ser utilizado:
        tapi_nonce = int(time.time()*1000)
        #tapi_nonce = 1
        params['tapi_nonce'] = tapi_nonce
        params = urllib.parse.urlencode(params)

        # Gerar MAC
        params_string = REQUEST_PATH + '?' + params
        H = hmac.new(bytearray(self.MB_TAPI_SECRET.encode()), digestmod=hashlib.sha512)
        H.update(params_string.encode())
        tapi_mac = H.hexdigest()
        
        # Gerar cabeçalho da requisição
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'TAPI-ID': self.MB_TAPI_ID,
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
            #print ("status: %s" % response_json['status_code'])
            if(response_json['status_code']!=100):
                raise ValueError(response_json['error_message'])
            #print(json.dumps(response_json, indent=4))
            if(nomeRetorno and nomeRetorno!=''):
                return json.dumps(response_json['response_data'][nomeRetorno], indent=4)
            else:
                return json.dumps(response_json['response_data'], indent=4)
        finally:
            if conn:
                conn.close()

    def list_system_messages(self, level=''):
        '''https://www.mercadobitcoin.com.br/trade-api/#list_system_messages

Método para comunicação de eventos do sistema relativos à TAPÌ, entre eles bugs, correções, manutenção programada e novas funcionalidades e versões. O conteúdo muda a medida que os eventos ocorrem. A comunicação externa, feita via Twitter e e-mail aos usuários da TAPI, continuará ocorrendo. Entretanto, essa forma permite ao desenvolvedor tratar as informações juntamente ao seus logs ou até mesmo automatizar comportamentos.
>level [opcional]: Filtro por criticidade das mensagens.
 Tipo: Classe MessageType.
        '''
        # Parâmetros
        params = {}
        if(level and level!=''):
            if(type(level)!=MessageType):
                raise ValueError('Parâmetro level inválido, utilize a classe MessageType.')
            
            params = {
                'level': level.value
            }

        return self.__post('list_system_messages', params, 'messages')
    
    def get_account_info(self):
        '''Retorna dados da conta, como saldos das moedas (Real, Bitcoin e Litecoin), saldos considerando retenção em ordens abertas, quantidades de ordens abertas por moeda digital, limites de saque/transferências das moedas.'''
        # Parâmetros
        params = {}
        return self.__post('get_account_info', params)

    def list_orders(self, coin_pair):
        '''Retorna uma lista de até 200 ordens, de acordo com os filtros informados, ordenadas pela data de última atualização. As operações executadas de cada ordem também são retornadas. Apenas ordens que pertencem ao proprietário da chave da TAPI são retornadas. Caso nenhuma ordem seja encontrada, é retornada uma lista vazia.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair'''
        if(type(coin_pair)!=CoinPair):
            raise ValueError('Parâmetro coin_pair inválido, utilize a classe CoinPair.')
        # Parâmetros
        params = {
            'coin_pair': coin_pair.value
        }
        return self.__post('list_orders', params, 'orders')
        
    def get_order(self, coin_pair, order_id):
        '''Retorna os dados da ordem de acordo com o ID informado. Dentre os dados estão as informações das Operações executadas dessa ordem. Apenas ordens que pertencem ao proprietário da chave da TAPI pode ser consultadas. Erros específicos são retornados para os casos onde o order_id informado não seja de uma ordem válida ou pertença a outro usuário.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair'''
        if(type(coin_pair)!=CoinPair):
            raise ValueError('Parâmetro coin_pair inválido, utilize a classe CoinPair.')
        if(type(order_id)!=int):
            raise ValueError('Parâmetro order_id inválido, deve ser do tipo Inteiro.')
        # Parâmetros
        params = {
            'coin_pair': coin_pair.value,
            'order_id': order_id
        }
        return self.__post('get_order', params, 'order')
        
    def list_orderbook(self, coin_pair, full=False):
        '''Retorna informações do livro de negociações (orderbook) do Mercado Bitcoin para o par de moedas (coin_pair) informado. Diferente do método orderbook público descrito em /api/#2.2., aqui são fornecidas informações importantes para facilitar a tomada de ação de clientes TAPI e sincronia das chamadas. Dentre elas, o número da última ordem contemplada (latest_order_id) e número das ordens do livro (order_id), descritos abaixo. Importante salientar que nesse método ordens de mesmo preço não são agrupadas como feito no método público.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair
>full [opcional]: Indica quantidades de ordens retornadas no livro. Utilizar uma quantidade menor acarreta em menos carga no servidor e no cliente, assim a resposta e seu tratamento serão mais rápidos, o que pode resultar em vantagem competitiva para o cliente TAPI.
 Tipo: Booleano'''
        if(type(coin_pair)!=CoinPair):
            raise ValueError('Parâmetro coin_pair inválido, utilize a classe CoinPair.')
        # Parâmetros
        params = {
            'coin_pair': coin_pair.value,
            'full': full
        }
        return self.__post('list_orderbook', params)
    
    def __place_order(self, order_type, coin_pair, quantity, limit_price):
        if(type(coin_pair)!=CoinPair):
            raise ValueError('Parâmetro coin_pair inválido, utilize a classe CoinPair.')
        if(type(order_type)!=OrderType):
            raise ValueError('Parâmetro order_type inválido, utilize a classe OrderType.')
        
        # Parâmetros
        params = {
            'coin_pair': coin_pair.value,
            'quantity': quantity,
            'limit_price': limit_price
        }
        return self.__post('place_'+order_type.value+'_order', params, 'order')
        
    def place_buy_order(self, coin_pair, quantity, limit_price):
        '''Abre uma ordem de compra (buy ou bid) do par de moedas, quantidade de moeda digital e preço unitário limite informados. A criação contempla o processo de confrontamento da ordem com o livro de negociações. Assim, a resposta pode informar se a ordem foi executada (parcialmente ou não) imediatamente após sua criação e, assim, se segue ou não aberta e ativa no livro.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair
>quantity: Quantidade da moeda digital a comprar/vender ao preço de limit_price.
 Tipo: String
>limit_price: Preço unitário máximo de compra ou mínimo de venda.
 Tipo: String'''
        return self.__place_order(OrderType.BUY, coin_pair, quantity, limit_price)
        
    def place_sell_order(self, coin_pair, quantity, limit_price):
        '''Abre uma ordem de venda (sell ou ask) do par de moedas, quantidade de moeda digital e preço unitário limite informados. A criação contempla o processo de confrontamento da ordem com o livro de negociações. Assim, a resposta pode informar se a ordem foi executada (parcialmente ou não) imediatamente após sua criação e, assim, se segue ou não aberta e ativa no livro.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair
>quantity: Quantidade da moeda digital a comprar/vender ao preço de limit_price.
 Tipo: String
>limit_price: Preço unitário máximo de compra ou mínimo de venda.
 Tipo: String'''
        return self.__place_order(OrderType.SELL, coin_pair, quantity, limit_price)
            
    def cancel_order(self, coin_pair, order_id):
        '''Cancela uma ordem, de venda ou compra, de acordo com o ID e par de moedas informado. O retorno contempla o sucesso ou não do cancelamento, bem como os dados e status atuais da ordem. Somente ordens pertencentes ao próprio usuário podem ser canceladas.

>coin_pair: Par de moedas a ser filtrado.
 Tipo: Classe CoinPair
>order_id: Número de identificação único da ordem.
 Tipo: Inteiro'''
        if(type(coin_pair)!=CoinPair):
            raise ValueError('Parâmetro coin_pair inválido, utilize a classe CoinPair.')
        # Parâmetros
        params = {
            'coin_pair': coin_pair.value,
            'order_id': order_id
        }
        return self.__post('cancel_order', params, 'order')
            
    def get_withdrawal(self, coin, withdrawal_id):
        '''Retorna os dados de uma transferência de moeda digital (BTC, LTC) ou de um saque de Real (BRL).

>coin: Moeda a ser feita transferência/saque.
 Tipo: Classe Coin
>withdrawal_id: Número de identificação da transferência/saque, único por coin.
 Tipo: Inteiro'''
        if(type(coin)!=Coin):
            raise ValueError('Parâmetro coin inválido, utilize a classe Coin.')
        if(type(withdrawal_id)!=int):
            raise ValueError('Parâmetro withdrawal_id inválido, deve ser do tipo Inteiro.')
        # Parâmetros
        params = {
            'coin': coin.value,
            'withdrawal_id': withdrawal_id
        }
        return self.__post('get_withdrawal', params, 'order')
            
    def __withdraw_coin(self, coin, description, params):
        if(type(coin)!=Coin):
            raise ValueError('Parâmetro coin inválido, utilize a classe Coin.')

        # Parâmetros
        params['coin'] = coin.value
        if(description!=''):
            params['description'] = description
        return self.__post('withdraw_coin', params, 'order')
            
    def withdraw_coin_brl(self, quantity, account_ref, description = ''):
        '''Executa a transferência de moedas digitais ou saques de Real. Assim, caso o valor de coin seja BRL, então realiza um saque para a conta bancária informada. Caso o valor seja BTC ou LTC, realiza uma transação para o endereço de moeda digital informado.

IMPORTANTE: Só é permitida a transferência para destinos 'confiáveis'. A necessidade de marcar um endereço ou conta bancária como 'confiável' é uma medida de segurança. Para marcar um endereço ou conta bancária como 'confiável', é necessário ter ativa a "Autenticação em dois passos" e possuir um "PIN de segurança". Essa funcionalidade só está disponível para usuários que possuem uma chave de Trade API ativa. Configure destinos confiáveis em "Endereços Bitcoin e Litecoin" e "Contas bancárias".

>quantity: Valor bruto do saque. Os limites e taxas se aplicam conforme descrito em "comissões, prazos e limites". As taxas, quando aplicáveis, são debitadas do valor informado.
 Tipo: String
>account_ref: ID de uma conta bancária já cadastrada e marcada como confiável .
 Tipo: String
>description [opcional]: Texto para descrever a transferência ou saque.
 Tipo: String'''
        # Parâmetros
        params = {
            'quantity': quantity,
            'account_ref': account_ref
        }
        return self.__withdraw_coin(Coin.BRL, description, params)
            
    def withdraw_coin_btc(self, address, quantity, tx_fee, tx_aggregate=True, via_blockchain=False, description = ''):
        '''Executa a transferência de moedas digitais ou saques de Real. Assim, caso o valor de coin seja BRL, então realiza um saque para a conta bancária informada. Caso o valor seja BTC ou LTC, realiza uma transação para o endereço de moeda digital informado.

IMPORTANTE: Só é permitida a transferência para destinos 'confiáveis'. A necessidade de marcar um endereço ou conta bancária como 'confiável' é uma medida de segurança. Para marcar um endereço ou conta bancária como 'confiável', é necessário ter ativa a "Autenticação em dois passos" e possuir um "PIN de segurança". Essa funcionalidade só está disponível para usuários que possuem uma chave de Trade API ativa. Configure destinos confiáveis em "Endereços Bitcoin e Litecoin" e "Contas bancárias".

>address: Endereço Bitcoin marcado como confiável .
 Tipo: String
>quantity: Valor líquido da transferência.
 Tipo: String
>tx_fee: Valor da taxa paga aos mineradores para processamento da transação. O site 21.co é especializado em cálculo de taxas e possui uma API que pode ser útil.
 Tipo: String
>tx_aggregate [opcional]: transferência pode ser feita junto de outras transferências em uma mesma transação no Blockchain.
 Tipo: Booleano
>via_blockchain [opcional]: transferência para endereço no Mercado Bitcoin pode ser feita via Blockchain para gerar uma transação na rede Bitcoin.
 Tipo: Booleano
>description [opcional]: Texto para descrever a transferência ou saque.
 Tipo: String'''
        
        # Parâmetros
        params = {
            'address': address,
            'quantity': quantity,
            'tx_fee': tx_fee,
            'tx_aggregate': tx_aggregate,
            'via_blockchain': via_blockchain
        }
        return self.__withdraw_coin(Coin.BTC, description, params)
           
    def withdraw_coin_ltc(self, address, quantity, description = ''):
        '''Executa a transferência de moedas digitais ou saques de Real. Assim, caso o valor de coin seja BRL, então realiza um saque para a conta bancária informada. Caso o valor seja BTC ou LTC, realiza uma transação para o endereço de moeda digital informado.

IMPORTANTE: Só é permitida a transferência para destinos 'confiáveis'. A necessidade de marcar um endereço ou conta bancária como 'confiável' é uma medida de segurança. Para marcar um endereço ou conta bancária como 'confiável', é necessário ter ativa a "Autenticação em dois passos" e possuir um "PIN de segurança". Essa funcionalidade só está disponível para usuários que possuem uma chave de Trade API ativa. Configure destinos confiáveis em "Endereços Bitcoin e Litecoin" e "Contas bancárias".

>address: Endereço Bitcoin marcado como confiável .
 Tipo: String
>quantity: Valor líquido da transferência.
 Tipo: String
>description [opcional]: Texto para descrever a transferência ou saque.
 Tipo: String'''
        
        # Parâmetros
        params = {
            'address': address,
            'quantity': quantity
        }
        return self.__withdraw_coin(Coin.LTC, description, params)
        
