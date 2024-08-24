# Desafio Cientista de Dados Júnior - Prefeitura do Rio de Janeiro

## Descrição

Este projeto é uma solução para o desafio de Cientista de Dados Júnior da Prefeitura do Rio de Janeiro. A aplicação foi construída usando Python e Streamlit para visualizar e analisar dados relacionados aos chamados do serviço 1746 e feriados no Brasil em 2024.

## Funcionalidades

- **Visualização de Chamados do 1746:**

  - Quantidade de chamados abertos em uma data específica.
  - Tipo de chamado mais frequente em uma data.
  - Bairros com mais chamados, com visualização no mapa.
  - Subprefeitura com mais chamados.
  - Chamados sem bairro ou subprefeitura.
  - Chamados relacionados a grandes eventos, como Carnaval e Rock in Rio.

- **Integração com APIs:**
  - Visualização dos feriados no Brasil em 2024.
  - Análise do tempo e temperatura média em cada feriado.
  - Identificação dos feriados "mais aproveitáveis" e "não aproveitáveis" com base no clima.

## Pré-requisitos

- Python 3.12 ou superior
- Git

## Instalação

1. Clone este repositório para sua máquina local:

   ```bash
   git clone https://github.com/fredzolio/dataScientistChallengeRIO-Frederico_Zolio.git
   cd dataScientistChallengeRIO-Frederico_Zolio
   ```

2. Crie um ambiente virtual:

   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:

   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. Você precisará de uma conta no GCP do Google.
2. Ative a API do BigQuery.
3. Crie um projeto.
4. Crie uma credencial do tipo Conta de Serviço.
5. Associe uma chave de acesso a ela.
6. Baixe o JSON com sua conta de serviço.
7. Copie cada item do JSON para cada item do arquivo .streamlit/secrets.toml
8. Verifique se você retirou o .exemple do final do arquivo.

## Executando a Aplicação

1. Para iniciar o aplicativo Streamlit, execute o seguinte comando:

   ```bash
   streamlit run app.py
   ```

2. O aplicativo será aberto no navegador padrão. Se isso não acontecer, você pode acessar manualmente no endereço:

   ```
   http://localhost:8501
   ```

## Estrutura do Projeto

- `app.py`: Arquivo principal do aplicativo Streamlit.
- `scripts/`: Pasta contendo scripts auxiliares para carregamento de dados, consultas SQL e visualizações.
- `requirements.txt`: Arquivo com as dependências necessárias para rodar a aplicação.

## Configuração do Locale

O código tenta configurar o locale para `pt_BR` para uma exibição correta das datas. Se isso não for possível, ele mantém o locale padrão do sistema.

## Visualizações

O aplicativo oferece diversas formas de visualização dos dados, incluindo gráficos interativos, métricas e mapas, que facilitam a análise das informações.
