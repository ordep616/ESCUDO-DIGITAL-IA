from __future__ import annotations

from collections.abc import Callable, MutableMapping
from typing import Any

import streamlit as st

from aprender import CLASSIFICACOES_VALIDAS, carregar_exercicios
from ai_service import AIServiceError
from main import RespostaIAInvalidaError, processar_mensagem
from storage import registrar_avaliacao


CLASSIFICACOES = {
    "baixo_risco": "Baixo risco",
    "moderado": "Risco moderado",
    "alto_risco": "Alto risco",
    "informacao_insuficiente": "Informação insuficiente",
}

DESCRICOES_CLASSIFICACAO = {
    "baixo_risco": "A mensagem não apresentou sinais fortes de golpe.",
    "moderado": "A mensagem tem pontos de atenção e deve ser verificada com cuidado.",
    "alto_risco": "A mensagem tem sinais fortes de golpe. Não envie dados, dinheiro ou códigos.",
    "informacao_insuficiente": "Não há informação suficiente para uma conclusão segura.",
}

OPCOES_CLASSIFICACAO = [
    "baixo_risco",
    "moderado",
    "alto_risco",
    "informacao_insuficiente",
]

MODOS_WEB = {"menu", "analise", "aprender", "sair"}


def _estado_get(
    estado: MutableMapping[str, Any],
    chave: str,
    padrao: Any,
) -> Any:
    return estado[chave] if chave in estado else padrao


def rotulo_classificacao(classificacao: str) -> str:
    return CLASSIFICACOES.get(classificacao, classificacao.replace("_", " "))


def descricao_classificacao(classificacao: str) -> str:
    return DESCRICOES_CLASSIFICACAO.get(
        classificacao,
        "Resultado retornado pela análise.",
    )


def formatar_confianca(confianca: float) -> tuple[str, float]:
    valor = max(0.0, min(float(confianca), 1.0))

    if valor >= 0.8:
        nivel = "Alta"
    elif valor >= 0.5:
        nivel = "Média"
    else:
        nivel = "Baixa"

    return f"{nivel} ({valor * 100:.0f}%)", valor


def preparar_estado_analise(estado: MutableMapping[str, Any]) -> None:
    if "resultado_analise" not in estado:
        estado["resultado_analise"] = None
    if "feedback_registrado" not in estado:
        estado["feedback_registrado"] = False


def preparar_estado_menu(estado: MutableMapping[str, Any]) -> None:
    if "modo_web" not in estado:
        estado["modo_web"] = "menu"


def preparar_estado_aprender(estado: MutableMapping[str, Any]) -> None:
    if "indice_exercicio" not in estado:
        estado["indice_exercicio"] = 0
    if "acertos" not in estado:
        estado["acertos"] = 0
    if "respondido" not in estado:
        estado["respondido"] = False
    if "ultimo_acerto" not in estado:
        estado["ultimo_acerto"] = None
    if "ultima_classificacao_esperada" not in estado:
        estado["ultima_classificacao_esperada"] = None


def registrar_resposta_aprender(
    estado: MutableMapping[str, Any],
    resposta: str,
    esperado: str,
) -> bool:
    if resposta not in CLASSIFICACOES_VALIDAS:
        raise ValueError("classificação informada é inválida")
    if esperado not in CLASSIFICACOES_VALIDAS:
        raise ValueError("classificação esperada é inválida")

    if _estado_get(estado, "respondido", False):
        return bool(_estado_get(estado, "ultimo_acerto", False))

    acertou = resposta == esperado

    if acertou:
        estado["acertos"] = int(_estado_get(estado, "acertos", 0)) + 1

    estado["respondido"] = True
    estado["ultimo_acerto"] = acertou
    estado["ultima_classificacao_esperada"] = esperado
    return acertou


def avancar_exercicio(estado: MutableMapping[str, Any]) -> None:
    estado["indice_exercicio"] = int(_estado_get(estado, "indice_exercicio", 0)) + 1
    estado["respondido"] = False
    estado["ultimo_acerto"] = None
    estado["ultima_classificacao_esperada"] = None


