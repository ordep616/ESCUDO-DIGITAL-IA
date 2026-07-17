from __future__ import annotations

import base64
from collections.abc import Callable, MutableMapping
from html import escape
from pathlib import Path
import re
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

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

ROTULOS_ITENS_APRENDER = {
    "ameaca": "Ameaça",
    "bloquear_e_denunciar": "Bloquear e denunciar",
    "confirmar_com_a_pessoa_por_outro_canal": "Confirmar por outro canal",
    "imitacao_de_pessoa_ou_instituicao": "Imitação de pessoa ou instituição",
    "link_desconhecido": "Link desconhecido",
    "nao_clicar": "Não clicar",
    "nao_enviar_senhas_ou_codigos": "Não enviar senhas ou códigos",
    "nao_responder": "Não responder",
    "pedido_de_dinheiro": "Pedido de dinheiro",
    "pedido_de_senha_ou_codigo": "Pedido de senha ou código",
    "recompensa": "Recompensa",
    "tentativa_de_impedir_verificacao": "Tentativa de impedir verificação",
    "urgencia": "Urgência",
    "usar_canal_oficial": "Usar canal oficial",
}

CAMINHO_LOGO = (
    Path(__file__).resolve().parent
    / "assets"
    / "escudo_digital_ia_security_network.png"
)

MODOS_WEB = {"menu", "analise", "aprender", "sair"}
MODAIS_WEB = {"analise", "aprender"}
ALTURA_MODAL = 520

