from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Tuple
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, dotenv_values
import os


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


def carregar_aeroportos() -> pd.DataFrame:
    response = requests.get('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat')
    content = response.content.decode('utf-8').split('\n')

    content = [c.replace('"', '').split(',') for c in content]

    airports = pd.DataFrame({'airport_name': [c[1] for c in content if len(c) == 14], 'iata': [c[4] for c in content if len(c) == 14]})

    return airports.drop(airports[airports.iata == r'\N'].index).reset_index()


def enviar_email(origem: str, destino: str, target: int, df: pd.DataFrame):
    # Carregar variáveis do .env
    load_dotenv()
    env = dotenv_values()

    SMTP_SERVER = env["SMTP_SERVER"]
    SMTP_PORT = int(env["SMTP_PORT"])
    SMTP_USER = env["SMTP_USER"]
    SMTP_PASSWORD = env["SMTP_PASSWORD"]
    EMAIL_REMETENTE = env["EMAIL_REMETENTE"]
    EMAIL_DESTINO = env["EMAIL_DESTINO"].split(',')[:-1]

    # Criar e-mail com HTML
    mensagem = MIMEMultipart()
    mensagem["From"] = EMAIL_REMETENTE
    mensagem["Subject"] = "O bot encontrou suas passagens!"

    # Corpo do e-mail em HTML
    html_tabela = ''    
    for index, row in df.iterrows():
        linha = f'<tr><td>{row['data_ida']}</td><td>{row['data_volta']}</td><td><a href="{row['url']}">R$ {row['preco']:,.2f}</a></td></tr>'
        html_tabela += linha

    arquivo_html = 'msg.html'
    with open(arquivo_html, 'r', encoding='utf-8') as file:
        html_conteudo = file.read().split('QUEBRA')
    
    corpo_email = html_conteudo[0] + f'{origem} / {destino} - Objetivo: R${target:,.2f}' + html_conteudo[1] +  html_tabela + html_conteudo[2]

    mensagem.attach(MIMEText(corpo_email, "html"))

    # Enviar e-mail
    try:
        # servidor_smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        servidor_smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        # servidor_smtp.starttls()
        servidor_smtp.login(SMTP_USER, SMTP_PASSWORD)
        for i in range(len(EMAIL_DESTINO)):
            mensagem["To"] = EMAIL_DESTINO[i]
            servidor_smtp.sendmail(EMAIL_REMETENTE, EMAIL_DESTINO[i], mensagem.as_string())
        servidor_smtp.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


