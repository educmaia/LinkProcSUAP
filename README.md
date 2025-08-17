# Web Scraper SUAP - Coleta de Links de Processos

Script automatizado para buscar processos no sistema SUAP do IFSP e extrair links diretos, salvando os resultados em arquivo CSV.

## Características

✅ **Robusto**: Usa seletores estáveis (ID e CSS) em vez de XPath absoluto  
✅ **Tratamento de Erros**: Continua funcionando mesmo se alguns processos não forem encontrados  
✅ **Espera Inteligente**: Aguarda elementos carregarem antes de interagir  
✅ **Logging Detalhado**: Acompanhe o progresso e identifique problemas  
✅ **Entrada JSON**: Lê automaticamente do arquivo `lista.json`  
✅ **Flexível**: Aceita listas, arquivos TXT ou CSV como entrada

## Instalação

### 1. Instalar Python (se não tiver)

```bash
# Baixe do site oficial: https://python.org
```

### 2. Instalar ChromeDriver

```bash
# Opção 1: Download manual
# Baixe de: https://chromedriver.chromium.org
# Adicione ao PATH do sistema

# Opção 2: Usando webdriver-manager (recomendado)
pip install webdriver-manager
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## Uso Básico

### Método 1: Usar o arquivo lista.json (Recomendado)

```bash
# O script já está configurado para ler do lista.json
python web_scraper_suap.py

# O navegador abrirá automaticamente
# Faça seu login no SUAP
# Pressione ENTER no terminal para continuar
```

### Método 2: Programaticamente

```python
from web_scraper_suap import SUAPScraper, carregar_processos_json

# Carregar do arquivo JSON
processos = carregar_processos_json('lista.json')

scraper = SUAPScraper()
try:
    if scraper.setup_driver():
        resultados = scraper.processar_lista(processos)
        scraper.salvar_csv(resultados)
finally:
    scraper.fechar()
```

### Método 3: Executar exemplos prontos

```bash
python exemplo_uso.py
# Escolha a opção 4 ou 5 para usar o lista.json
```

### Método 4: Teste rápido (apenas 3 processos)

```python
from web_scraper_suap import SUAPScraper, carregar_processos_json

processos = carregar_processos_json('lista.json')[:3]  # Apenas 3 para teste
scraper = SUAPScraper(headless=False)  # Ver o navegador funcionando
try:
    if scraper.setup_driver():
        resultados = scraper.processar_lista(processos)
        scraper.salvar_csv(resultados, 'teste.csv')
finally:
    scraper.fechar()
```

## Estrutura do Projeto

```
├── web_scraper_suap.py    # Script principal
├── exemplo_uso.py         # Exemplos de uso
├── lista.json            # Arquivo com números de processo (ENTRADA)
├── requirements.txt       # Dependências
├── README.md             # Este arquivo
└── processos_links.csv   # Resultado (gerado após execução)
```

## Formato do lista.json

O arquivo `lista.json` deve ter a seguinte estrutura:

```json
{
  "processos": [
    "23430.000701.2021-17",
    "23430.001200.2021-58",
    "23430.000986.2021-96"
  ]
}
```

## Arquivo de Saída

O script gera um CSV com as colunas:

- **NumeroProcesso**: Número do processo buscado
- **LinkProcesso**: Link direto ou "Não encontrado"

Exemplo:

```csv
NumeroProcesso,LinkProcesso
23430.000701.2021-17,https://suap.ifsp.edu.br/admin/processo_eletronico/processo/12345/
23430.001200.2021-58,Não encontrado
```

## Execução Passo a Passo

1. **Certifique-se que o arquivo `lista.json` existe** com seus números de processo
2. **Execute o script principal**:
   ```bash
   python web_scraper_suap.py
   ```
3. **Faça login no navegador**:
   - O navegador Chrome abrirá automaticamente
   - Navegue até o SUAP e faça seu login
   - Após estar logado, volte ao terminal
   - Pressione ENTER para continuar
4. **Acompanhe o progresso** através dos logs no terminal
5. **Verifique o resultado** no arquivo `processos_links.csv`

## 🔐 Processo de Login

O script inclui uma pausa automática para login manual:

```
🔐 FAÇA SEU LOGIN NO NAVEGADOR
============================================================
1. O navegador foi aberto com a página do SUAP
2. Faça seu login normalmente
3. Navegue até estar logado no sistema
4. Pressione ENTER aqui para continuar...
============================================================
```

## Configurações Avançadas

### Modo Headless (sem interface gráfica)

```python
scraper = SUAPScraper(headless=True)
```

### Personalizar tempo de espera

```python
# No código, altere a linha:
self.wait = WebDriverWait(self.driver, 15)  # 15 segundos
```

### Alterar intervalo entre buscas

```python
# No método processar_lista, altere:
time.sleep(2)  # 2 segundos entre cada busca
```

### Processar apenas parte da lista

```python
processos = carregar_processos_json('lista.json')
processos_parciais = processos[0:50]  # Apenas os primeiros 50
```

## Solução de Problemas

### Arquivo lista.json não encontrado

```bash
# Verifique se o arquivo existe no mesmo diretório do script
ls lista.json

# Ou crie um arquivo de exemplo:
echo '{"processos": ["23430.000701.2021-17"]}' > lista.json
```

### ChromeDriver não encontrado

```bash
# Instale o webdriver-manager
pip install webdriver-manager

# Modifique o código para usar:
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Processo não encontrado

- Verifique se o número está correto no `lista.json`
- Confirme se você tem acesso ao sistema SUAP
- Alguns processos podem estar restritos

### Timeout errors

- Aumente o tempo de espera
- Verifique sua conexão com a internet
- O servidor pode estar lento

## Boas Práticas

1. **Teste com poucos processos primeiro** (use a opção 5 do exemplo_uso.py)
2. **Use modo headless para lotes grandes**
3. **Mantenha backup do lista.json**
4. **Monitore os logs para identificar problemas**
5. **Respeite o servidor - não remova o time.sleep()**

## Exemplo Completo de Uso

```python
#!/usr/bin/env python3
from web_scraper_suap import SUAPScraper, carregar_processos_json

def main():
    # Carregar processos do JSON
    processos = carregar_processos_json('lista.json')

    if not processos:
        print("Erro: Não foi possível carregar lista.json")
        return

    print(f"Carregados {len(processos)} processos")

    # Para teste, processar apenas os primeiros 5
    processos_teste = processos[:5]

    scraper = SUAPScraper(headless=False)

    try:
        if scraper.setup_driver():
            print("Iniciando coleta...")
            resultados = scraper.processar_lista(processos_teste)
            scraper.salvar_csv(resultados, 'meus_processos.csv')
            print("Concluído! Verifique o arquivo meus_processos.csv")
    finally:
        scraper.fechar()

if __name__ == "__main__":
    main()
```

## Estatísticas do Arquivo Atual

O arquivo `lista.json` fornecido contém **458 processos** para serem processados.

## Licença

Este projeto é de uso livre para fins educacionais e de automação pessoal.