ESTILO_SITE = """
<style>
:root {
    --escudo-bg-deep: #030817;
    --escudo-bg: #071426;
    --escudo-cyan: #00D9FF;
    --escudo-green: #B7FF24;
    --escudo-white: #F5F7FA;
    --escudo-purple: #7B55FF;
}

.stApp {
    position: relative;
    min-height: 100vh;
    background:
        radial-gradient(circle at center, rgba(0, 217, 255, 0.12) 0%, rgba(7, 20, 38, 0.58) 32%, rgba(3, 8, 23, 0.98) 78%),
        linear-gradient(135deg, var(--escudo-bg-deep) 0%, var(--escudo-bg) 48%, var(--escudo-bg-deep) 100%);
    color: var(--escudo-white);
}

.escudo-constellation {
    position: fixed;
    inset: 0;
    z-index: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
}

.escudo-constellation line {
    stroke: rgba(0, 217, 255, 0.30);
    stroke-width: 1.15;
}

.escudo-constellation circle {
    filter: drop-shadow(0 0 8px rgba(0, 217, 255, 0.42));
}

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
[data-testid="stMainMenu"],
[data-testid="stBaseButton-header"],
[data-testid="stMainMenuButton"],
.stDeployButton,
#MainMenu,
footer {
    display: none !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
.main {
    background: transparent;
}

[data-testid="stAppViewContainer"] > .main,
.block-container {
    position: relative;
    z-index: 1;
}

.block-container {
    width: min(1120px, 100%);
    max-width: 1120px;
    height: 100vh;
    min-height: 100vh;
    padding: clamp(24px, 5vh, 56px) clamp(18px, 4vw, 48px) 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}

[data-testid="stMarkdownContainer"] h2 {
    color: var(--escudo-white);
    width: min(840px, 100%);
    text-align: left;
    font-size: clamp(1.35rem, 2vw, 1.8rem);
    font-weight: 800;
    margin: 0 auto 1.25rem;
}

.escudo-logo-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 0 auto clamp(24px, 3.5vh, 44px);
}

.escudo-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: clamp(30px, 4vw, 56px);
    width: min(70vw, 780px);
    filter:
        drop-shadow(0 0 18px rgba(0, 217, 255, 0.16))
        drop-shadow(0 0 45px rgba(0, 217, 255, 0.12));
}

.escudo-wordmark {
    display: grid;
    gap: 10px;
    line-height: 0.92;
    color: var(--escudo-white);
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-size: clamp(3.2rem, 6.6vw, 5.15rem);
    font-weight: 900;
    letter-spacing: 0.025em;
    text-transform: uppercase;
    white-space: nowrap;
}

.escudo-wordmark span:last-child {
    color: var(--escudo-green);
}

.escudo-shield {
    width: clamp(172px, 18vw, 245px);
    height: auto;
    overflow: visible;
}

.escudo-shield-outline {
    fill: rgba(10, 32, 64, 0.64);
    stroke: var(--escudo-cyan);
    stroke-width: 7;
    stroke-linejoin: round;
    filter: drop-shadow(0 0 16px rgba(0, 217, 255, 0.38));
}

.escudo-check {
    fill: none;
    stroke: var(--escudo-green);
    stroke-width: 13;
    stroke-linecap: square;
    stroke-linejoin: miter;
}

.escudo-key-line {
    stroke: #2d86ff;
    stroke-width: 5;
    stroke-linecap: square;
}

.escudo-key-dot {
    fill: #2d86ff;
}

.escudo-purple-line {
    stroke: var(--escudo-purple);
    stroke-width: 5;
    stroke-linecap: square;
}

.escudo-purple-dot {
    fill: var(--escudo-purple);
}

[data-testid="stHorizontalBlock"] {
    width: min(840px, 100%);
    margin: 0 auto;
    gap: 18px;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button {
    min-height: 50px;
    border: 1px solid rgba(0, 217, 255, 0.38);
    border-radius: 14px;
    background:
        linear-gradient(180deg, rgba(9, 34, 65, 0.98), rgba(5, 22, 45, 0.98));
    color: var(--escudo-white);
    font-size: 0.98rem;
    font-weight: 800;
    letter-spacing: 0;
    box-shadow: 0 0 0 rgba(0, 217, 255, 0);
    cursor: pointer;
    transition:
        border-color 160ms ease,
        box-shadow 160ms ease,
        transform 160ms ease,
        background 160ms ease;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    border-color: rgba(0, 217, 255, 0.82);
    background:
        linear-gradient(180deg, rgba(10, 45, 82, 1), rgba(5, 27, 55, 1));
    color: var(--escudo-white);
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.20);
    transform: translateY(-1px);
}

.stButton > button:focus,
.stButton > button:focus-visible,
[data-testid="stFormSubmitButton"] button:focus,
[data-testid="stFormSubmitButton"] button:focus-visible {
    border-color: var(--escudo-green);
    box-shadow: 0 0 0 3px rgba(183, 255, 36, 0.18);
    color: var(--escudo-white);
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    border-color: rgba(183, 255, 36, 0.54);
    box-shadow: 0 0 24px rgba(0, 217, 255, 0.12);
}

.escudo-learning-complete {
    width: min(840px, 100%);
    margin: 0.75rem auto 0.8rem;
    padding: 0.85rem 1rem;
    border: 1px solid rgba(0, 217, 255, 0.36);
    border-left: 4px solid var(--escudo-green);
    border-radius: 12px;
    background:
        linear-gradient(135deg, rgba(5, 30, 58, 0.98), rgba(3, 8, 23, 0.98));
    box-shadow: 0 0 24px rgba(0, 217, 255, 0.10);
}

.escudo-learning-complete strong,
.escudo-learning-complete span {
    display: block;
}

.escudo-learning-complete strong {
    color: var(--escudo-white);
    font-size: 1rem;
    margin-bottom: 0.35rem;
}

.escudo-learning-complete span {
    color: rgba(245, 247, 250, 0.86);
    line-height: 1.45;
}

.escudo-learning-complete--review {
    border-left-color: var(--escudo-cyan);
}

.escudo-learning-details {
    width: min(840px, 100%);
    margin: 0.65rem auto 0;
    display: grid;
    gap: 0.75rem;
}

.escudo-learning-section {
    padding: 0.82rem 0.95rem;
    border: 1px solid rgba(0, 217, 255, 0.22);
    border-radius: 12px;
    background:
        linear-gradient(135deg, rgba(7, 25, 49, 0.96), rgba(3, 8, 23, 0.96));
}

.escudo-learning-section--message {
    border-left: 4px solid rgba(0, 217, 255, 0.64);
}

.escudo-learning-section--explanation {
    border-left: 4px solid rgba(183, 255, 36, 0.62);
}

.escudo-learning-section-header {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 0.58rem;
}

.escudo-learning-section-icon {
    width: 28px;
    height: 28px;
    display: inline-grid;
    place-items: center;
    border-radius: 999px;
    background: rgba(0, 217, 255, 0.12);
    color: var(--escudo-cyan);
    font-size: 0.9rem;
    font-weight: 900;
    line-height: 1;
}

.escudo-learning-section-title {
    color: var(--escudo-white);
    font-size: 0.98rem;
    font-weight: 850;
    line-height: 1.25;
}

.escudo-learning-text,
.escudo-learning-empty {
    margin: 0;
    color: rgba(245, 247, 250, 0.88);
    font-size: 0.95rem;
    line-height: 1.55;
    white-space: pre-wrap;
}

.escudo-learning-empty {
    color: rgba(245, 247, 250, 0.62);
    font-style: italic;
}

.escudo-learning-topic-list {
    display: grid;
    gap: 0.42rem;
    padding: 0.05rem 0 0;
    margin: 0;
    list-style: none;
}

.escudo-learning-topic-item {
    display: flex;
    align-items: flex-start;
    gap: 0.58rem;
    min-height: auto;
    padding: 0.08rem 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: rgba(245, 247, 250, 0.90);
    font-size: 0.92rem;
    font-weight: 650;
    line-height: 1.45;
}

.escudo-learning-topic-item--recommendation,
.escudo-learning-topic-item--message {
    background: transparent;
}

.escudo-learning-topic-marker {
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    margin-top: 0.48rem;
    border-radius: 999px;
    background: var(--escudo-cyan);
    box-shadow: 0 0 10px rgba(0, 217, 255, 0.42);
}

.escudo-learning-topic-item--recommendation .escudo-learning-topic-marker,
.escudo-learning-section--explanation .escudo-learning-topic-marker {
    background: var(--escudo-green);
    box-shadow: 0 0 10px rgba(183, 255, 36, 0.34);
}

.escudo-learning-topic-item--message .escudo-learning-topic-marker {
    background: var(--escudo-purple);
    box-shadow: 0 0 10px rgba(123, 85, 255, 0.36);
}

.escudo-learning-topic-label {
    flex: 1;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: rgba(0, 217, 255, 0.30) !important;
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.30);
    margin-top: 0.45rem !important;
    height: clamp(280px, calc(100vh - 585px), 520px) !important;
    max-height: clamp(280px, calc(100vh - 585px), 520px) !important;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    scrollbar-color: rgba(0, 217, 255, 0.50) rgba(3, 8, 23, 0.28);
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
    max-height: inherit !important;
    overflow-y: auto !important;
}

.st-key-escudo-modal-analise,
.st-key-escudo-modal-aprender {
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
    height: clamp(280px, calc(100vh - 585px), 520px) !important;
    max-height: clamp(280px, calc(100vh - 585px), 520px) !important;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    scrollbar-color: rgba(0, 217, 255, 0.50) rgba(3, 8, 23, 0.28);
}

div[data-testid="stLayoutWrapper"]:has(> .st-key-escudo-modal-analise),
div[data-testid="stLayoutWrapper"]:has(> .st-key-escudo-modal-aprender) {
    position: relative;
    z-index: 3;
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
    border-radius: 8px;
    height: clamp(280px, calc(100vh - 585px), 520px) !important;
    max-height: clamp(280px, calc(100vh - 585px), 520px) !important;
    overflow: hidden !important;
    transform: translateY(-8px);
}

textarea,
[data-baseweb="select"] > div {
    border-color: rgba(0, 217, 255, 0.28) !important;
}

@media (max-width: 780px) {
    .block-container {
        padding: 24px 14px 24px;
    }

    .escudo-logo-wrap {
        margin-bottom: 20px;
    }

    .escudo-brand {
        width: 95vw;
        gap: 18px;
    }

    .escudo-wordmark {
        font-size: clamp(2.05rem, 11vw, 3.5rem);
    }

    .escudo-shield {
        width: clamp(104px, 28vw, 150px);
    }

    [data-testid="stHorizontalBlock"] {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
    }

    [data-testid="column"] {
        width: 100% !important;
    }
}
</style>
"""

