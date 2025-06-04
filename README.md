# Projeto API FastAPI para servir dados da pasta data

Este projeto se trata de uma API REST utilizando FastAPI, permitindo acessar os dados dos arquivos CSV presentes no site da [EMBRAPA](https://web.archive.org/web/20230525151939/http://vitibrasil.cnpuv.embrapa.br/index.php?).

## Como executar

1. Instale as dependências:
   ```powershell
   pip install fastapi uvicorn pandas
   ```
2. Execute a API:
   ```powershell
   uvicorn main:app --reload
   ```

Acesse a documentação interativa em: http://localhost:8000/docs

Link do repositório: https://github.com/LongDayJ/TechChallenge1

não consegui utilizar o jwt por questões de tempo, vou tentar arrumar

Caso o arquivo do vídeo não tenha conseguido abrir: https://youtu.be/3xUz6M8H318
