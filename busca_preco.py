from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date,datetime, timedelta
import time
import re
import pandas as pd
import win32com.client as win32
import json


# declaração de funções
def verifica_data(data: str) -> bool:
    dia = data[:2]
    mes = data[3:5]
    ano = data[-4:]

    check = False

    # meses com 31 dias
    if mes in ['01', '03', '05', '07', '08', '10', '12']:
        if int(dia) <= 31:
            check = True
    # meses com 30 dias
    elif mes in ['04', '06', '09', '11']:
        if int(dia) <= 30:
            check = True
    # fevereiro
    elif mes == '02':
        # testa se é bissexto
        if (int(ano) % 4 == 0 and int(ano) % 100 != 0) or int(ano) % 400 == 0:
            if int(dia) <= 29:
                check = True
        else:
            if int(dia) <= 28:
                check = True
    
    return check


# procurar e verificar aquivo de configuração json
verify_config = False
chaves_json = ['mode', 'navegador', 'destino', 'd_inicio', 'd_fim', 'periodo', 'p_desejado', 'mail_to']
try:
    with open('botConfig.json') as f:
        config_json = json.load(f)
        if list(config_json.keys()) == chaves_json:
            verify_config = True
except IOError:
    with open('saida.txt', 'a') as f:
        f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Arquivo de configuracao nao encontrado.')

# verificar nas configurações se o programa deve rodar em primeiro ou segundo plano
padrao_data = re.compile(r'\d{2}\/\d{2}\/\d{4}')
if verify_config and config_json['mode'] == 'primeiro':
    while True:
        # solicitar ao usuario a cidade de destino da viagem
        while True:
            destino = input('Qual a cidade de destino da viagem? ').capitalize()
            if len(destino) > 0:
                break
            else:
                print('Você precisa digitar o destino da viagem!')

        # solicitar ao ususario a data inicial de embarque
        while True:
            data_inicio = input('Qual a data inicial da pesquisa?(formato: dd/mm/aaaa) ')
            if len(re.findall(padrao_data, data_inicio)) > 0:
                if verifica_data(data_inicio):
                    d_ini = date(year=int(data_inicio[-4:]), month=int(data_inicio[3:5]), day=int(data_inicio[:2]))
                    if d_ini >= date.today():
                        break
                    else:
                        print('A data inicial deve ser maior ou igual a data de hoje. Digite novamente.')
                else:
                    print('A data digitada está no formato solicitado, porém não é uma data válida. Digite novamente.')
            else:
                print('A data digitada não está no formato esperado (dd/mm/aaaa). Digite novamente.')

        # solicitar ao usuario a data final de embarque
        while True:
            data_fim = input('Qual a data final da pesquisa?(formato: dd/mm/aaaa) ')
            if len(re.findall(padrao_data, data_fim)) > 0:
                if verifica_data(data_fim):
                    d_fim = date(year=int(data_fim[-4:]), month=int(data_fim[3:5]), day=int(data_fim[:2]))
                    if d_fim >= d_ini:
                        break
                    else:
                        print('A data final não pode ser menor do que a data inicial. Digite novamente.')
                else:
                    print('A data digitada está no formato solicitado, porém não é uma data válida. Digite novamente.')
            else:
                print('A data digitada não está no formato esperado (dd/mm/aaaa). Digite novamente.')

        # solicitar ao usuario o período da viagem em dias
        while True:
            periodo_dias = input('Digite o numero de dias da viagem? ')
            if periodo_dias.isnumeric():
                if int(periodo_dias) >= 0:
                    break
                else:
                    print('O período da viagem deve ser maior ou igual a 0')
            else:
                print('O período digitado não é válido. Digite novamente.')
        
        # solicitar ao usuario o preço desejado que ele está buscando
        while True:
            replacements = [(',', ''), ('.', ''), ('R', ''), ('$', ''), ('U', ''), ('E', '')]
            preco_desejado = input('Digite o preço desejado, usando apenas números e sem separadores. ')
            for char, replacement in replacements:
                if char in preco_desejado:
                    preco_desejado = preco_desejado.replace(char, replacement)
            if preco_desejado.isnumeric():
                break
            else:
                print('O valor digitado não é um número. Digite novamente.')
        
        print(f'Destino da Viagem: {destino}')
        print(f'Data inicial da pesquisa: {data_inicio}')
        print(f'Data final da pesquisa: {data_fim}')
        print(f'Período da viagem: {periodo_dias}')
        print(f'O preço desejado é: {preco_desejado}')

        confirmacao = ' '
        while confirmacao not in 'NS':
            confirmacao = input('Você confirma as informações inserida e quer continuar com a busca? [S/N] ').upper()
        if confirmacao == 'S':
            break

