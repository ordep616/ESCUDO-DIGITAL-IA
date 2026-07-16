"""Entrada e apresentação da interface de terminal."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


AVISO_SEGURANCA = (
    "Esta análise é educativa e pode cometer erros. Não clique em links, "
    "não envie senhas ou códigos e confirme a situação por um canal oficial."
)

_CLASSIFICACOES = {
    "baixo_risco": "BAIXO RISCO",
    "moderado": "RISCO MODERADO",
    "alto_risco": "ALTO RISCO",
    "informacao_insuficiente": "INFORMAÇÃO INSUFICIENTE",
}

_TEXTOS_AMIGAVEIS = {
    "urgencia": "Urgência",
    "ameaca": "Ameaça",
    "recompensa": "Promessa de recompensa",
    "pedido_de_segredo": "Pedido de segredo",
    "imitacao_de_pessoa_ou_instituicao": "Imitação de pessoa ou instituição",
    "pedido_de_senha_ou_codigo": "Pedido de senha ou código",
    "pedido_de_dados_pessoais": "Pedido de dados pessoais",
    "pedido_de_dinheiro": "Pedido de dinheiro",
    "link_desconhecido": "Link desconhecido",
    "tentativa_de_impedir_verificacao": "Tentativa de impedir verificação",
    "nao_clicar": "Não clique em links",
    "nao_responder": "Não responda à mensagem",
    "nao_enviar_dados": "Não envie dados pessoais",
    "nao_enviar_senhas_ou_codigos": "Não envie senhas ou códigos",
    "usar_canal_oficial": "Use um canal oficial",
    "confirmar_com_a_pessoa_por_outro_canal": (
        "Confirme com a pessoa por outro canal"
    ),
    "bloquear_e_denunciar": "Bloqueie e denuncie o remetente",
}


def _texto_amigavel(valor: str) -> str:
    """Converte identificadores internos em textos legíveis."""
    return _TEXTOS_AMIGAVEIS.get(valor, valor.replace("_", " ").capitalize())


def _formatar_lista(titulo: str, valores: Sequence[str]) -> list[str]:
    linhas = [f"{titulo}:"]
    if not valores:
        linhas.append("- Nenhum item identificado")
        return linhas

    linhas.extend(f"- {_texto_amigavel(valor)}" for valor in valores)
    return linhas


def texto_introducao() -> str:
    """Retorna a apresentação e o aviso exibidos antes da entrada."""
    return (
        "=== Escudo Digital IA ===\n"
        "Cole somente uma mensagem fictícia ou previamente anonimizada.\n\n"
        f"Aviso: {AVISO_SEGURANCA}"
    )


def formatar_resultado(resultado: Mapping[str, Any]) -> str:
    """Transforma uma resposta validada em texto amigável para o terminal."""
    classificacao = _CLASSIFICACOES.get(
        resultado["classificacao"],
        str(resultado["classificacao"]).replace("_", " ").upper(),
    )
    confianca = float(resultado["confianca"]) * 100

    linhas = [
        "=== Resultado da análise ===",
        f"Classificação: {classificacao}",
        f"Certeza da análise: {confianca:.0f}%",
        (
            "Essa porcentagem indica a segurança da IA sobre a classificação, "
            "não se a mensagem é confiável."
        ),
        "",
    ]
    linhas.extend(_formatar_lista("Sinais identificados", resultado["sinais"]))
    linhas.append("")
    linhas.extend(_formatar_lista("Recomendações", resultado["recomendacoes"]))
    linhas.extend(
        [
            "",
            "Explicação:",
            str(resultado["explicacao_simples"]).strip(),
            "",
            f"Aviso: {AVISO_SEGURANCA}",
        ]
    )
    return "\n".join(linhas)
