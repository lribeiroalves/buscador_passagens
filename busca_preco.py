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
def enviar_email(to_adrrs: str, sub: str, msg: str) -> None:
    # conectar com o servidor do email
    outlook = win32.Dispatch('outlook.application')
    email = outlook.CreateItem(0)
    # preparar mensagem do email
    email.To = to_adrrs
    email.Subject = sub
    email.HTMLBody = msg
    # enviar
    email.Send()


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


def coleta_dados(c_day: date, p: int) -> list:
    if '--headless' in options_chrome.arguments:
        # escrever a data de embarque
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input').send_keys(Keys.BACK_SPACE * 30)
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input').send_keys(f'{str(c_day.month).zfill(2)}/{str(c_day.day).zfill(2)}/{str(c_day.year)}')
        # escrever a data de retorno
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[2]/div/input').send_keys(Keys.BACK_SPACE * 30)
        data_periodo = c_day + timedelta(days=p)
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[2]/div/input').send_keys(f'{str(data_periodo.month).zfill(2)}/{str(data_periodo.day).zfill(2)}/{str(data_periodo.year)}')
        # sair do campo da data de retorno
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[2]/div/input').send_keys(Keys.TAB)
    else:
        # clicar na data de embarque para abrir o painel de seleção de datas
        chrome.find_element('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input').click()
        # redefinir para limpar os campos de data
        chrome.find_element('xpath', '//div[2]/div/div[2]/div[1]/div[2]/div[2]/button/span').click()
        # escrever a data de embarque
        chrome.find_element('xpath', '//div[2]/div/div[2]/div[1]/div[1]/div[1]/div/input').send_keys(f'{str(c_day.day).zfill(2)}/{str(c_day.month).zfill(2)}/{str(c_day.year)}')
        # escrever a data de retorno
        data_periodo = c_day + timedelta(days=p)
        chrome.find_element('xpath', '//div[2]/div/div[2]/div[1]/div[1]/div[2]/div/input').send_keys(f'{str(data_periodo.day).zfill(2)}/{str(data_periodo.month).zfill(2)}/{str(data_periodo.year)}')
        # sair do campo da data de retorno para liberar o botão de confirmar
        chrome.find_element('xpath', '//div[2]/div/div[2]/div[1]/div[1]/div[2]/div/input').send_keys(Keys.TAB)

    time.sleep(1)
    # chrome.save_screenshot(f'imagens/image{c_day.day}-{data_periodo.day}.png')

    # coletar todos os preços de passagens exibidos na página
    objects = chrome.find_elements('xpath', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div/ul/li/div/div[2]/div/div[2]/div[6]/div[1]/div[2]/span')

    lista_precos = []
    
    for el in objects:
        if '--headless' in options_chrome.arguments:
            lista_precos.append(int(el.text[2:].replace(',', ''))) if el.text[2:].replace(',', '').isnumeric() else lista_precos.append(None)
        else:
            if el.text[3:].replace('.', '').isnumeric():
                lista_precos.append(int(el.text[3:].replace('.', '')))
            else:
                lista_precos.append(None)

    return lista_precos
    

# procurar e verificar aquivo de configuração json
verify_config = False
chaves_json = ['mode', 'navegador', 'destino', 'd_inicio', 'd_fim', 'periodo', 'p_desejado', 'mail_to']
try:
    with open('botConfig.json') as f:
        config_json = json.load(f)
        if list(config_json.keys()) == chaves_json:
            verify_config = True
except IOError:
    with open('log-saida.txt', 'a') as f:
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
            if ',' in preco_desejado:
                preco_desejado = preco_desejado.split(',')[0]
            for char, replacement in replacements:
                if char in preco_desejado:
                    preco_desejado = preco_desejado.replace(char, replacement)
            if preco_desejado.isnumeric():
                break
            else:
                print('O valor digitado não é um número. Digite novamente.')
        
        print(f'\n\n\n\n\nDestino da Viagem: {destino}')
        print(f'Data inicial da pesquisa: {data_inicio}')
        print(f'Data final da pesquisa: {data_fim}')
        print(f'Período da viagem: {periodo_dias} dias')
        print(f'O preço desejado é: R${int(preco_desejado):.2f}')

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
        with open('log-saida.txt', 'a') as f:
            f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Algum input necessario para a busca nao esta informado corretamente no arquivo de configuracao json')

else:
    with open('log-saida.txt', 'a') as f:
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

    # preencher o campo destino do site 
    caixa_destino = chrome.find_element('xpath', '//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
    caixa_destino.clear()
    caixa_destino.send_keys(destino)
    time.sleep(2)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(1)

# iniciar a coleta de dados
if verify_config:
    mais_precos = 0
    counter = 1
    dic_tabela = {}
    dic_preco_desejado = {}

    if config_json['mode'] == 'primeiro':
        print(f'\n\n\n\nPreços de Passagens para {destino}:', end='\n'*2)
    
    current_day = d_ini
    dif = d_fim - current_day

    if periodo_dias == '0':
        etapas = (dif.days + 1) * 2
    else:
        etapas = (dif.days + 1) * 3
    
    if config_json['mode'] == 'primeiro':
        print('', end='\n')
        print(f'\rProgress: [{("#" * int(0)):<50}] {0:.2f}%', end='')
    
    while current_day <= d_fim:    
        # coletar os dados
        for i in [-1, 0, 1]:
            if periodo_dias == '0' and i == -1:
                continue
            
            precos_dia = coleta_dados(current_day, int(periodo_dias) + i)
            
            lista_preco_desejado = []
            for preco_temp in precos_dia:
                if preco_temp != None and preco_temp <= int(preco_desejado):
                    lista_preco_desejado.append(preco_temp)
            if len(lista_preco_desejado) > 0:
                lista_preco_desejado = list(set(lista_preco_desejado))
                dic_preco_desejado[f'{current_day.day}/{current_day.month}/{current_day.year} - {int(periodo_dias) + i} dias'] = lista_preco_desejado
            
            if len(precos_dia) > mais_precos:
                mais_precos = len(precos_dia)
            
            dic_tabela[f'{current_day.day}/{current_day.month}/{current_day.year} - {int(periodo_dias) + i} dias'] = precos_dia
            
            # printar a barra de progresso
            if config_json['mode'] == 'primeiro':
                print(f'\rProgress: [{("#" * int(50 * counter/etapas)):<50}] {counter/etapas * 100:.2f}%', end='')
            counter += 1
            
        # avançar para o próximo dia
        current_day += timedelta(days=1)
    chrome.close()
    
# tratar os dados coletados
if verify_config:
    # deixar o dicionario inteiro com o mesmo tamanho para poder criar o DataFrame
    for item in dic_tabela.items():
        if len(item[1]) < mais_precos:
            for c in range(mais_precos - len(item[1])):
                item[1].append(None)

    # construir o DataFrame e exportar a tabela
    tabela_precos = pd.DataFrame(dic_tabela)
    if config_json['mode'] == 'primeiro':
        tabela_precos.to_excel('tabela_precos.xlsx')
    
# analisar os dados
if verify_config:
    menor_preco = {}
    for item in tabela_precos.min().items():
        if item[1] == tabela_precos.min().min():
            item_data = str(item[0][:9]).split('/')
            item_data = date(int(item_data[2]), int(item_data[1]), int(item_data[0]))
            item_retorno = str(item[0]).split(' - ')
            item_retorno = item_data + timedelta(days=int(item_retorno[1][0]))
            menor_preco[f'{item_data:%d/%m/%Y} -- {item_retorno:%d/%m/%Y}'] = f'R${item[1]:.2f}'

# exibir ou enviar os dados ao usuario
if verify_config:
    if config_json['mode'] == 'primeiro':
        # exibir os dados
        print(f'\n\n\nAs seguintes datas para {destino} apresentaram preços abaixo do preço desejado:', end='\n\n')
        for k, i in dic_preco_desejado.items():
            k_data = k[:9].split('/')
            k_data = date(year=int(k_data[2]), month=int(k_data[1]), day=int(k_data[0]))
            k_retorno = k.split(' - ')
            k_retorno = k_data + timedelta(days=int(k_retorno[1][0]))
            print(f'{k_data:%d/%m/%Y} -- {k_retorno:%d/%m/%Y} --> ', end='')
            for index, preco in enumerate(i):
                if index == len(i) - 1:
                    print(f'R${preco:.2f}')
                else:
                    print(f'R${preco:.2f}', end=', ')

        if len(menor_preco) > 1:
            print('\n\nOs menores preços encontrados foram:')
        else:
            print('\n\nO menor preço encontrado foi', end=' ')

        for viagem, preco in menor_preco.items():
            print(f'{preco} com ida e retorno nos dias {viagem}')

        print('', end='\n\n\n')
    elif config_json['mode'] == 'segundo':
        r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
        if r.match(config_json['mail_to']):
            # enviar e-mail
            mensagem = f"""
            <h1 style="color:red;">Buscador de Preços no Google Flights</h1>

            <p style="font-size:1.2em">Destino: <strong style="font-size:1.4em">{destino}</strong></p>
            <p style="font-size:1.2em">Primeira data de busca: <strong style="font-size:1.4em">{data_inicio}</strong> - Última data de busca: <strong style="font-size:1.4em">{data_fim}</strong></p>
            <p style="font-size:1.2em">Período da viagem: <strong style="font-size:1.4em">{periodo_dias} dias</strong></p>
            <p style="font-size:1.2em">Preço desejado: <strong style="font-size:1.4em">R${int(preco_desejado):.2f}</strong></p>

            """

            assunto = 'Bot Buscador de Preços de Passagens'
            email_to = config_json['mail_to']

            enviar_email(email_to, assunto, mensagem)
        else:
            with open('log-saida.txt', 'a') as f:
                f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Nao foi possivel enviar o e-mail pois o endereco cadastrado no arquivo de configuracao nao e um e-mail valido.')
    else:
        with open('log-saida.txt', 'a') as f:
            f.write(f'{str(datetime.now())[:19]} - Execucao encerrada. [ERRO] Nao foi possivel enviar ou exibir os dados por um problema no arquivo de configuracao.')
