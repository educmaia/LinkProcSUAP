#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Web Scraping para Coleta de Links de Processos - SUAP IFSP
Automatiza a busca de processos e extrai links diretos para arquivo CSV
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SUAPScraper:
    def __init__(self, headless=False):
        """
        Inicializa o scraper com configurações do navegador

        Args:
            headless (bool): Se True, executa o navegador em modo headless
        """
        self.base_url = "https://suap.ifsp.edu.br/admin/processo_eletronico/processo/"
        self.driver = None
        self.wait = None
        self.headless = headless

    def setup_driver(self):
        """Configura e inicializa o driver do Selenium"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")

            # Inicializa o driver (assumindo ChromeDriver no PATH)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            logger.info("Driver do Selenium configurado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao configurar driver: {e}")
            return False

    def aguardar_login(self):
        """
        Abre a página de login e aguarda o usuário fazer login manualmente
        """
        if self.headless:
            logger.warning(
                "Modo headless ativo - login automático não é possível")
            return False

        try:
            # Acessar a página principal do SUAP
            logger.info("Abrindo página de login do SUAP...")
            self.driver.get("https://suap.ifsp.edu.br/")

            print("\n" + "="*60)
            print("🔐 FAÇA SEU LOGIN NO NAVEGADOR")
            print("="*60)
            print("1. O navegador foi aberto com a página do SUAP")
            print("2. Faça seu login normalmente")
            print("3. Navegue até estar logado no sistema")
            print("4. Pressione ENTER aqui para continuar...")
            print("="*60)

            # Aguardar o usuário pressionar Enter
            input("Pressione ENTER após fazer o login: ")

            logger.info("Continuando com a automação...")
            return True

        except Exception as e:
            logger.error(f"Erro durante o processo de login: {e}")
            return False

    def buscar_processo(self, numero_processo):
        """
        Busca um processo específico e retorna o link

        Args:
            numero_processo (str): Número do processo a ser buscado

        Returns:
            str: Link do processo ou "Não encontrado"
        """
        try:
            # Acessar a página de busca
            self.driver.get(self.base_url)
            logger.info(f"Buscando processo: {numero_processo}")

            # Localizar e limpar o campo de busca
            campo_busca = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchbar"))
            )
            campo_busca.clear()
            campo_busca.send_keys(numero_processo)

            # Clicar no botão de filtro
            botao_filtro = self.driver.find_element(By.ID, "button_filter")
            botao_filtro.click()

            # Aguardar a tabela de resultados aparecer
            self.wait.until(
                EC.presence_of_element_located((By.ID, "result_list"))
            )

            # Aguardar um pouco para garantir que a tabela carregou completamente
            time.sleep(2)

            # Buscar todas as linhas da tabela de resultados
            linhas = self.driver.find_elements(
                By.CSS_SELECTOR, '#result_list tbody tr')

            if not linhas:
                logger.warning(
                    f"Nenhuma linha encontrada na tabela para {numero_processo}")
                return "Não encontrado"

            logger.info(
                f"Encontradas {len(linhas)} linhas na tabela de resultados")

            # Percorrer cada linha para encontrar o processo correto
            for i, linha in enumerate(linhas, 1):
                try:
                    # Debug: mostrar estrutura da linha
                    th_elements = linha.find_elements(By.TAG_NAME, 'th')
                    td_elements = linha.find_elements(By.TAG_NAME, 'td')
                    logger.info(
                        f"Linha {i}: {len(th_elements)} th, {len(td_elements)} td")

                    # Buscar o número do processo na primeira coluna td
                    # A estrutura é: th (com link) + td (com número do processo)
                    if not td_elements:
                        logger.warning(
                            f"Linha {i}: Nenhuma coluna td encontrada")
                        continue

                    # O número do processo está na primeira coluna td
                    numero_na_tabela = td_elements[0].text.strip()

                    # Debug: mostrar todos os textos das colunas td
                    textos_td = [td.text.strip()
                                 # Primeiras 3 colunas
                                 for td in td_elements[:3]]
                    logger.info(f"Linha {i}: Textos td = {textos_td}")

                    logger.info(
                        f"Linha {i}: Comparando '{numero_na_tabela}' com '{numero_processo}'")

                    # Verificar se o número do processo corresponde
                    if numero_na_tabela == numero_processo:
                        logger.info(f"✅ Processo encontrado na linha {i}!")

                        # Buscar o link no th desta mesma linha
                        try:
                            link_elemento = linha.find_element(
                                By.CSS_SELECTOR, 'th a.icon-view')
                            link_href = link_elemento.get_attribute('href')
                            logger.info(
                                f"Link encontrado para {numero_processo}: {link_href}")
                            return link_href
                        except NoSuchElementException:
                            # Tentar seletor alternativo para o link
                            try:
                                link_elemento = linha.find_element(
                                    By.CSS_SELECTOR, 'th a[href*="/processo_eletronico/processo/"]')
                                link_href = link_elemento.get_attribute('href')
                                logger.info(
                                    f"Link encontrado (seletor alternativo) para {numero_processo}: {link_href}")
                                return link_href
                            except NoSuchElementException:
                                # Tentar qualquer link no th
                                try:
                                    link_elemento = linha.find_element(
                                        By.CSS_SELECTOR, 'th a')
                                    link_href = link_elemento.get_attribute(
                                        'href')
                                    logger.info(
                                        f"Link encontrado (genérico) para {numero_processo}: {link_href}")
                                    return link_href
                                except NoSuchElementException:
                                    logger.warning(
                                        f"Nenhum link encontrado no th da linha {i}")
                                    return "Link não encontrado na linha"

                except Exception as e:
                    logger.warning(f"Erro ao processar linha {i}: {e}")
                    continue

            # Se chegou até aqui, o processo não foi encontrado em nenhuma linha
            logger.warning(
                f"Processo {numero_processo} não encontrado em nenhuma linha da tabela")
            return "Não encontrado"

        except TimeoutException:
            logger.warning(
                f"Timeout: Processo {numero_processo} não encontrado")
            return "Não encontrado"
        except NoSuchElementException:
            logger.warning(
                f"Elemento não encontrado para processo {numero_processo}")
            return "Não encontrado"
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar {numero_processo}: {e}")
            return "Erro na busca"

    def processar_lista(self, lista_processos):
        """
        Processa uma lista de números de processo

        Args:
            lista_processos (list): Lista com números de processo

        Returns:
            list: Lista de dicionários com resultados
        """
        dados_finais = []
        total_processos = len(lista_processos)

        logger.info(f"Iniciando processamento de {total_processos} processos")

        for i, processo in enumerate(lista_processos, 1):
            logger.info(f"Processando {i}/{total_processos}: {processo}")

            link = self.buscar_processo(processo)

            dados_finais.append({
                'NumeroProcesso': processo,
                'LinkProcesso': link
            })

            # Pequena pausa entre requisições para não sobrecarregar o servidor
            time.sleep(1)

        return dados_finais

    def salvar_csv(self, dados, nome_arquivo='processos_links.csv'):
        """
        Salva os dados em arquivo CSV

        Args:
            dados (list): Lista de dicionários com os dados
            nome_arquivo (str): Nome do arquivo CSV
        """
        try:
            df = pd.DataFrame(dados)
            df.to_csv(nome_arquivo, index=False, encoding='utf-8')
            logger.info(f"Dados salvos em {nome_arquivo}")

            # Estatísticas
            total = len(dados)
            encontrados = len([d for d in dados if d['LinkProcesso'] not in [
                              'Não encontrado', 'Erro na busca']])
            logger.info(
                f"Estatísticas: {encontrados}/{total} processos encontrados")

        except Exception as e:
            logger.error(f"Erro ao salvar CSV: {e}")

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            logger.info("Navegador fechado")


def carregar_processos_json(arquivo='lista.json'):
    """
    Carrega a lista de processos do arquivo JSON

    Args:
        arquivo (str): Caminho para o arquivo JSON

    Returns:
        list: Lista de números de processo
    """
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        processos = dados.get('processos', [])
        logger.info(
            f"Carregados {len(processos)} processos do arquivo {arquivo}")
        return processos

    except FileNotFoundError:
        logger.error(f"Arquivo {arquivo} não encontrado!")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo: {e}")
        return []


def main():
    """Função principal do script"""
    # Carregar processos do arquivo lista.json
    lista_processos = carregar_processos_json('lista.json')

    if not lista_processos:
        logger.error(
            "Nenhum processo foi carregado. Verifique o arquivo lista.json")
        return

    # Inicializar o scraper
    scraper = SUAPScraper(headless=False)  # Mude para True para modo headless

    try:
        # Configurar o driver
        if not scraper.setup_driver():
            logger.error(
                "Falha ao configurar o driver. Verifique se o ChromeDriver está instalado.")
            return

        # Aguardar login do usuário
        if not scraper.aguardar_login():
            logger.error("Falha no processo de login")
            return

        # Processar a lista de processos
        resultados = scraper.processar_lista(lista_processos)

        # Salvar resultados em CSV
        scraper.salvar_csv(resultados)

    except KeyboardInterrupt:
        logger.info("Operação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro geral: {e}")
    finally:
        # Sempre fechar o navegador
        scraper.fechar()


if __name__ == "__main__":
    main()
