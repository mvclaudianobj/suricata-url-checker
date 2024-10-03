import re
import requests
import os
import logging
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import mss
import tarfile
import urllib.request
import shutil

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

# Função para limpar o conteúdo das pastas, mesmo arquivos ocultos
def clean_directory(directory):
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))  # Remove arquivos
            for name in dirs:
                os.rmdir(os.path.join(root, name))  # Remove subdiretórios vazios
        os.rmdir(directory)  # Remove o diretório principal, se estiver vazio
    except Exception as e:
        print(f"Erro ao limpar o diretório {directory}: {e}")

# Função para baixar e extrair as assinaturas, com opção de produção ou homologação
def download_and_extract_signatures(is_production=True):
    if is_production:
        url = 'http://wsutm.bluepex.com/fapp/rules0.tar.gz'
        print("Modo de Produção selecionado.")
    else:
        url = 'http://wsutm.bluepex.com/fapp_homologation/rules0.tar.gz'
        print("Modo de Homologação selecionado.")

    download_path = 'fapp_rules/rules0.tar.gz'
    extract_path = 'fapp_rules'

    # Cria o diretório fapp_rules, se não existir
    os.makedirs(extract_path, exist_ok=True)

    # Faz o download do arquivo
    print(f"Baixando assinaturas de {url}...")
    urllib.request.urlretrieve(url, download_path)

    # Extrai o arquivo tar.gz
    print("Extraindo o arquivo rules0.tar.gz...")
    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(path=extract_path)

    # Remove o arquivo tar.gz
    print("Removendo arquivo rules0.tar.gz...")
    os.remove(download_path)

# Pergunta ao usuário se deseja fazer o download das assinaturas
def ask_to_download_signatures():
    mode = input("Deseja usar o modo produção ou homologação? (p/h): ").lower()

    if mode == 'p':
        download_and_extract_signatures(is_production=True)
    elif mode == 'h':
        download_and_extract_signatures(is_production=False)
    else:
        print("Opção inválida. Nenhum download será realizado.")
        return

    # Limpa as pastas rules e rules_navigate após o download
    clean_directory('rules')
    clean_directory('rules_navigate')
    print("Pastas 'rules' e 'rules_navigate' limpas.")


# Função para listar os arquivos extraídos e perguntar qual homologar
def ask_category_to_approve():
    extracted_path = 'fapp_rules'
    homologated_path = 'rules'
    navigate_path = 'rules_navigate'

    # Lista os arquivos na pasta fapp_rules
    files = [f for f in os.listdir(extracted_path) if f.endswith('.rules')]

    if not files:
        print("Nenhum arquivo de regras encontrado na pasta 'fapp_rules'.")
        return

    # Exibe os arquivos numerados
    print("\nArquivos extraídos:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")

    # Pergunta ao usuário qual categoria deseja homologar
    try:
        choice = int(input("\nEscolha o número do arquivo que deseja homologar: "))
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
        else:
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    # Copia o arquivo homologado para a pasta 'rules'
    os.makedirs(homologated_path, exist_ok=True)
    shutil.copy(os.path.join(extracted_path, selected_file), homologated_path)
    print(f"Arquivo homologado: {selected_file} copiado para a pasta 'rules'.")

    # Copia os outros arquivos para a pasta 'rules_navigate'
    os.makedirs(navigate_path, exist_ok=True)
    for file in files:
        if file != selected_file:
            shutil.copy(os.path.join(extracted_path, file), navigate_path)
            print(f"Arquivo {file} copiado para a pasta 'rules_navigate'.")

# Função para configurar o ChromeDriver para o Selenium
def configure_selenium():
    driver_path = os.path.join('driver', 'chromedriver')  # Caminho do ChromeDriver
    
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"ChromeDriver não encontrado em: {driver_path}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome sem abrir a janela
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = ChromeService(driver_path)  # Substitua 'Service' por 'ChromeService'
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# Função para verificar o status do site usando Requests
def check_url_with_requests(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        description = status_descriptions.get(status_code, "Erro desconhecido")
    except requests.exceptions.RequestException as e:
        status_code = "Erro"
        description = str(e)
        logging.error(f"Erro ao acessar URL: {url}, Erro: {description}")

    return status_code, description

# Função para verificar o status do site usando Selenium
def check_url_with_selenium(url, driver):
    try:
        driver.get(url)
        status_code = 200  # Se carregar corretamente, assume código 200
        description = status_descriptions.get(200)
    except Exception as e:
        status_code = "Erro"
        description = str(e)
    
    return status_code, description

# Função para abrir o Chrome no modo incógnito e capturar a tela
def open_chrome_incognito(url, screenshot_dir='screenshot', use_flatpak=False, monitor_number=2):
    try:
        os.makedirs(screenshot_dir, exist_ok=True)

        # Inicia o Chrome dependendo do valor de use_flatpak
        if use_flatpak:
            process = subprocess.Popen(['/usr/bin/flatpak', 'run', '--branch=stable', '--arch=x86_64', 
                                        '--command=/app/bin/chrome', '--file-forwarding', 'com.google.Chrome', 
                                        '--incognito', url])
        else:
            process = subprocess.Popen(['google-chrome', '--incognito', url])

        time.sleep(10)  # Aguarda o carregamento da página

        # Captura a tela usando mss, selecionando o monitor especificado
        with mss.mss() as sct:
            # Obtém a lista de monitores disponíveis
            monitors = sct.monitors
            if monitor_number > len(monitors) or monitor_number < 1:
                monitor_number = 1  # Se o monitor escolhido não existir, usa o primeiro

            monitor = monitors[monitor_number]  # Seleciona o monitor
            sanitized_url = re.sub(r'\W+', '_', url)  # Remove caracteres especiais da URL para usar no nome do arquivo
            screenshot_path = os.path.join(screenshot_dir, f'screenshot_{sanitized_url}_{int(time.time())}.png')

            # Captura a tela do monitor selecionado
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=screenshot_path)

            print(f"Captura de tela salva em: {screenshot_path}")

        process.terminate()  # Fecha o Chrome
    except Exception as e:
        logging.error(f"Erro ao abrir o Chrome no modo incógnito ou capturar a tela: {e}")