elif verify_config and config_json['mode'] == 'segundo':
    if len(config_json['destino']) == 0 or len(config_json['d_inicio']) == 0 or len(config_json['d_fim']) == 0 or len(config_json['periodo']) == 0 or len(config_json['p_desejado']) == 0:
        verify_config = False
    
    verify_input = [False] * 5
    # destino já foi verificado acima
    destino = config_json['destino']
    verify_input[0] = True
    # data inicial
    if len(re.findall(padrao_data, config_json['d_inicio'])) > 0 and verify_input[0]:
        if verifica_data(config_json['d_inicio']):
            data_inicio = config_json['d_inicio']
            d_ini = date(year=int(data_inicio[-4:]), month=int(data_inicio[3:5]), day=int(data_inicio[:2]))
            if d_ini >= date.today():
                verify_input[1] = True
    # data final
    if len(re.findall(padrao_data, config_json['d_fim'])) > 0 and verify_input[1]:
        if verifica_data(config_json['d_fim']):
            data_fim = config_json['d_fim']
            d_fim = date(year=int(data_fim[-4:]), month=int(data_fim[3:5]), day=int(data_fim[:2]))
            if d_fim >= d_ini:
                verify_input[2] = True
    # periodo da viagem
    if config_json['periodo'].isnumeric() and verify_input[2]:
        if int(config_json['periodo']) >= 0:
            periodo_dias = config_json['periodo']
            verify_input[3] = True
    # preço desejado
    if verify_input[3]:
        replacements = [(',', ''), ('.', ''), ('R', ''), ('$', ''), ('U', ''), ('E', '')]
        preco_desejado = config_json['p_desejado']
        for char, replacement in replacements:
            if char in preco_desejado:
                preco_desejado = preco_desejado.replace(char, replacement)
        if preco_desejado.isnumeric():
            verify_input[4] = True
    
    if verify_input != [True] * 5:
        verify_config = False
        with open('saida.txt', 'a') as f:
            f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Algum input necessario para a busca nao esta informado corretamente no arquivo de configuracao json')

else:
    with open('saida.txt', 'a') as f:
        f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Arquivo de configuracao nao especifica se o programa deve rodar em primeiro ou segundo plano.')

if verify_config:
    # configurações do navegador
    options_chrome = Options()
    options_chrome.add_argument('--window-size=1920,1080')
    options_chrome.add_argument('--incognito')
    if config_json['navegador'] == 'headless':
        options_chrome.add_argument('--headless')
    
    # inicialização do navegador
    chrome = webdriver.Chrome(options=options_chrome)
    chrome.maximize_window()
    chrome.implicitly_wait(5) # informa ao navegador para aguardar 5s antes de desistir de encontar um elemento na tela
    chrome.get('https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI0LTAyLTAxagcIARIDR1JVcgwIAxIIL20vMDVxdGoaIxIKMjAyNC0wMi0wOGoMCAMSCC9tLzA1cXRqcgcIARIDR1JVQAFIAXABggELCP___________wGYAQE&tfu=KgA')
    actions = ActionChains(chrome) # habilita as ações em cadeia, ex: ações de teclado

    # preencher o campo destino
    caixa_destino = chrome.find_element('xpath', '//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
    caixa_destino.clear()
    caixa_destino.send_keys(destino)
    time.sleep(1)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(1)

    # iniciar a coleta de dados