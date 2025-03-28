from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from datetime import datetime
from typing import List, Tuple


def pesquisa(aeroporto_origem: str, aeroporto_destino: str, data_ida: str, data_volta: str, modo_oculto: bool = True) -> Tuple[List[int], str]:
    """Realiza uma busca no site de passagens aéreas da Google (Flights) e retorna uma lista com preços.

    As informações de aeroporto precisam ser strings de 3 caracteres informando o código do aeroporto. Ex: 'GRU' (Guarulhos).

    As informações de data precisam ser strings no formato 'dd/mm/aa'.

    O modo_oculto define se o navegador deve aparecer ou rodar em segundo plano.
    
    O retorno será uma lista de int com todos os valores encontrados para aqueles aeroportos naquelas datas e uma string com a url da pesquisa realizada."""

    # Definir opções e criar o navegador
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument("--window-size=1920,1080")
    if modo_oculto:
        options.add_argument('--headless')
    nav = webdriver.Chrome(options = options)
    nav.get('https://www.google.com/travel/flights')

    # Aeroporto de origem
    campo_aeroporto_origem = nav.find_element('xpath', '//*[@data-placeholder="De onde?"]/div/div/div/div/input')
    campo_aeroporto_origem.send_keys(Keys.BACK_SPACE * 300)
    campo_aeroporto_origem.send_keys(aeroporto_origem)
    time.sleep(1)
    lista_aeroportos = nav.find_elements('xpath', '//*[@aria-label="Informe sua origem"]/div/ul/li')
    lista_aeroportos[0].click()
    time.sleep(1)

    # Aeroporto de Destino
    campo_aeroporto_destino = nav.find_element('xpath', '//*[@data-placeholder="Para onde?"]/div/div/div/div/input')
    campo_aeroporto_destino.send_keys(Keys.BACK_SPACE * 300)
    campo_aeroporto_destino.send_keys(aeroporto_destino)
    time.sleep(1)
    lista_aeroportos = nav.find_elements('xpath', '//*[@aria-label="Digite seu destino"]/div/ul/li')
    lista_aeroportos[0].click()
    time.sleep(1)

    # Data de inicio
    campo_data_inicio = nav.find_element('xpath', '//div/input[@placeholder="Partida"]')
    campo_data_inicio.send_keys(Keys.BACK_SPACE * 300)
    campo_data_inicio.send_keys(data_ida)
    campo_data_inicio.send_keys(Keys.TAB)
    time.sleep(1)

    # Data do final
    campo_data_final = nav.find_element('xpath', '//div/input[@placeholder="Volta"]')
    campo_data_final.send_keys(Keys.BACK_SPACE * 300)
    campo_data_final.send_keys(data_volta)
    campo_data_final.send_keys(Keys.TAB)
    time.sleep(1)

    # Pesquisar
    search = nav.find_element('xpath', '//button[@aria-label="Pesquisar"]/span[text()="Pesquisar"]')
    search.click()

    time.sleep(2)

    # mostrar todos os voos
    try:
        nav.find_element('xpath', '//div[span="Mostrar mais voos"]').click()
    except:
        pass

    time.sleep(2)

    # Extrair os preços das passagens
    precos = nav.find_elements('xpath', '//div[div[contains(@aria-label, "Selecionar voo")]]/div[2]/div[1]/div[2]/div[1]/div[6]/div[1]/div[2]/span')
    precos_tratados = []
    for preco in precos:
        try:
            p = int(preco.text.replace('R$', '').replace('.', '').strip())
            precos_tratados.append(p)
        except:
            pass
    
    url = nav.current_url
    
    nav.close()

    return (precos_tratados, url)


def verificar_data(data: str) -> bool:
    try:
        # Tenta converter a string para um objeto datetime no formato dd/mm/aa
        data_convertida = datetime.strptime(data, "%d/%m/%y")
        return data_convertida
    except ValueError:
        return None


def busca_passagem(aeroporto_origem: str, aeroporto_destino: str, periodo_inicio: str, periodo_fim: str, numero_dias: int, preco_target: float, modo_exibicao: str = 'oculto') -> pd.DataFrame:
    """Cria um DataFrame com os resultados das pesquisas de preços de passagens aéreas para cada uma das datas dentro do range entre periodo_inicio e periodo_fim.
    
    As informações de aeroporto precisam ser strings de 3 caracteres informando o código do aeroporto. Ex: 'GRU' (Guarulhos).

    As informações de data precisam ser strings no formato 'dd/mm/aa'.
    
    O num_dias é a duração da viagem, e o preco_target é o valor que o usuário quer alcançar por aquela passagem.
    
    modo_exibição (Default = oculto) pode assumir os valores oculto ou aparente, para definir se o usuário verá o navegador sendo aberto ou não.
    
    O retorno será um dataframe pandas com as seguintes colunas: 'data_ida', 'data_volta', 'precos', 'url'."""
    
    # Verificar se as datas estão no formato correto
    periodo_inicio_dt = verificar_data(periodo_inicio)
    if not periodo_inicio_dt:
        raise Exception('Data de início do período inválida. Use o formato esperado (dd/mm/aa)')
    periodo_fim_dt = verificar_data(periodo_fim)
    if not periodo_fim_dt:
        raise Exception('Data de fim do período inválida. Use o formato esperado (dd/mm/aa)')
    
    # data_formatada = data_atual.strftime("%d/%m/%y")

    # Verificar os códigos de aeroportos
    
