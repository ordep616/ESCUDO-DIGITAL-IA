"""Persistencia local de metricas permitidas pelo projeto."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent
BANCO_PATH = BASE_DIR / "data" / "escudo_digital.db"
CARACTERES_POR_TOKEN_APROXIMADO = 4

def _criar_banco(caminho: str | Path = BANCO_PATH) -> None:
    """Cria o banco e a tabela de consumo quando ainda não existem."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(caminho) as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS consumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caracteres_entrada INTEGER NOT NULL
                    CHECK (caracteres_entrada >= 0),
                tokens_aproximados INTEGER NOT NULL
                    CHECK (tokens_aproximados >= 0),
                criado_em TEXT NOT NULL
            )
            """
        )

def _inserir_consumo(
    caracteres_entrada: int,
    tokens_aproximados: int,
    caminho: str | Path = BANCO_PATH,
) -> None:
    """Insere somente métricas, sem receber ou salvar a mensagem."""
    caminho = Path(caminho)
    _criar_banco(caminho)

    with sqlite3.connect(caminho) as conexao:
        conexao.execute(
            """
            INSERT INTO consumo (
                caracteres_entrada,
                tokens_aproximados,
                criado_em
            )
            VALUES (?, ?, ?)
            """,
            (
                caracteres_entrada,
                tokens_aproximados,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

def _resumir_consumo(
    caminho: str | Path = BANCO_PATH,
) -> dict[str, int | float]:
    """Calcula totais e médias dos registros SQLite."""
    caminho = Path(caminho)

    if not caminho.exists():
        return _metricas_consumo_zeradas()

    _criar_banco(caminho)

    with sqlite3.connect(caminho) as conexao:
        resultado = conexao.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(caracteres_entrada), 0),
                COALESCE(SUM(tokens_aproximados), 0),
                COALESCE(AVG(caracteres_entrada), 0),
                COALESCE(AVG(tokens_aproximados), 0),
                COALESCE(
                    (
                        SELECT caracteres_entrada
                        FROM consumo
                        ORDER BY id DESC
                        LIMIT 1
                    ),
                    0
                ),
                COALESCE(
                    (
                        SELECT tokens_aproximados
                        FROM consumo
                        ORDER BY id DESC
                        LIMIT 1
                    ),
                    0
                )
            FROM consumo
            """
        ).fetchone()

    if resultado is None:
        return _metricas_consumo_zeradas()

    return {
        "total_chamadas": int(resultado[0]),
        "total_caracteres_entrada": int(resultado[1]),
        "total_tokens_aproximados": int(resultado[2]),
        "media_caracteres_por_chamada": round(float(resultado[3]), 2),
        "media_tokens_aproximados_por_chamada": round(
            float(resultado[4]), 2
        ),
        "ultima_entrada_caracteres": int(resultado[5]),
        "ultima_entrada_tokens_aproximados": int(resultado[6]),
    }

def _metricas_consumo_zeradas() -> dict[str, int | float]:
    return {
        "total_chamadas": 0,
        "total_caracteres_entrada": 0,
        "total_tokens_aproximados": 0,
        "media_caracteres_por_chamada": 0,
        "media_tokens_aproximados_por_chamada": 0,
        "ultima_entrada_caracteres": 0,
        "ultima_entrada_tokens_aproximados": 0,
    }




def _calcular_tokens_aproximados(total_caracteres: int) -> int:
    if total_caracteres <= 0:
        return 0

    return (total_caracteres + CARACTERES_POR_TOKEN_APROXIMADO - 1) // (
        CARACTERES_POR_TOKEN_APROXIMADO
    )




def carregar_consumo(
    caminho: str | Path = BANCO_PATH,
) -> dict[str, int | float]:
    """Carrega o resumo das métricas armazenadas no SQLite."""
    return _resumir_consumo(caminho)
    


def calcular_tamanho_entrada(texto_entrada: str) -> dict[str, int]:
    """Calcula tamanho da entrada sem retornar ou persistir seu conteudo."""
    if not isinstance(texto_entrada, str):
        raise TypeError("texto_entrada deve ser uma string")

    total_caracteres = len(texto_entrada)

    return {
        "caracteres": total_caracteres,
        "tokens_aproximados": _calcular_tokens_aproximados(total_caracteres),
    }


def registrar_consumo_basico(
    texto_entrada: str,
    caminho: str | Path = BANCO_PATH,
) -> dict[str, int | float]:
    """Registra o uso sem armazenar o conteúdo da mensagem."""
    tamanho = calcular_tamanho_entrada(texto_entrada)

    _inserir_consumo(
        tamanho["caracteres"],
        tamanho["tokens_aproximados"],
        caminho,
    )

    return _resumir_consumo(caminho)