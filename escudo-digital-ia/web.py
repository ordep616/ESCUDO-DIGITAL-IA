import streamlit as st

from aprender import carregar_exercicios
from ai_service import AIServiceError
from main import RespostaIAInvalidaError, processar_mensagem


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


def rotulo_classificacao(classificacao):
    return CLASSIFICACOES.get(classificacao, str(classificacao).replace("_", " "))


def descricao_classificacao(classificacao):
    return DESCRICOES_CLASSIFICACAO.get(
        classificacao,
        "Resultado retornado pela análise.",
    )


def formatar_confianca(confianca):
    valor = max(0.0, min(float(confianca), 1.0))

    if valor >= 0.8:
        nivel = "Alta"
    elif valor >= 0.5:
        nivel = "Média"
    else:
        nivel = "Baixa"

    return f"{nivel} ({valor * 100:.0f}%)", valor


def escrever_lista(titulo, itens, texto_vazio):
    st.write(f"**{titulo}:**")

    if itens:
        for item in itens:
            st.markdown(f"- {item}")
        return

    st.write(texto_vazio)


st.set_page_config(
    page_title="Escudo Digital IA",
    page_icon="🛡️",
    layout="centered",
)

st.title("Escudo Digital IA")
st.write("Assistente Digital para reconhecer possíveis golpes digitais.")

aba_analise, aba_aprender = st.tabs(["Analisar mensagem", "Modo Aprender"])


with aba_analise:
    st.subheader("Analisar mensagem")

    mensagem = st.text_area(
        "Cole uma mensagem fictícia ou previamente anonimizada:",
        height=180,
    )

    if st.button("Analisar"):
        try:
            resultado = processar_mensagem(mensagem)
            classificacao = resultado["classificacao"]
            texto_confianca, valor_confianca = formatar_confianca(
                resultado["confianca"]
            )

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

        except (ValueError, AIServiceError, RespostaIAInvalidaError) as erro:
            st.error(f"Não foi possível concluir a análise: {erro}")


with aba_aprender:
    st.subheader("Modo Aprender")

    exercicios = carregar_exercicios()

    if "indice_exercicio" not in st.session_state:
        st.session_state.indice_exercicio = 0
        st.session_state.acertos = 0
        st.session_state.respondido = False

    indice = st.session_state.indice_exercicio

    if indice < len(exercicios):
        exercicio = exercicios[indice]

        st.write(f"**Exercício {indice + 1}/{len(exercicios)}**")
        st.info(exercicio["mensagem"])

        resposta = st.radio(
            "Qual é a classificação?",
            [
                "baixo_risco",
                "moderado",
                "alto_risco",
                "informacao_insuficiente",
            ],
            format_func=rotulo_classificacao,
            key=f"resposta_{indice}",
        )

        if st.button("Responder"):
            esperado = exercicio["classificacao_esperada"]

            if resposta == esperado:
                st.session_state.acertos += 1
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

            st.session_state.respondido = True

        if st.session_state.respondido:
            if st.button("Próximo exercício"):
                st.session_state.indice_exercicio += 1
                st.session_state.respondido = False
                st.rerun()

    else:
        total = len(exercicios)
        acertos = st.session_state.acertos
        aproveitamento = (acertos / total) * 100

        st.success("Modo Aprender concluído.")
        st.write(f"**Acertos:** {acertos} de {total}")
        st.write(f"**Aproveitamento:** {aproveitamento:.0f}%")
        st.progress(acertos / total)

        if st.button("Recomeçar"):
            st.session_state.indice_exercicio = 0
            st.session_state.acertos = 0
            st.session_state.respondido = False
            st.rerun()
