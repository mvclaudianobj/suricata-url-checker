# Suricata URL Checker - README

Descrição

O Suricata URL Checker é um script Python desenvolvido para processar arquivos .rules do Suricata, extrair URLs das regras e verificar o status de cada URL usando Requests ou Selenium com ChromeDriver. O script registra o código de status HTTP e uma breve descrição para cada URL verificada. Ele organiza os resultados em arquivos distintos:

    Analytics.txt: Contém URLs que retornaram código de status diferente de 200 (erros).
    Analytics_200.txt: Contém URLs que retornaram código de status 200 (sucesso).

Além disso, o script evita navegar em URLs repetidas e grava o SID da regra associada no arquivo de resultado e captura capturas de tela dos sites acessados.

## Funcionalidades

- Verifica URLs extraídas de arquivos .rules.
- Usa requests para verificação rápida.
- Usa selenium para acessar sites que requerem renderização JavaScript.
- Salva os resultados em arquivos de texto.
- Captura capturas de tela dos sites abertos no Chrome.
- Suporta modo de depuração para visualização em tempo real dos resultados.
- Permite navegação em modo incógnito.

## Pré-requisitos
1. Instalação de dependências

Este projeto requer Python 3.x. Para instalar as dependências necessárias, siga os passos abaixo.
2. Clonar o repositório

Baixe ou clone o repositório em sua máquina:

git clone https://github.com/mvclaudiano/suricata-url-checker.git
cd suricata-url-checker

3. Instalar as bibliotecas Python

Certifique-se de que você tenha o pip instalado e execute o seguinte comando para instalar as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

O arquivo requirements.txt deve conter as seguintes dependências:

requests
selenium
webdriver-manager

4. Instalar o Chrome e ChromeDriver

Para usar o Selenium, você precisa instalar o Google Chrome e o ChromeDriver correspondente. O ChromeDriver será automaticamente gerenciado pela biblioteca webdriver-manager.

    Para instalar o Chrome, faça o download no site oficial: Download Google Chrome.
    ChromeDriver será gerenciado automaticamente pelo script via webdriver-manager.

5. Estrutura de Diretórios

Certifique-se de ter as seguintes pastas no diretório do projeto:

rules/    # Coloque seus arquivos .rules aqui
result/   # A pasta 'result' será criada automaticamente para armazenar os resultados

## Chrome Driver Downloads
https://chromedriver.storage.googleapis.com/index.html

## Como Usar
1. Adicionar Regras Suricata

Coloque seus arquivos .rules na pasta rules/. Esses arquivos contêm as regras do Suricata, e o script extrairá as URLs a partir das regras que contêm o campo reference:url.
2. Executar o Script

Para executar o script, use o comando abaixo. O script processará todas as regras na pasta rules e gravará os resultados na pasta result.

```bash
python suricata_url_checker.py
```

3. Opções de Execução

O script possui duas opções importantes:

    use_selenium (True/False): Define se o Selenium será utilizado para navegar pelas URLs.
    debug_mode (True/False): Exibe o progresso da verificação em tempo real na tela.

Exemplo com Requests:

Para executar o script usando apenas Requests:

```bash
python suricata_url_checker.py
```

Exemplo com Selenium:

Para executar o script usando Selenium com ChromeDriver:

```bash
python suricata_url_checker.py --use_selenium True
```

Exemplo com Debug Mode:

Para exibir o progresso em tempo real (modo debug):

```bash
python suricata_url_checker.py --debug_mode True
```

4. Saída

    result/result_nome_arquivo.rules.txt: Arquivo com o status de cada URL verificada.
    Analytics.txt: URLs que retornaram um código de status diferente de 200.
    Analytics_200.txt: URLs que retornaram o código de status 200.
    processed_urls.txt: Lista de URLs já processadas para evitar navegação repetida.

Parâmetros

O script pode ser personalizado com os seguintes parâmetros:

    use_selenium: Define se o Selenium será utilizado (default: False).
        Tipo: Booleano (True/False)
        Exemplo: --use_selenium True
    debug_mode: Exibe o progresso em tempo real (default: False).
        Tipo: Booleano (True/False)
        Exemplo: --debug_mode True

Estrutura de Arquivos de Saída:

    result/result_nome_arquivo.rules.txt:

SID: 9620217 - https://www.hotgirlclub.com - Código: 404, Descrição: Página Não Encontrada
SID: 9620218 - https://www.kaktuz.com - Código: 200, Descrição: Sucesso

Analytics.txt:

