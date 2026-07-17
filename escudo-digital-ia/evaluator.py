"""Avaliação dos resultados da IA nos casos fictícios."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai_service import AIServiceError, analisar_mensagem
from privacy import anonimizar_cpf_telefone
from prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2
from safety import validar_mensagem_usuario
from storage import registrar_consumo_basico
from validator import CLASSIFICACOES_PERMITIDAS, validar_resposta_ia


BASE_DIR = Path(__file__).resolve().parent
CASOS_PATH = BASE_DIR / "data" / "casos_teste.json" 
RESULTADOS_V1_PATH = BASE_DIR / "data" / "resultados_prompt_v1.json"
RESULTADOS_V2_PATH = BASE_DIR / "data" / "resultados_prompt_v2.json"
PROMPTS_DISPONIVEIS = {
    "v1": SYSTEM_PROMPT_V1,
    "v2": SYSTEM_PROMPT_V2,
}
RESULTADOS_POR_PROMPT = {
    "v1": RESULTADOS_V1_PATH,
    "v2": RESULTADOS_V2_PATH,
}

CAMPOS_OBRIGATORIOS_CASO = {
    "id",
    "mensagem",
    "classificacao_esperada",
}


def selecionar_prompt(versao_prompt: str) -> str:
    """Retorna o prompt correspondente à versão informada."""
    try:
        return PROMPTS_DISPONIVEIS[versao_prompt]
    except KeyError as erro:
        raise ValueError("versão do prompt deve ser v1 ou v2") from erro


def caminho_resultados_prompt(versao_prompt: str) -> Path:
    """Retorna o arquivo padrão de resultados para a versão do prompt."""
    try:
        return RESULTADOS_POR_PROMPT[versao_prompt]
    except KeyError as erro:
        raise ValueError("versão do prompt deve ser v1 ou v2") from erro


def filtrar_casos_por_ids(
    casos: list[dict[str, Any]],
    ids_casos: Iterable[str] | None,
) -> list[dict[str, Any]]:
    """Filtra casos por identificador preservando a ordem do arquivo."""
    if ids_casos is None:
        return casos

    ids = set(ids_casos)
    casos_filtrados = [caso for caso in casos if caso["id"] in ids]
    encontrados = {caso["id"] for caso in casos_filtrados}
    ausentes = sorted(ids - encontrados)

    if ausentes:
        raise ValueError(f"casos não encontrados: {', '.join(ausentes)}")

    return casos_filtrados


def carregar_casos(
    caminho: str | Path = CASOS_PATH,
) -> list[dict[str, Any]]:
    """Carrega e valida os casos fictícios do arquivo JSON."""
    caminho = Path(caminho)

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ValueError("arquivo de casos não encontrado") from erro
    except json.JSONDecodeError as erro:
        raise ValueError("arquivo de casos contém JSON inválido") from erro

    if not isinstance(dados, list) or not dados:
        raise ValueError("arquivo de casos deve conter uma lista não vazia")

    for indice, caso in enumerate(dados, start=1):
        if not isinstance(caso, dict):
            raise ValueError(f"caso {indice} deve ser um objeto")

        campos_ausentes = CAMPOS_OBRIGATORIOS_CASO - set(caso)

        if campos_ausentes:
            nomes = ", ".join(sorted(campos_ausentes))
            raise ValueError(
                f"caso {indice} possui campos ausentes: {nomes}"
            )

        if not isinstance(caso["id"], str) or not caso["id"].strip():
            raise ValueError(f"caso {indice} possui id inválido")

        if (
            not isinstance(caso["mensagem"], str)
            or not caso["mensagem"].strip()
        ):
            raise ValueError(f"caso {indice} possui mensagem inválida")

        if (
            caso["classificacao_esperada"]
            not in CLASSIFICACOES_PERMITIDAS
        ):
            raise ValueError(
                f"caso {indice} possui classificação esperada inválida"
            )

    return dados

def classificar_resultado(
    classificacao_esperada: str,
    classificacao_obtida: str | None,
    json_valido: bool = True,
) -> str:
    """Classifica o resultado como acerto ou tipo de erro."""
    if not json_valido:
        return "resposta_invalida"

    if classificacao_esperada not in CLASSIFICACOES_PERMITIDAS:
        raise ValueError("classificação esperada inválida")

    if classificacao_obtida not in CLASSIFICACOES_PERMITIDAS:
        return "resposta_invalida"

    if classificacao_obtida == classificacao_esperada:
        return "acerto"

    if (
        classificacao_esperada == "baixo_risco"
        and classificacao_obtida in {"moderado", "alto_risco"}
    ):
        return "falso_positivo"

    if (
        classificacao_esperada == "alto_risco"
        and classificacao_obtida == "baixo_risco"
    ):
        return "falso_negativo"

    return "erro_classificacao"
def avaliar_caso(
    caso: dict[str, Any],
    resposta_ia: Any,
) -> dict[str, Any]:
    """Compara uma resposta da IA com o resultado esperado."""
    if not isinstance(caso, dict):
        raise TypeError("caso deve ser um objeto")

    if "id" not in caso or "classificacao_esperada" not in caso:
        raise ValueError("caso incompleto")

    identificador = caso["id"]
    classificacao_esperada = caso["classificacao_esperada"]
    erros_validacao = validar_resposta_ia(resposta_ia)

    if erros_validacao:
        return {
            "id": identificador,
            "esperado": classificacao_esperada,
            "obtido": None,
            "json_valido": False,
            "resultado": "resposta_invalida",
            "erros_validacao": erros_validacao,
        }

    classificacao_obtida = resposta_ia["classificacao"]

    return {
        "id": identificador,
        "esperado": classificacao_esperada,
        "obtido": classificacao_obtida,
        "json_valido": True,
        "resultado": classificar_resultado(
            classificacao_esperada,
            classificacao_obtida,
        ),
        "erros_validacao": [],
    }


def analisar_caso_com_prompt(
    mensagem: str,
    prompt: str,
    cliente: Any = None,
) -> dict[str, Any]:
    """Analisa uma mensagem usando explicitamente o prompt informado."""
    mensagem_validada = validar_mensagem_usuario(mensagem)
    mensagem_segura = anonimizar_cpf_telefone(mensagem_validada)
    resposta_textual = analisar_mensagem(mensagem_segura, prompt, cliente)
    registrar_consumo_basico(mensagem_segura)

    try:
        resposta = json.loads(resposta_textual)
    except json.JSONDecodeError as erro:
        raise ValueError(
            "A IA retornou uma resposta que não está em JSON válido."
        ) from erro

    return resposta


def calcular_metricas(
    resultados: list[dict[str, Any]],
) -> dict[str, int | float]:
    """Calcula as métricas mínimas exigidas pelo projeto."""
    if not isinstance(resultados, list):
        raise TypeError("resultados deve ser uma lista")

    contagens = {
        "acerto": 0,
        "falso_positivo": 0,
        "falso_negativo": 0,
        "resposta_invalida": 0,
        "erro_classificacao": 0,
    }

    for indice, resultado in enumerate(resultados, start=1):
        if not isinstance(resultado, dict):
            raise ValueError(f"resultado {indice} deve ser um objeto")

        tipo = resultado.get("resultado")

        if tipo not in contagens:
            raise ValueError(
                f"resultado {indice} possui tipo de resultado inválido"
            )

        contagens[tipo] += 1

    total = len(resultados)
    acertos = contagens["acerto"]
    total_erros = total - acertos

    taxa_acerto = 0.0
    if total:
        taxa_acerto = round((acertos / total) * 100, 2)

    return {
        "total_casos": total,
        "acertos": acertos,
        "erros": total_erros,
        "falsos_positivos": contagens["falso_positivo"],
        "falsos_negativos": contagens["falso_negativo"],
        "respostas_invalidas": contagens["resposta_invalida"],
        "outros_erros": contagens["erro_classificacao"],
        "taxa_acerto": taxa_acerto,
    }

def salvar_resultados(
    resultados: list[dict[str, Any]],
    versao_prompt: str,
    caminho: str | Path | None = None,
) -> dict[str, Any]:
    """Salva métricas e resultados sem copiar as mensagens analisadas."""
    if versao_prompt not in PROMPTS_DISPONIVEIS:
        raise ValueError("versão do prompt deve ser v1 ou v2")

    metricas = calcular_metricas(resultados)
    resultados_seguros = []

    campos_permitidos = (
        "id",
        "esperado",
        "obtido",
        "json_valido",
        "resultado",
        "erros_validacao",
    )

    for resultado in resultados:
        resultado_seguro = {
            campo: resultado.get(campo)
            for campo in campos_permitidos
        }
        resultados_seguros.append(resultado_seguro)

    dados_saida = {
        "versao_prompt": versao_prompt,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "metricas": metricas,
        "resultados": resultados_seguros,
    }

    caminho = Path(caminho) if caminho is not None else caminho_resultados_prompt(
        versao_prompt
    )
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados_saida, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return dados_saida


def executar_avaliacao(
    versao_prompt: str = "v1",
    ids_casos: Iterable[str] | None = None,
    caminho_casos: str | Path = CASOS_PATH,
    caminho_resultados: str | Path | None = None,
    cliente: Any = None,
    saida: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Executa casos usando a versão de prompt selecionada."""
    prompt = selecionar_prompt(versao_prompt)
    casos = filtrar_casos_por_ids(carregar_casos(caminho_casos), ids_casos)
    resultados = []

    for numero, caso in enumerate(casos, start=1):
        saida(f"Executando {caso['id']} ({numero}/{len(casos)})...")

        try:
            resposta = analisar_caso_com_prompt(caso["mensagem"], prompt, cliente)
            resultado = avaliar_caso(caso, resposta)
        except (AIServiceError, ValueError) as erro:
            resultado = {
                "id": caso["id"],
                "esperado": caso["classificacao_esperada"],
                "obtido": None,
                "json_valido": False,
                "resultado": "resposta_invalida",
                "erros_validacao": [str(erro)],
            }

        resultados.append(resultado)

        saida(f"Esperado: {resultado['esperado']}")
        saida(f"Obtido: {resultado['obtido']}")
        saida(f"Resultado: {resultado['resultado']}\n")

    dados = salvar_resultados(
        resultados,
        versao_prompt,
        caminho_resultados,
    )

    saida("Resumo:")
    saida(json.dumps(dados["metricas"], indent=2, ensure_ascii=False))

    return dados


def executar_avaliacao_v1() -> dict[str, Any]:
    """Executa os casos usando o Prompt V1."""
    return executar_avaliacao("v1")


def executar_avaliacao_v2(
    ids_casos: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Executa os casos usando o Prompt V2."""
    return executar_avaliacao("v2", ids_casos=ids_casos)


def main(argv: list[str] | None = None) -> int:
    """Executa a avaliação pela linha de comando."""
    parser = argparse.ArgumentParser(description="Avalia os casos fictícios.")
    parser.add_argument(
        "--prompt",
        choices=sorted(PROMPTS_DISPONIVEIS),
        default="v1",
        help="versão do prompt usada na avaliação",
    )
    parser.add_argument(
        "--casos",
        nargs="*",
        help="ids específicos de casos para avaliar",
    )
    args = parser.parse_args(argv)

    executar_avaliacao(args.prompt, ids_casos=args.casos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