def busca_passagem(aeroporto_origem: str, aeroporto_destino: str, periodo_inicio: str, periodo_fim: str, numero_dias: int, preco_target: float, output: str, modo_exibicao: str = 'oculto') -> pd.DataFrame:
    """Cria um DataFrame com os resultados das pesquisas de preços de passagens aéreas para cada uma das datas dentro do range entre periodo_inicio e periodo_fim.
    
    As informações de aeroporto precisam ser strings de 3 caracteres informando o código do aeroporto. Ex: 'GRU' (Guarulhos). E precisam correspoder ao código IATA de um aeroporto existente.

    As informações de data precisam ser strings no formato 'dd/mm/aa'. A data inicial não pode ser menor do que o dia atual.
    
    O num_dias é a duração da viagem (minimo 2 dias), e o preco_target é o valor que o usuário quer alcançar por aquela passagem (maior que 0).
    
    modo_exibição (Default = oculto) pode assumir os valores oculto ou aparente, para definir se o usuário verá o navegador sendo aberto ou não.
    
    O retorno será um dataframe pandas com as seguintes colunas: 'data_ida', 'data_volta', 'precos', 'url'."""
    
    # Verificar se as datas estão no formato correto
    periodo_inicio_dt = verificar_data(periodo_inicio)
    if not periodo_inicio_dt:
        raise Exception('Data de início do período inválida. Use o formato esperado (dd/mm/aa)')
    periodo_fim_dt = verificar_data(periodo_fim)
    if not periodo_fim_dt:
        raise Exception('Data de fim do período inválida. Use o formato esperado (dd/mm/aa)')
    if periodo_inicio_dt < datetime.now():
        raise Exception('A data inicial não pode ser menor do que o dia de hoje')
    if periodo_fim_dt < periodo_inicio_dt:
        raise Exception('A data final não pode ser menor do que a data inicial.')
    
    # data_formatada = data_atual.strftime("%d/%m/%y")

    # Verificar os códigos de aeroportos
    airports = carregar_aeroportos()

    if aeroporto_origem.upper() not in airports['iata'].values:
        raise Exception('Aeroporto de Origem não encontrado.')
    if aeroporto_destino.upper() not in airports['iata'].values:
        raise Exception('Aeroporto de Destino não encontrado.')
    
    # Verificação do numero de dias da viagem
    try:
        numero_dias = int(numero_dias)
    except:
        raise Exception('O número de dias precisa ser umm número natural maior que 1.')
    if numero_dias < 2:
        raise Exception('O número de dias da viagem deve ser de pelo menos 2.')
    
    # Verificação do preco target
    if not (isinstance(preco_target, float) or isinstance(preco_target, int)) or preco_target <= 0:
        raise Exception('O preço target precisa ser um número maior que 0.')
    
    # Verificação do modo de exibição
    if modo_exibicao == 'oculto':
        modo_exibicao = True
    elif modo_exibicao == 'aparente':
        modo_exibicao == False
    else:
        raise Exception('O modo de exibição deve ser "oculto" ou "aparente".')
    
    # Criar sequencia das datas que serão pesquisadas
    data_atual = periodo_inicio_dt
    data_final = periodo_fim_dt + timedelta(days=1)
    datas_pesquisa = []

    while data_atual < data_final:
        datas_pesquisa.append((data_atual.strftime("%d/%m/%y"), (data_atual + timedelta(days=numero_dias-1)).strftime("%d/%m/%y")))
        datas_pesquisa.append((data_atual.strftime("%d/%m/%y"), (data_atual + timedelta(days=numero_dias)).strftime("%d/%m/%y")))
        datas_pesquisa.append((data_atual.strftime("%d/%m/%y"), (data_atual + timedelta(days=numero_dias+1)).strftime("%d/%m/%y")))
        data_atual += timedelta(days=1)
    
    # Realizar as pesquisas e armazená-las em um dataframe
    resultados = pd.DataFrame(columns=['data_ida', 'data_volta', 'preco', 'url'])

    for datas in datas_pesquisa:
        print(f'Pesquisando nas datas: {datas[0]} - {datas[1]} para {output}')
        result = pesquisa(aeroporto_origem.upper(), aeroporto_destino.upper(), datas[0], datas[1])
        df = pd.DataFrame({'data_ida': datas[0], 'data_volta': datas[1], 'preco': result[0], 'url': result[1]})
        df = df.drop(df[df.preco > preco_target+(preco_target*0.1)].index).reset_index()
        resultados = pd.concat([resultados, df], ignore_index=True)
    
    if len(resultados) > 0:
        resultados.to_csv(f'{output}.csv', index=False)
        enviar_email(aeroporto_origem, aeroporto_destino, preco_target, resultados)
        return False
    else:
        print(f'Nada foi encontrado para {output}.')
        return True


if __name__ == '__main__':
    hora_atual = datetime.now()
    proxima_execucao = hora_atual
    
    # Habilitar as pesquisas
    petrolina = True
    suica = True

    while True:
        if hora_atual >= proxima_execucao:
            print(f'Iniciando pesquisa às: {hora_atual.strftime("%d/%m/%Y, %H:%M:%S")}')
            if petrolina:
               petrolina = busca_passagem(aeroporto_origem='PNZ', aeroporto_destino='GRU', periodo_inicio='15/12/25', periodo_fim='23/12/25',numero_dias= 40, preco_target=700, output='petrolina')
            if suica:
                suica = busca_passagem(aeroporto_origem='GRU', aeroporto_destino='ZRH', periodo_inicio='28/11/25', periodo_fim='01/12/25',numero_dias= 13, preco_target=3600, output='suica')
        
            proxima_execucao = hora_atual + timedelta(hours=1)

        hora_atual = datetime.now()
        
        # Se já encontrou os preços encerra a execução
        if not petrolina and not suica:
            break
        