MARCA_SITE_HTML = """
<div class="escudo-constellation" aria-hidden="true">
    <svg viewBox="0 0 1600 1000" preserveAspectRatio="none">
        <g>
            <line x1="0" y1="220" x2="170" y2="95" />
            <line x1="170" y1="95" x2="320" y2="160" />
            <line x1="320" y1="160" x2="455" y2="35" />
            <line x1="320" y1="160" x2="420" y2="265" />
            <line x1="95" y1="470" x2="260" y2="560" />
            <line x1="260" y1="560" x2="350" y2="430" />
            <line x1="350" y1="430" x2="95" y2="470" />
            <line x1="70" y1="760" x2="245" y2="880" />
            <line x1="245" y1="880" x2="382" y2="820" />
            <line x1="382" y1="820" x2="520" y2="930" />
            <line x1="1060" y1="70" x2="1225" y2="145" />
            <line x1="1225" y1="145" x2="1410" y2="80" />
            <line x1="1410" y1="80" x2="1588" y2="150" />
            <line x1="1225" y1="145" x2="1345" y2="300" />
            <line x1="1345" y1="300" x2="1515" y2="380" />
            <line x1="1515" y1="380" x2="1588" y2="150" />
            <line x1="1160" y1="610" x2="1370" y2="520" />
            <line x1="1370" y1="520" x2="1540" y2="690" />
            <line x1="1540" y1="690" x2="1435" y2="870" />
            <line x1="1435" y1="870" x2="1250" y2="810" />
            <line x1="1250" y1="810" x2="1160" y2="610" />
            <line x1="720" y1="925" x2="930" y2="870" />
            <line x1="930" y1="870" x2="1110" y2="950" />
            <line x1="1110" y1="950" x2="1250" y2="810" />
            <line x1="0" y1="340" x2="130" y2="455" />
            <line x1="130" y1="455" x2="230" y2="350" />
            <line x1="230" y1="350" x2="420" y2="265" />
            <line x1="455" y1="35" x2="610" y2="120" />
            <line x1="610" y1="120" x2="760" y2="55" />
            <line x1="760" y1="55" x2="930" y2="110" />
            <line x1="930" y1="110" x2="1060" y2="70" />
            <line x1="545" y1="720" x2="720" y2="925" />
            <line x1="382" y1="820" x2="545" y2="720" />
            <line x1="930" y1="870" x2="1010" y2="735" />
            <line x1="1010" y1="735" x2="1160" y2="610" />
            <line x1="1370" y1="520" x2="1510" y2="505" />
            <line x1="1510" y1="505" x2="1600" y2="430" />
            <line x1="1510" y1="505" x2="1540" y2="690" />
            <line x1="1225" y1="145" x2="1290" y2="35" />
            <line x1="1290" y1="35" x2="1410" y2="80" />
        </g>
        <g>
            <circle cx="0" cy="220" r="5" fill="#3568d8" />
            <circle cx="170" cy="95" r="4" fill="#00D9FF" />
            <circle cx="320" cy="160" r="5" fill="#00D9FF" />
            <circle cx="455" cy="35" r="5" fill="#00D9FF" />
            <circle cx="420" cy="265" r="4" fill="#00D9FF" />
            <circle cx="95" cy="470" r="4" fill="#7B55FF" />
            <circle cx="260" cy="560" r="5" fill="#00D9FF" />
            <circle cx="350" cy="430" r="4" fill="#00D9FF" />
            <circle cx="70" cy="760" r="5" fill="#00D9FF" />
            <circle cx="245" cy="880" r="4" fill="#7B55FF" />
            <circle cx="382" cy="820" r="5" fill="#00D9FF" />
            <circle cx="520" cy="930" r="5" fill="#00D9FF" />
            <circle cx="1060" cy="70" r="4" fill="#00D9FF" />
            <circle cx="1225" cy="145" r="5" fill="#00D9FF" />
            <circle cx="1410" cy="80" r="4" fill="#00D9FF" />
            <circle cx="1588" cy="150" r="5" fill="#00D9FF" />
            <circle cx="1345" cy="300" r="4" fill="#7B55FF" />
            <circle cx="1515" cy="380" r="5" fill="#00D9FF" />
            <circle cx="1160" cy="610" r="4" fill="#00D9FF" />
            <circle cx="1370" cy="520" r="5" fill="#00D9FF" />
            <circle cx="1540" cy="690" r="5" fill="#00D9FF" />
            <circle cx="1435" cy="870" r="5" fill="#00D9FF" />
            <circle cx="1250" cy="810" r="4" fill="#7B55FF" />
            <circle cx="720" cy="925" r="5" fill="#00D9FF" />
            <circle cx="930" cy="870" r="4" fill="#00D9FF" />
            <circle cx="1110" cy="950" r="4" fill="#3568d8" />
            <circle cx="130" cy="455" r="4" fill="#00D9FF" />
            <circle cx="230" cy="350" r="4" fill="#3568d8" />
            <circle cx="610" cy="120" r="4" fill="#00D9FF" />
            <circle cx="760" cy="55" r="4" fill="#7B55FF" />
            <circle cx="930" cy="110" r="4" fill="#00D9FF" />
            <circle cx="545" cy="720" r="4" fill="#00D9FF" />
            <circle cx="1010" cy="735" r="4" fill="#7B55FF" />
            <circle cx="1510" cy="505" r="4" fill="#00D9FF" />
            <circle cx="1290" cy="35" r="4" fill="#00D9FF" />
        </g>
    </svg>
</div>
<div class="escudo-logo-wrap">
    <div class="escudo-brand" aria-label="Logo Escudo Digital IA">
        <div class="escudo-wordmark" aria-hidden="true">
            <span>Escudo</span>
            <span>Digital IA</span>
        </div>
        <svg class="escudo-shield" viewBox="0 0 260 320" role="img" aria-label="Escudo Digital IA">
            <path class="escudo-shield-outline" d="M130 16 L224 54 L210 184 L130 298 L50 184 L36 54 Z" />
            <path class="escudo-check" d="M82 162 L116 196 L182 106" />
            <circle class="escudo-key-dot" cx="74" cy="82" r="15" />
            <path class="escudo-key-line" d="M88 96 L116 124" />
            <path class="escudo-purple-line" d="M170 198 L198 226" />
            <circle class="escudo-purple-dot" cx="208" cy="236" r="16" />
        </svg>
    </div>
</div>
"""