def registrar_feedback_analise(
    valor: str,
    registrador: Callable[[str], None] = registrar_avaliacao,
) -> str:
    registrador(valor)
    return "Obrigado pela avaliação. Ela foi registrada sem salvar a mensagem."


def selecionar_modo(estado: MutableMapping[str, Any], modo: str) -> None:
    if modo not in MODOS_WEB:
        raise ValueError("modo da web inválido")

    estado["modo_web"] = modo


def escrever_lista(titulo: str, itens: list[str], texto_vazio: str) -> None:
    st.write(f"**{titulo}:**")

    if itens:
        for item in itens:
            st.markdown(f"- {item}")
        return

    st.write(texto_vazio)


def renderizar_resultado_analise(resultado: dict[str, Any]) -> None:
    classificacao = resultado["classificacao"]
    texto_confianca, valor_confianca = formatar_confianca(resultado["confianca"])

    st.success("Análise concluída")

    coluna_resultado, coluna_confianca = st.columns(2)
    coluna_resultado.metric(
        "Resultado",
        rotulo_classificacao(classificacao),
    )
    coluna_confianca.metric("Certeza da análise", texto_confianca)
    st.progress(valor_confianca)
    st.caption(
        "Esta porcentagem indica o quanto a IA está segura da classificação "
        "mostrada acima. Ela não mede se a mensagem é confiável ou segura."
    )

    if classificacao == "alto_risco":
        st.error(descricao_classificacao(classificacao))
    elif classificacao == "moderado":
        st.warning(descricao_classificacao(classificacao))
    elif classificacao == "informacao_insuficiente":
        st.info(descricao_classificacao(classificacao))
    else:
        st.success(descricao_classificacao(classificacao))

    escrever_lista(
        "Sinais identificados",
        resultado["sinais"],
        "Nenhum sinal identificado.",
    )

    escrever_lista(
        "Recomendações",
        resultado["recomendacoes"],
        "Nenhuma recomendação específica.",
    )

    st.write("**Explicação:**")
    st.write(resultado["explicacao_simples"])


def renderizar_feedback_analise() -> None:
    st.write("**Esta análise foi útil?**")

    feedback_registrado = st.session_state["feedback_registrado"]
    coluna_util, coluna_nao_util = st.columns(2)

    if coluna_util.button(
        "Útil",
        key="feedback_util",
        disabled=feedback_registrado,
    ):
        try:
            st.success(registrar_feedback_analise("util"))
            st.session_state["feedback_registrado"] = True
        except Exception as erro:
            st.error(f"Não foi possível registrar a avaliação: {erro}")

    if coluna_nao_util.button(
        "Não útil",
        key="feedback_nao_util",
        disabled=feedback_registrado,
    ):
        try:
            st.success(registrar_feedback_analise("nao_util"))
            st.session_state["feedback_registrado"] = True
        except Exception as erro:
            st.error(f"Não foi possível registrar a avaliação: {erro}")

    if st.session_state["feedback_registrado"]:
        st.caption("Sua avaliação já foi registrada.")


def renderizar_aba_analise() -> None:
    st.subheader("Analisar mensagem")
    preparar_estado_analise(st.session_state)

    mensagem = st.text_area(
        "Cole uma mensagem fictícia ou previamente anonimizada:",
        height=180,
    )

    if st.button("Analisar"):
        try:
            st.session_state["resultado_analise"] = processar_mensagem(mensagem)
            st.session_state["feedback_registrado"] = False
        except (ValueError, AIServiceError, RespostaIAInvalidaError) as erro:
            st.session_state["resultado_analise"] = None
            st.session_state["feedback_registrado"] = False
            st.error(f"Não foi possível concluir a análise: {erro}")

    resultado = st.session_state["resultado_analise"]

    if resultado:
        renderizar_resultado_analise(resultado)
        renderizar_feedback_analise()