URLs com erro ou código diferente de 200:
SID: 9620217 - https://www.hotgirlclub.com - Código: 404, Descrição: Página Não Encontrada

Analytics_200.txt:

    URLs com código 200 Sucesso:
    SID: 9620218 - https://www.kaktuz.com - Código: 200, Descrição: Sucesso

# Atualizações 2.0

Aqui está o conteúdo atualizado do README.md com os últimos ajustes que fizemos no código:

# Verificador de URLs a partir de Regras Suricata

Este projeto consiste em um script Python que lê regras do Suricata em arquivos `.rules`, extrai URLs, verifica o status de cada URL e grava os resultados em arquivos de saída. O script pode usar tanto a biblioteca `requests` quanto o `Selenium` para realizar as verificações.

## Pré-requisitos

Antes de executar o script, você deve garantir que as seguintes bibliotecas estejam instaladas:

- `requests`
- `selenium`

Você pode instalar as bibliotecas necessárias usando o `pip`:

```bash
pip install requests selenium
```

Além disso, se você optar por usar o Selenium, o ChromeDriver deve estar instalado e disponível no seu sistema. Ele deve ser compatível com a versão do Chrome que você possui. O ChromeDriver deve estar no seu PATH ou em um diretório específico que você pode especificar no código.
Estrutura de Diretórios

A estrutura de diretórios do projeto deve ser a seguinte:

graphql

/project-directory
│
├── rules/               # Diretório que contém os arquivos .rules
│   ├── example.rules    # Exemplo de arquivo .rules
│   └── another.rules
│
├── result/              # Diretório onde os resultados serão salvos
│
├── Analytics.txt        # Arquivo para URLs que não retornam 200 Sucesso
│
├── Analytics_200.txt    # Arquivo para URLs que retornam 200 Sucesso
│
├── processed_urls.txt    # Arquivo para URLs que já foram processadas
│
└── script.py            # O script Python principal

Captura de Tela

Se a opção real_mode for ativada, o script abrirá o Google Chrome em modo incógnito, navegará para cada URL e fará uma captura de tela após 3 segundos. As capturas de tela serão salvas na pasta screenshot com um timestamp no nome do arquivo.

### Observações

Para usar o Chrome com Flatpak, o comando para abrir será:

```bash
sudo /usr/bin/flatpak run --branch=stable --arch=x86_64 --command=/app/bin/chrome --file-forwarding com.google.Chrome --incognito URL
```


Como Usar

    Coloque seus arquivos .rules no diretório rules.

    Execute o script:

    Você pode executar o script diretamente usando o Python. Use o seguinte comando:

    bash

    python script.py

    O script irá processar todos os arquivos .rules na pasta rules, verificar as URLs extraídas e gravar os resultados nos arquivos de saída.

    Parâmetros Opcionais:
        Para habilitar o modo de debug, você pode definir debug_mode = True dentro do script. Isso mostrará o resultado da navegação em tempo real no console.
        Para usar o Selenium na navegação, você pode definir use_selenium = True dentro do script. Certifique-se de que o ChromeDriver esteja instalado e no seu PATH.

Exemplo de Uso

Se você quiser rodar com os parâmetros debug_mode e use_selenium habilitados, você pode modificar o final do seu script:

python

if __name__ == "__main__":
    debug_mode = True  # Habilita o modo debug
    use_selenium = False  # Define se o Selenium será utilizado
    process_all_rules_files(debug_mode, use_selenium)

Estrutura dos Arquivos de Saída

    result/result_{nome_do_arquivo}.txt: Contém o resultado da verificação de cada URL, incluindo o SID da regra, a URL, o código de status e a descrição.
    Analytics.txt: Contém URLs que não retornaram o status 200 (Sucesso).
    Analytics_200.txt: Contém URLs que retornaram o status 200 (Sucesso).
    processed_urls.txt: Contém URLs que já foram processadas para evitar repetições em futuras execuções.

Logs de Erro

O script registra erros durante a execução no console e no arquivo processed_urls.txt

Funcionalidades Futuras (Roadmap)

    Suporte a mais navegadores no Selenium (Firefox, Edge).
    Opção de tempo limite para cada requisição ou navegação.
    Gerenciamento de proxies para navegação.

Contribuindo

Se você deseja contribuir com este projeto, fique à vontade para abrir um pull request ou relatar problemas na seção de issues.
Suporte

Se você encontrar problemas ou tiver dúvidas sobre o script, sinta-se à vontade para abrir um issue no repositório ou entrar em contato pelo email mvclaudiano@gmail.com.