import base64
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tradutor_libraille import traduzir_arquivo

app = FastAPI(
    title="LiBraille API",
    description="API de tradução de arquivos (.txt e .epub) para Braille",
    version="0.1.0",
)

# Libera o acesso para o frontend (ajustaremos a URL exata quando conectarmos o site)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "online", "servico": "LiBraille Backend API"}


@app.post("/traduzir")
async def endpoint_traduzir(
    arquivo: UploadFile = File(...),
    tabela: str = "ptbr",
):
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    extensao = Path(arquivo.filename).suffix.lower()
    if extensao not in {".txt", ".epub"}:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{extensao}' não suportado. Envie um arquivo .txt ou .epub.",
        )

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

    caminho_temporario = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as temp:
            temp.write(conteudo)
            caminho_temporario = Path(temp.name)

        resultado = traduzir_arquivo(caminho_livro=caminho_temporario, tabela=tabela)

        binario_base64 = base64.b64encode(resultado["bytes_binario"]).decode("utf-8")
        nome_saida = f"{Path(arquivo.filename).stem}.bin"

        return {
            "nome_arquivo_original": arquivo.filename,
            "nome_arquivo_binario": nome_saida,
            "total_blocos": resultado["total_blocos"],
            "total_caracteres_braille": resultado["total_caracteres_braille"],
            "texto_braille": resultado["texto_braille"],
            "binario_base64": binario_base64,
        }

    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro interno na tradução: {str(erro)}")
    finally:
        if caminho_temporario and caminho_temporario.exists():
            caminho_temporario.unlink()