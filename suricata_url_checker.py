import re
import requests
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from datetime import datetime  # Importa para manipulação de data

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dicionário para mapear códigos de status HTTP a descrições
status_descriptions = {
    200: "Sucesso",
    201: "Criado",
    204: "Nenhum Conteúdo",
    301: "Movido Permanentemente",
    302: "Encontrado",
    400: "Requisição Inválida",
    401: "Não Autorizado",
    403: "Proibido",
    404: "Página Não Encontrada",
    407: "Autenticação Proxy Necessária",
    500: "Erro Interno do Servidor",
    502: "Bad Gateway",
    503: "Serviço Indisponível",
    504: "Tempo Limite da Conexão Excedido",
}

# Regex para extrair URL e SID das regras Suricata
url_pattern = re.compile(r'reference:url,([^;]+);')
sid_pattern = re.compile(r'sid:(\d+);')

# Função para verificar o status do site usando Requests
def check_url_with_requests(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        description = status_descriptions.get(status_code, "Erro desconhecido")
    except requests.exceptions.RequestException as e:
        status_code = "Erro"
        description = str(e)
        logging.error(f"Erro ao acessar URL: {url}, Erro: {description}")  # Log de erro

    return status_code, description

# Função para verificar o status do site usando Selenium
def check_url_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar em modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)  # Usa o ChromeDriver instalado no sistema
    driver.get(url)
    
    # O status_code não pode ser recuperado diretamente, portanto, pode ser necessário um método alternativo
    status_code = driver.execute_script("return window.performance.getEntries()[0].responseEnd;")  # Este script pode não funcionar conforme esperado
    description = status_descriptions.get(status_code, "Erro desconhecido")
    
    driver.quit()  # Fecha o navegador
    return status_code, description

# Função para processar arquivo .rules e extrair URLs
def extract_urls_from_rules(file_input, file_output, analytics_file, analytics_200_file, processed_urls_file, debug_mode, use_selenium):
    processed_urls = set()
    
    # Carregar URLs já processadas
    if os.path.exists(processed_urls_file):
        with open(processed_urls_file, 'r') as f_processed:
            processed_urls.update(line.strip() for line in f_processed.readlines())
    
    with open(file_input, 'r') as f_in, open(file_output, 'w') as f_out, \
         open(analytics_file, 'a') as f_analytics, open(analytics_200_file, 'a') as f_analytics_200, \
         open(processed_urls_file, 'a') as f_processed:

        rules = f_in.readlines()  # Lê todas as linhas do arquivo .rules
        for rule in rules:
            url_match = url_pattern.search(rule)
            sid_match = sid_pattern.search(rule)

            if url_match and sid_match:
                url = url_match.group(1).strip()
                full_url = f"https://{url}"  # Adiciona o https:// à URL extraída
                sid = sid_match.group(1)  # Extrai o SID

                # Ignora URLs já processadas
                if full_url in processed_urls:
                    logging.info(f"URL já processada: {full_url}")
                    continue

                logging.info(f"Processando URL: {full_url} (SID: {sid})")
                
                # Verifica o status usando Requests ou Selenium
                if use_selenium:
                    status_code, description = check_url_with_selenium(full_url)
                else:
                    status_code, description = check_url_with_requests(full_url)

                # Exibe o resultado no modo debug
                if debug_mode:
                    print(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}")

                # Escreve no arquivo de resultado
                f_out.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")
                
                # Grava no Analytics.txt se o status for diferente de 200
                if status_code != 200:
                    f_analytics.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")
                else:
                    f_analytics_200.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")
                
                # Marca a URL como processada e grava no arquivo
                processed_urls.add(full_url)
                f_processed.write(f"{full_url}\n")

# Função para ler qualquer arquivo .rules do diretório 'rules' e gravar em 'result'
def process_all_rules_files(debug_mode=False, use_selenium=False):
    input_dir = 'rules'  # Diretório de entrada com os arquivos .rules
    output_dir = 'result'  # Diretório de saída para os resultados
    analytics_file = 'Analytics.txt'  # Arquivo de saída para URLs que não retornam 200 Sucesso
    analytics_200_file = 'Analytics_200.txt'  # Arquivo de saída para URLs que retornam 200 Sucesso
    processed_urls_file = 'processed_urls.txt'  # Arquivo para gravar URLs já processadas
    
    # Cria a pasta result se ela não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Limpa ou cria os arquivos Analytics.txt e Analytics_200.txt
    with open(analytics_file, 'w') as f_analytics:
        f_analytics.write("URLs com erro ou código diferente de 200:\n")
    
    with open(analytics_200_file, 'w') as f_analytics_200:
        f_analytics_200.write("URLs com código 200 Sucesso:\n")

    # Processa todos os arquivos .rules na pasta 'rules'
    files = [f for f in os.listdir(input_dir) if f.endswith('.rules')]
    if not files:
        logging.error("Nenhum arquivo .rules encontrado na pasta 'rules'.")
        return
    
    for file_input in files:
        input_path = os.path.join(input_dir, file_input)  # Caminho completo do arquivo de entrada
        output_path = os.path.join(output_dir, f"result_{file_input}.txt")  # Caminho completo do arquivo de saída
        logging.info(f"Processando {file_input}...")
        extract_urls_from_rules(input_path, output_path, analytics_file, analytics_200_file, processed_urls_file, debug_mode, use_selenium)
        logging.info(f"Resultado salvo em {output_path}")

    # Salva processed_urls.txt com a data e limpa o arquivo para a próxima execução
    current_date = datetime.now().strftime("%Y%m%d")  # Formata a data no formato YYYYMMDD
    dated_processed_file = f"processed_urls_{current_date}.txt"  # Nome do novo arquivo com a data
    
    # Renomeia o arquivo processed_urls.txt
    if os.path.exists(processed_urls_file):
        os.rename(processed_urls_file, dated_processed_file)
        logging.info(f"Arquivo de URLs processadas salvo como: {dated_processed_file}")
    
    # Limpa o arquivo original para a próxima execução
    open(processed_urls_file, 'w').close()  # Limpa o conteúdo do arquivo

# Configurações
# debug_mode = True exibe resultados na tela em tempo real
# use_selenium = True para usar o Selenium na navegação
process_all_rules_files(debug_mode=True, use_selenium=True)

print("Verificação concluída. Confira os arquivos resultantes na pasta 'result', o Analytics.txt e o Analytics_200.txt.")