def renderizar_aba_aprender() -> None:
    st.subheader("Modo Aprender")

    exercicios = carregar_exercicios()
    preparar_estado_aprender(st.session_state)

    indice = st.session_state["indice_exercicio"]

    if indice < len(exercicios):
        exercicio = exercicios[indice]

        st.write(f"**Exercício {indice + 1}/{len(exercicios)}**")
        st.info(exercicio["mensagem"])

        resposta = st.radio(
            "Qual é a classificação?",
            OPCOES_CLASSIFICACAO,
            format_func=rotulo_classificacao,
            key=f"resposta_{indice}",
        )

        if st.button("Responder", disabled=st.session_state["respondido"]):
            esperado = exercicio["classificacao_esperada"]
            registrar_resposta_aprender(st.session_state, resposta, esperado)

        if st.session_state["respondido"]:
            esperado = st.session_state["ultima_classificacao_esperada"]

            if st.session_state["ultimo_acerto"]:
                st.success("Você acertou.")
            else:
                st.error(
                    "Você errou. Resposta esperada: "
                    f"{rotulo_classificacao(esperado)}"
                )

            escrever_lista("Sinais", exercicio["sinais"], "Nenhum sinal.")

            st.write("**Explicação:**")
            st.write(exercicio["explicacao"])

            escrever_lista(
                "Recomendações",
                exercicio["recomendacoes"],
                "Nenhuma recomendação.",
            )

            if st.button("Próximo exercício"):
                avancar_exercicio(st.session_state)
                st.rerun()

    else:
        total = len(exercicios)
        acertos = st.session_state["acertos"]
        aproveitamento = (acertos / total) * 100

        st.success("Modo Aprender concluído.")
        st.write(f"**Acertos:** {acertos} de {total}")
        st.write(f"**Aproveitamento:** {aproveitamento:.0f}%")
        st.progress(acertos / total)

        if st.button("Recomeçar"):
            st.session_state["indice_exercicio"] = 0
            st.session_state["acertos"] = 0
            st.session_state["respondido"] = False
            st.session_state["ultimo_acerto"] = None
            st.session_state["ultima_classificacao_esperada"] = None
            st.rerun()


def renderizar_menu_principal() -> None:
    st.subheader("Menu principal")

    coluna_analise, coluna_aprender, coluna_sair = st.columns(3)

    if coluna_analise.button("Analisar mensagem", use_container_width=True):
        selecionar_modo(st.session_state, "analise")
        st.rerun()

    if coluna_aprender.button("Iniciar modo Aprender", use_container_width=True):
        selecionar_modo(st.session_state, "aprender")
        st.rerun()

    if coluna_sair.button("Sair", use_container_width=True):
        selecionar_modo(st.session_state, "sair")
        st.rerun()


def renderizar_botao_voltar_menu() -> None:
    if st.button("Voltar ao menu"):
        selecionar_modo(st.session_state, "menu")
        st.rerun()


def renderizar_tela_sair() -> None:
    st.subheader("Sair")
    st.info("Aplicação encerrada. Você pode fechar esta aba do navegador.")
    renderizar_botao_voltar_menu()


def executar_web() -> None:
    st.set_page_config(
        page_title="Escudo Digital IA",
        page_icon="🛡️",
        layout="centered",
    )

    st.title("Escudo Digital IA")
    st.write("Assistente Digital para reconhecer possíveis golpes digitais.")

    preparar_estado_menu(st.session_state)

    if st.session_state["modo_web"] == "menu":
        renderizar_menu_principal()
    elif st.session_state["modo_web"] == "analise":
        renderizar_botao_voltar_menu()
        renderizar_aba_analise()
    elif st.session_state["modo_web"] == "aprender":
        renderizar_botao_voltar_menu()
        renderizar_aba_aprender()
    else:
        renderizar_tela_sair()


if __name__ == "__main__":
    executar_web()
