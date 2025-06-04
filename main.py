from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os

app = FastAPI(title="API dos dados da EMBRAPA")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def listar_csvs():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

# @app.get("/arquivos", summary="Lista os arquivos CSV disponíveis")
# def get_arquivos():
#     return {"arquivos": listar_csvs()}


# @app.get("/dados/{arquivo}", summary="Retorna os dados de um arquivo CSV")
# def get_dados_arquivo(arquivo: str):
#     if not arquivo.endswith(".csv"):
#         arquivo += ".csv"
#     caminho = os.path.join(DATA_DIR, arquivo)
#     if not os.path.isfile(caminho):
#         raise HTTPException(status_code=404, detail="Arquivo não encontrado")
#     try:
#         df = pd.read_csv(caminho)
#         return JSONResponse(content=df.to_dict(orient="records"))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo: {str(e)}")


def criar_endpoint(nome_arquivo):
    rota = f"/{nome_arquivo.replace('.csv', '').lower()}"
    is_imp_exp = nome_arquivo.lower().startswith(("imp", "exp"))

    async def endpoint(
        request: Request,
        ano: str = Query(None, description="Ano desejado (ex: 2020)"),
        produto: str = Query(None, description="Filtra pelo nome do produto"),
        pais: str = Query(
            None,
            description="Filtra pelo nome do país"
            if is_imp_exp
            else "(Apenas para arquivos de importação/exportação)",
        ),
    ):
        caminho = os.path.join(DATA_DIR, nome_arquivo)
        try:
            if is_imp_exp:
                df = pd.read_csv(caminho, sep="\t")
            else:
                df = pd.read_csv(caminho, sep=";")
            filtros = {}
            if ano:
                filtros["ano"] = ano
            if produto:
                filtros["produto"] = produto
            if pais and is_imp_exp:
                filtros["pais"] = pais
            filtros.update(dict(request.query_params))

            if list(filtros.keys()) == ["anos"]:
                anos = [col for col in df.columns if col.strip().isdigit()]
                return {"anos": sorted(anos)}

            if "ano" in filtros:
                ano = filtros["ano"].strip()
                if ano in df.columns:
                    colunas_id = [
                        col for col in df.columns if not col.strip().isdigit()
                    ]
                    for col_id in colunas_id:
                        if col_id.lower() == "produto" and "produto" in filtros:
                            valor_produto = filtros["produto"].strip().lower()
                            df = df[
                                df[col_id].astype(str).str.lower().str.strip()
                                == valor_produto
                            ]

                        if nome_arquivo.lower().startswith(("imp", "exp")):
                            if col_id.lower() in ["pais", "país"] and (
                                "pais" in filtros or "país" in filtros
                            ):
                                valor_pais = (
                                    filtros.get("pais", filtros.get("país", ""))
                                    .strip()
                                    .lower()
                                )
                                df = df[
                                    df[col_id].astype(str).str.lower().str.strip()
                                    == valor_pais
                                ]
                    dados = df[colunas_id + [ano]].to_dict(orient="records")
                    return JSONResponse(content=dados)
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Ano '{ano}' não encontrado nas colunas deste arquivo.",
                    )

            if (nome_arquivo.lower().startswith(("imp", "exp"))) and (
                "pais" in filtros or "país" in filtros
            ):
                colunas_id = [col for col in df.columns if not col.strip().isdigit()]
                for col_id in colunas_id:
                    if col_id.lower() in ["pais", "país"]:
                        valor_pais = (
                            filtros.get("pais", filtros.get("país", "")).strip().lower()
                        )
                        df = df[
                            df[col_id].astype(str).str.lower().str.strip() == valor_pais
                        ]
                return JSONResponse(content=df.to_dict(orient="records"))

            for coluna, valor in filtros.items():
                if coluna in df.columns:
                    valor = valor.strip()
                    try:
                        col_serie = pd.to_numeric(df[coluna], errors="coerce")
                        mask = col_serie == float(valor)
                        if not mask.any():
                            mask = df[coluna].astype(str).str.strip() == valor
                    except ValueError:
                        mask = df[coluna].astype(str).str.strip() == valor
                    df = df[mask]
            return JSONResponse(content=df.to_dict(orient="records"))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao ler o arquivo: {str(e)}"
            )

    endpoint.__name__ = f"get_{nome_arquivo.replace('.csv', '').lower()}"
    app.get(rota, summary=f"Retorna os dados de {nome_arquivo} com filtros dinâmicos")(
        endpoint
    )


for arquivo in listar_csvs():
    criar_endpoint(arquivo)