ESTILO_MODAL = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
    border-radius: 8px !important;
    overflow-y: auto !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: linear-gradient(180deg, #061127 0%, #030817 100%) !important;
}
</style>
"""

ATALHOS_TECLADO_HTML = """
<script>
(function () {
    const documento = window.parent.document;

    if (documento.__escudoDigitalAtalhosInstalados) {
        return;
    }

    documento.__escudoDigitalAtalhosInstalados = true;

    function textoBotao(botao) {
        return (botao.innerText || botao.textContent || "").trim();
    }

    function botaoVisivel(nome) {
        return Array.from(documento.querySelectorAll("button")).find(
            function (botao) {
                const retangulo = botao.getBoundingClientRect();
                const visivel = retangulo.width > 0 && retangulo.height > 0;
                const habilitado = (
                    !botao.disabled &&
                    botao.getAttribute("aria-disabled") !== "true"
                );

                return textoBotao(botao) === nome && visivel && habilitado;
            }
        );
    }

    function clicarPrimeiroBotao(nomes) {
        for (const nome of nomes) {
            const botao = botaoVisivel(nome);

            if (botao) {
                botao.click();
                return true;
            }
        }

        return false;
    }

    documento.addEventListener(
        "keydown",
        function (evento) {
            if (
                evento.key !== "Enter" ||
                evento.shiftKey ||
                evento.ctrlKey ||
                evento.metaKey ||
                evento.altKey
            ) {
                return;
            }

            const elementoAtivo = documento.activeElement;

            if (elementoAtivo && elementoAtivo.tagName === "BUTTON") {
                return;
            }

            const acionou = clicarPrimeiroBotao([
                "Analisar",
                "Responder",
                "Próximo exercício",
                "Ver resultado final",
                "Recomeçar",
            ]);

            if (acionou) {
                evento.preventDefault();
                evento.stopPropagation();
            }
        },
        true
    );
})();
</script>
"""


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
    if "modal_web" not in estado:
        estado["modal_web"] = None


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


def carregar_logo_base64(caminho_logo: Path = CAMINHO_LOGO) -> str:
    return base64.b64encode(caminho_logo.read_bytes()).decode("ascii")


def carregar_icone_site(caminho_logo: Path = CAMINHO_LOGO) -> Image.Image:
    with Image.open(caminho_logo) as imagem:
        return imagem.copy()


def aplicar_estilo_site() -> None:
    st.markdown(ESTILO_SITE, unsafe_allow_html=True)


def renderizar_logo_site() -> None:
    st.markdown(MARCA_SITE_HTML, unsafe_allow_html=True)


def aplicar_estilo_modal() -> None:
    st.markdown(ESTILO_MODAL, unsafe_allow_html=True)


def instalar_atalhos_teclado() -> None:
    components.html(ATALHOS_TECLADO_HTML, height=0)


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


def rotulo_avanco_aprender(indice: int, total: int) -> str:
    if indice + 1 >= total:
        return "Ver resultado final"

    return "Próximo exercício"


def mensagem_feedback_aprender(acertou: bool, esperado: str | None) -> str:
    if acertou:
        return "Você acertou. A resposta foi registrada."

    rotulo_esperado = rotulo_classificacao(esperado or "")
    return f"Você errou. Resposta esperada: {rotulo_esperado}."


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


def selecionar_modal(estado: MutableMapping[str, Any], modal: str) -> None:
    if modal not in MODAIS_WEB:
        raise ValueError("modal da web inválido")

    estado["modal_web"] = modal


def fechar_modal(estado: MutableMapping[str, Any]) -> None:
    estado["modal_web"] = None


def escrever_lista(titulo: str, itens: list[str], texto_vazio: str) -> None:
    st.write(f"**{titulo}:**")

    if itens:
        for item in itens:
            st.markdown(f"- {item}")
        return

    st.write(texto_vazio)


def rotulo_item_aprender(item: str) -> str:
    texto = str(item).strip()

    if texto in ROTULOS_ITENS_APRENDER:
        return ROTULOS_ITENS_APRENDER[texto]

    texto_legivel = " ".join(texto.replace("_", " ").split())
    if not texto_legivel:
        return ""

    return texto_legivel[:1].upper() + texto_legivel[1:]


def dividir_explicacao_aprender(explicacao: str) -> list[str]:
    texto = " ".join(str(explicacao).split())
    if not texto:
        return []

    return [
        parte.strip()
        for parte in re.split(r"(?<=[.!?])\s+", texto)
        if parte.strip()
    ]


def _lista_topicos_aprender_html(
    itens: list[str],
    texto_vazio: str,
    classe_extra: str = "",
    usar_rotulos: bool = True,
) -> str:
    rotulos = []
    for item in itens:
        rotulo = rotulo_item_aprender(item) if usar_rotulos else str(item).strip()
        if rotulo:
            rotulos.append(rotulo)

    if not rotulos:
        return f'<p class="escudo-learning-empty">{escape(texto_vazio)}</p>'

    classe_item = "escudo-learning-topic-item"
    if classe_extra:
        classe_item = f"{classe_item} {classe_extra}"

    topicos = "".join(
        f'<li class="{classe_item}">'
        '<span class="escudo-learning-topic-marker" aria-hidden="true"></span>'
        f'<span class="escudo-learning-topic-label">{escape(rotulo)}</span>'
        "</li>"
        for rotulo in rotulos
    )
    return f'<ul class="escudo-learning-topic-list">{topicos}</ul>'


def detalhes_aprender_html(exercicio: dict[str, Any]) -> str:
    mensagem = _lista_topicos_aprender_html(
        [str(exercicio["mensagem"]).strip()],
        "Mensagem não informada.",
        "escudo-learning-topic-item--message",
        usar_rotulos=False,
    )
    explicacao = _lista_topicos_aprender_html(
        dividir_explicacao_aprender(exercicio["explicacao"]),
        "Nenhuma explicação informada.",
        usar_rotulos=False,
    )
    sinais = _lista_topicos_aprender_html(
        exercicio["sinais"],
        "Nenhum sinal identificado.",
    )
    recomendacoes = _lista_topicos_aprender_html(
        exercicio["recomendacoes"],
        "Nenhuma recomendação específica.",
        "escudo-learning-topic-item--recommendation",
    )

    return (
        '<div class="escudo-learning-details">'
        '<section class="escudo-learning-section escudo-learning-section--message">'
        '<div class="escudo-learning-section-header">'
        '<span class="escudo-learning-section-icon">M</span>'
        '<span class="escudo-learning-section-title">Mensagem analisada</span>'
        "</div>"
        f"{mensagem}"
        "</section>"
        '<section class="escudo-learning-section escudo-learning-section--explanation">'
        '<div class="escudo-learning-section-header">'
        '<span class="escudo-learning-section-icon">E</span>'
        '<span class="escudo-learning-section-title">Por que essa era a resposta?</span>'
        "</div>"
        f"{explicacao}"
        "</section>"
        '<section class="escudo-learning-section">'
        '<div class="escudo-learning-section-header">'
        '<span class="escudo-learning-section-icon">S</span>'
        '<span class="escudo-learning-section-title">Sinais identificados</span>'
        "</div>"
        f"{sinais}"
        "</section>"
        '<section class="escudo-learning-section">'
        '<div class="escudo-learning-section-header">'
        '<span class="escudo-learning-section-icon">R</span>'
        '<span class="escudo-learning-section-title">Recomendações</span>'
        "</div>"
        f"{recomendacoes}"
        "</section>"
        "</div>"
    )


def renderizar_detalhes_aprender(exercicio: dict[str, Any]) -> None:
    st.markdown(detalhes_aprender_html(exercicio), unsafe_allow_html=True)


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


def renderizar_estado_resposta_aprender(acertou: bool, esperado: str | None) -> None:
    classe = "correct" if acertou else "review"
    mensagem = mensagem_feedback_aprender(acertou, esperado)
    st.markdown(
        f"""
        <div class="escudo-learning-complete escudo-learning-complete--{classe}">
            <strong>Resposta concluída</strong>
            <span>{mensagem}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    with st.form("form_analise", enter_to_submit=True):
        mensagem = st.text_area(
            "Cole uma mensagem fictícia ou previamente anonimizada:",
            height=180,
        )

        analisar = st.form_submit_button("Analisar")

    if analisar:
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
    total_exercicios = len(exercicios)

    if indice < total_exercicios:
        exercicio = exercicios[indice]
        respondido = bool(st.session_state["respondido"])

        progresso = (indice + (1 if respondido else 0)) / total_exercicios
        st.write(f"**Questão {indice + 1}/{total_exercicios}**")
        st.progress(progresso)

        if not respondido:
            st.info(exercicio["mensagem"])

            resposta = st.radio(
                "Qual é a classificação?",
                OPCOES_CLASSIFICACAO,
                format_func=rotulo_classificacao,
                key=f"resposta_{indice}",
            )

            if st.button(
                "Responder",
                key=f"responder_{indice}",
                type="primary",
                use_container_width=True,
            ):
                esperado = exercicio["classificacao_esperada"]
                registrar_resposta_aprender(st.session_state, resposta, esperado)
                st.rerun()

        if respondido:
            esperado = st.session_state["ultima_classificacao_esperada"]
            acertou = bool(st.session_state["ultimo_acerto"])

            coluna_feedback, coluna_avanco = st.columns([2, 1])
            with coluna_feedback:
                renderizar_estado_resposta_aprender(acertou, esperado)
            with coluna_avanco:
                if st.button(
                    rotulo_avanco_aprender(indice, total_exercicios),
                    key=f"avancar_{indice}",
                    type="primary",
                    use_container_width=True,
                ):
                    avancar_exercicio(st.session_state)
                    st.rerun()

            renderizar_detalhes_aprender(exercicio)

    else:
        acertos = st.session_state["acertos"]
        aproveitamento = (acertos / total_exercicios) * 100

        st.success("Modo Aprender concluído.")
        st.write(f"**Acertos:** {acertos} de {total_exercicios}")
        st.write(f"**Aproveitamento:** {aproveitamento:.0f}%")
        st.progress(acertos / total_exercicios)

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
        selecionar_modal(st.session_state, "analise")

    if coluna_aprender.button("Iniciar modo Aprender", use_container_width=True):
        selecionar_modal(st.session_state, "aprender")

    if coluna_sair.button("Sair", use_container_width=True):
        selecionar_modo(st.session_state, "sair")
        st.rerun()

    if st.session_state["modal_web"] == "analise":
        renderizar_modal_analise()
    elif st.session_state["modal_web"] == "aprender":
        renderizar_modal_aprender()