# Função para processar arquivo .rules e extrair URLs
def extract_urls_from_rules(file_input, file_output, analytics_file, analytics_200_file, processed_urls_file, debug_mode, use_selenium, real_mode, use_flatpak, test_false_positives):
    processed_urls = set()

    if os.path.exists(processed_urls_file):
        with open(processed_urls_file, 'r') as f_processed:
            processed_urls.update(line.strip() for line in f_processed.readlines())

    driver = None  # Inicializando a variável 'driver' para evitar referência antes de definição

    with open(file_input, 'r') as f_in, open(file_output, 'w') as f_out, \
         open(analytics_file, 'a') as f_analytics, open(analytics_200_file, 'a') as f_analytics_200, \
         open(processed_urls_file, 'a') as f_processed:

        rules = f_in.readlines()
        for rule in rules:
            url_match = url_pattern.search(rule)
            sid_match = sid_pattern.search(rule)

            if url_match and sid_match:
                url = url_match.group(1).strip()
                full_url = f"https://{url}"
                sid = sid_match.group(1)

                if full_url in processed_urls:
                    logging.info(f"URL já processada: {full_url}")
                    continue

                logging.info(f"Processando URL: {full_url} (SID: {sid})")

                if use_selenium:
                    driver = configure_selenium()
                    status_code, description = check_url_with_selenium(full_url, driver)
                    driver.quit()
                else:
                    status_code, description = check_url_with_requests(full_url)

                if debug_mode:
                    print(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}")

                # Grava a informação no arquivo de saída
                f_out.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")

                if status_code == 200:
                    f_analytics_200.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")
                    
                    # Se o código de status for 200 e o real_mode estiver ativado, captura a tela
                    if real_mode:
                        open_chrome_incognito(full_url, use_flatpak=use_flatpak)
                else:
                    f_analytics.write(f"SID: {sid} - {full_url} - Código: {status_code}, Descrição: {description}\n")

                processed_urls.add(full_url)
                f_processed.write(f"{full_url}\n")

    # Fechar o driver se ele foi usado
    if driver is not None:
        driver.quit()

    # Se o parâmetro test_false_positives for True, faz o teste de falso positivo
    if test_false_positives:
        navigate_file = 'rules_navigate'
        analytics_error_file = 'Navigate_Error.txt'
        analytics_200_file = 'Navigate_200.txt'

        for file_input in os.listdir(navigate_file):
            if file_input.endswith('.rules'):
                input_path = os.path.join(navigate_file, file_input)
                output_path = os.path.join('result', f"result_{file_input}.txt")
                logging.info(f"Testando falso positivo em {file_input}...")

                # No teste de falso positivo, apenas utiliza requests, sem real_mode ou Selenium
                extract_urls_from_rules(input_path, output_path, analytics_error_file, analytics_200_file, processed_urls_file, debug_mode, use_selenium=False, real_mode=False, use_flatpak=use_flatpak, test_false_positives=False)

# Função para ler qualquer arquivo .rules do diretório 'rules' e gravar em 'result'
def process_all_rules_files(debug_mode=False, use_selenium=False, real_mode=False, use_flatpak=False, test_false_positives=False):
    input_dir = 'rules'
    output_dir = 'result'
    analytics_file = 'Analytics.txt'
    analytics_200_file = 'Analytics_200.txt'
    processed_urls_file = 'processed_urls.txt'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(analytics_file, 'w') as f_analytics:
        f_analytics.write("URLs com erro ou código diferente de 200:\n")
    
    with open(analytics_200_file, 'w') as f_analytics_200:
        f_analytics_200.write("URLs com código 200 Sucesso:\n")

    files = [f for f in os.listdir(input_dir) if f.endswith('.rules')]
    if not files:
        logging.error("Nenhum arquivo .rules encontrado na pasta 'rules'.")
        return
    
    for file_input in files:
        input_path = os.path.join(input_dir, file_input)
        output_path = os.path.join(output_dir, f"result_{file_input}.txt")
        logging.info(f"Processando {file_input}...")
        extract_urls_from_rules(input_path, output_path, analytics_file, analytics_200_file, processed_urls_file, debug_mode, use_selenium, real_mode, use_flatpak, test_false_positives)
        logging.info(f"Resultado salvo em {output_path}")

    current_date = datetime.now().strftime("%Y%m%d")
    dated_processed_file = f"processed_urls_{current_date}.txt"
    
    if os.path.exists(processed_urls_file):
        os.rename(processed_urls_file, dated_processed_file)
        logging.info(f"Arquivo de URLs processadas salvo como: {dated_processed_file}")
    
    open(processed_urls_file, 'w').close()

# Chama a função no início do programa
ask_to_download_signatures()
ask_category_to_approve()
# Configurações
process_all_rules_files(debug_mode=True, use_selenium=False, real_mode=True, use_flatpak=False, test_false_positives=True)

print("Verificação concluída. Confira os arquivos resultantes na pasta 'result', o Analytics.txt e o Analytics_200.txt.")