def renderizar_botao_voltar_menu() -> None:
    if st.button("Voltar ao menu"):
        selecionar_modo(st.session_state, "menu")
        st.rerun()


def renderizar_tela_sair() -> None:
    st.subheader("Sair")
    st.info("Aplicação encerrada. Você pode fechar esta aba do navegador.")
    renderizar_botao_voltar_menu()


def renderizar_modal_analise() -> None:
    aplicar_estilo_modal()
    with st.container(
        border=True,
        height=ALTURA_MODAL,
        key="escudo-modal-analise",
    ):
        renderizar_aba_analise()


def renderizar_modal_aprender() -> None:
    aplicar_estilo_modal()
    with st.container(
        border=True,
        height=ALTURA_MODAL,
        key="escudo-modal-aprender",
    ):
        renderizar_aba_aprender()


def executar_web() -> None:
    st.set_page_config(
        page_title="Escudo Digital IA",
        page_icon=carregar_icone_site(),
        layout="wide",
    )

    aplicar_estilo_site()
    renderizar_logo_site()
    aplicar_estilo_modal()
    instalar_atalhos_teclado()

    preparar_estado_menu(st.session_state)

    if st.session_state["modo_web"] == "sair":
        renderizar_tela_sair()
    else:
        renderizar_menu_principal()


if __name__ == "__main__":
    executar_web()
