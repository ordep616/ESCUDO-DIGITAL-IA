"""Testes das regras auxiliares da interface web."""

import unittest
from types import SimpleNamespace

from web import ATALHOS_TECLADO_HTML
from web import ALTURA_MODAL
from web import CAMINHO_LOGO
from web import ESTILO_MODAL
from web import ESTILO_SITE
from web import MARCA_SITE_HTML
from web import avancar_exercicio, formatar_confianca
from web import carregar_logo_base64
from web import detalhes_aprender_html
from web import dividir_explicacao_aprender
from web import fechar_modal
from web import instalar_atalhos_teclado
from web import mensagem_feedback_aprender
from web import preparar_estado_menu, selecionar_modo
from web import preparar_upload_imagem
from web import selecionar_modal
from web import registrar_feedback_analise, registrar_resposta_aprender
from web import renderizar_modal_analise, renderizar_modal_aprender
from web import rotulo_avanco_aprender
from web import rotulo_classificacao
from web import rotulo_item_aprender


class WebTests(unittest.TestCase):
    def test_upload_de_imagem_exige_arquivo(self) -> None:
        with self.assertRaisesRegex(ValueError, "Selecione uma imagem"):
            preparar_upload_imagem(None, True)

    def test_upload_de_imagem_exige_autorizacao(self) -> None:
        arquivo = SimpleNamespace(
            type="image/png",
            getvalue=lambda: b"imagem",
        )

        with self.assertRaisesRegex(ValueError, "autoriza"):
            preparar_upload_imagem(arquivo, False)

    def test_upload_de_imagem_retorna_bytes_e_tipo(self) -> None:
        arquivo = SimpleNamespace(
            type="image/png",
            getvalue=lambda: b"imagem",
        )

        imagem, tipo_mime = preparar_upload_imagem(
            arquivo,
            True,
        )

        self.assertEqual(imagem, b"imagem")
        self.assertEqual(tipo_mime, "image/png")

    def test_estado_da_web_inicia_no_menu_principal(self) -> None:
        estado = {}

        preparar_estado_menu(estado)

        self.assertEqual(estado["modo_web"], "menu")
        self.assertIsNone(estado["modal_web"])

    def test_seleciona_opcoes_do_menu_principal(self) -> None:
        estado = {"modo_web": "menu"}

        selecionar_modo(estado, "analise")
        self.assertEqual(estado["modo_web"], "analise")

        selecionar_modo(estado, "aprender")
        self.assertEqual(estado["modo_web"], "aprender")

        selecionar_modo(estado, "sair")
        self.assertEqual(estado["modo_web"], "sair")

    def test_rejeita_modo_web_invalido(self) -> None:
        with self.assertRaisesRegex(ValueError, "modo da web inválido"):
            selecionar_modo({}, "configuracao")

    def test_seleciona_modal_abaixo_do_menu_principal(self) -> None:
        estado = {"modal_web": None}

        selecionar_modal(estado, "analise")
        self.assertEqual(estado["modal_web"], "analise")

        selecionar_modal(estado, "aprender")
        self.assertEqual(estado["modal_web"], "aprender")

    def test_fecha_modal_abaixo_do_menu_principal(self) -> None:
        estado = {"modal_web": "analise"}

        fechar_modal(estado)

        self.assertIsNone(estado["modal_web"])

    def test_rejeita_modal_web_invalido(self) -> None:
        with self.assertRaisesRegex(ValueError, "modal da web inválido"):
            selecionar_modal({}, "configuracao")

    def test_modais_principais_estao_disponiveis(self) -> None:
        self.assertTrue(callable(renderizar_modal_analise))
        self.assertTrue(callable(renderizar_modal_aprender))

    def test_atalhos_de_teclado_estao_disponiveis(self) -> None:
        self.assertTrue(callable(instalar_atalhos_teclado))
        self.assertIn("window.parent.document", ATALHOS_TECLADO_HTML)
        self.assertIn("Enter", ATALHOS_TECLADO_HTML)
        self.assertIn("shiftKey", ATALHOS_TECLADO_HTML)
        self.assertNotIn("Escape", ATALHOS_TECLADO_HTML)
        self.assertNotIn("Fechar", ATALHOS_TECLADO_HTML)
        self.assertIn("Analisar", ATALHOS_TECLADO_HTML)
        self.assertIn("Responder", ATALHOS_TECLADO_HTML)
        self.assertIn("Próximo exercício", ATALHOS_TECLADO_HTML)
        self.assertIn("Ver resultado final", ATALHOS_TECLADO_HTML)
        self.assertIn("Recomeçar", ATALHOS_TECLADO_HTML)

    def test_estilo_modal_inline_preserva_fundo_do_site(self) -> None:
        self.assertIn("stVerticalBlockBorderWrapper", ESTILO_MODAL)
        self.assertIn("#061127", ESTILO_MODAL)
        self.assertIn("#030817", ESTILO_MODAL)
        self.assertNotIn("background: transparent", ESTILO_MODAL)
        self.assertIn("border-radius: 8px", ESTILO_MODAL)
        self.assertIn("overflow-y: auto", ESTILO_MODAL)
        self.assertNotIn("dialog::backdrop", ESTILO_MODAL)
        self.assertNotIn("data-baseweb", ESTILO_MODAL)

    def test_modal_tem_altura_propria_para_rolagem_interna(self) -> None:
        self.assertEqual(ALTURA_MODAL, 520)

    def test_logo_da_home_usa_asset_portavel(self) -> None:
        self.assertEqual(CAMINHO_LOGO.name, "escudo_digital_ia_security_network.png")
        self.assertEqual(CAMINHO_LOGO.parent.name, "assets")
        self.assertTrue(CAMINHO_LOGO.exists())
        self.assertGreater(len(carregar_logo_base64()), 100)

    def test_estilo_site_configura_home_responsiva(self) -> None:
        self.assertIn("width: min(70vw, 780px)", ESTILO_SITE)
        self.assertIn("width: 95vw", ESTILO_SITE)
        self.assertIn("clamp(24px, 3.5vh, 44px)", ESTILO_SITE)
        self.assertIn("overflow: hidden", ESTILO_SITE)
        self.assertIn("overflow-y: auto", ESTILO_SITE)
        self.assertIn("calc(100vh - 585px)", ESTILO_SITE)
        self.assertIn("overscroll-behavior: contain", ESTILO_SITE)
        self.assertIn("stLayoutWrapper", ESTILO_SITE)
        self.assertIn(":has(> .st-key-escudo-modal-analise)", ESTILO_SITE)
        self.assertIn("z-index: 3", ESTILO_SITE)
        self.assertIn("translateY(-8px)", ESTILO_SITE)
        self.assertIn("escudo-learning-complete", ESTILO_SITE)
        self.assertIn("escudo-learning-details", ESTILO_SITE)
        self.assertIn("escudo-learning-topic-list", ESTILO_SITE)
        self.assertIn("escudo-learning-topic-item", ESTILO_SITE)
        self.assertIn("button[kind=\"primary\"]", ESTILO_SITE)
        self.assertIn("st-key-escudo-modal-analise", ESTILO_SITE)
        self.assertIn("st-key-escudo-modal-aprender", ESTILO_SITE)
        self.assertIn("escudo-constellation", ESTILO_SITE)
        self.assertIn("stroke: rgba(0, 217, 255, 0.30)", ESTILO_SITE)
        self.assertIn("text-align: left", ESTILO_SITE)
        self.assertIn("header[data-testid=\"stHeader\"]", ESTILO_SITE)
        self.assertIn("[data-testid=\"stDeployButton\"]", ESTILO_SITE)
        self.assertIn("[data-testid=\"stAppDeployButton\"]", ESTILO_SITE)
        self.assertIn("[data-testid=\"stMainMenu\"]", ESTILO_SITE)
        self.assertIn("[data-testid=\"stBaseButton-header\"]", ESTILO_SITE)
        self.assertIn("[data-testid=\"stMainMenuButton\"]", ESTILO_SITE)
        self.assertIn("#030817", ESTILO_SITE)
        self.assertIn("#00D9FF", ESTILO_SITE)

    def test_marca_site_preserva_logo_limpa_da_home(self) -> None:
        self.assertIn("Escudo", MARCA_SITE_HTML)
        self.assertIn("Digital IA", MARCA_SITE_HTML)
        self.assertIn("escudo-shield", MARCA_SITE_HTML)
        self.assertIn("Logo Escudo Digital IA", MARCA_SITE_HTML)
        self.assertGreaterEqual(MARCA_SITE_HTML.count("<line "), 40)
        self.assertGreaterEqual(MARCA_SITE_HTML.count("<circle "), 35)
        self.assertNotIn("<img", MARCA_SITE_HTML)

    def test_formata_classificacao_para_leitura_humana(self) -> None:
        self.assertEqual(rotulo_classificacao("baixo_risco"), "Baixo risco")
        self.assertEqual(
            rotulo_classificacao("informacao_insuficiente"),
            "Informação insuficiente",
        )

    def test_formata_confianca_com_nivel_e_valor_normalizado(self) -> None:
        texto, valor = formatar_confianca(0.92)

        self.assertEqual(texto, "Alta (92%)")
        self.assertEqual(valor, 0.92)

    def test_registra_feedback_sem_receber_mensagem(self) -> None:
        chamadas = []

        mensagem = registrar_feedback_analise("util", chamadas.append)

        self.assertEqual(chamadas, ["util"])
        self.assertIn("sem salvar a mensagem", mensagem)

    def test_resposta_do_aprender_contabiliza_uma_unica_vez(self) -> None:
        estado = {
            "acertos": 0,
            "respondido": False,
            "ultimo_acerto": None,
            "ultima_classificacao_esperada": None,
        }

        primeira = registrar_resposta_aprender(
            estado,
            "alto_risco",
            "alto_risco",
        )
        segunda = registrar_resposta_aprender(
            estado,
            "alto_risco",
            "alto_risco",
        )

        self.assertTrue(primeira)
        self.assertTrue(segunda)
        self.assertEqual(estado["acertos"], 1)
        self.assertTrue(estado["respondido"])

    def test_resposta_errada_do_aprender_nao_incrementa_acertos(self) -> None:
        estado = {
            "acertos": 2,
            "respondido": False,
            "ultimo_acerto": None,
            "ultima_classificacao_esperada": None,
        }

        acertou = registrar_resposta_aprender(
            estado,
            "baixo_risco",
            "alto_risco",
        )

        self.assertFalse(acertou)
        self.assertEqual(estado["acertos"], 2)
        self.assertEqual(estado["ultima_classificacao_esperada"], "alto_risco")

    def test_feedback_do_aprender_indica_resposta_concluida(self) -> None:
        self.assertIn(
            "registrada",
            mensagem_feedback_aprender(True, "alto_risco"),
        )
        self.assertIn(
            "Resposta esperada: Alto risco.",
            mensagem_feedback_aprender(False, "alto_risco"),
        )

    def test_rotulo_de_avanco_do_aprender_guia_ultima_questao(self) -> None:
        self.assertEqual(rotulo_avanco_aprender(0, 10), "Próximo exercício")
        self.assertEqual(rotulo_avanco_aprender(9, 10), "Ver resultado final")

    def test_rotulo_item_aprender_deixa_codigos_legiveis(self) -> None:
        self.assertEqual(
            rotulo_item_aprender("pedido_de_senha_ou_codigo"),
            "Pedido de senha ou código",
        )
        self.assertEqual(
            rotulo_item_aprender("novo_sinal_teste"),
            "Novo sinal teste",
        )

    def test_explicacao_do_aprender_vira_lista_de_topicos(self) -> None:
        self.assertEqual(
            dividir_explicacao_aprender("Primeiro ponto. Segundo ponto!"),
            ["Primeiro ponto.", "Segundo ponto!"],
        )

    def test_detalhes_aprender_destacam_conteudo_pos_resposta(self) -> None:
        html = detalhes_aprender_html(
            {
                "mensagem": "<script>alert('x')</script>",
                "sinais": ["urgencia", "pedido_de_senha_ou_codigo"],
                "explicacao": "A mensagem pressiona o usuário. Ela pede ação rápida.",
                "recomendacoes": ["nao_clicar", "usar_canal_oficial"],
            }
        )

        self.assertIn("escudo-learning-details", html)
        self.assertIn("escudo-learning-topic-list", html)
        self.assertIn("escudo-learning-topic-item", html)
        self.assertEqual(html.count('class="escudo-learning-topic-list"'), 4)
        self.assertEqual(html.count('class="escudo-learning-topic-item'), 7)
        self.assertIn("Mensagem analisada", html)
        self.assertIn("Sinais identificados", html)
        self.assertIn("Por que essa era a resposta?", html)
        self.assertIn("Recomendações", html)
        self.assertIn("Urgência", html)
        self.assertIn("Pedido de senha ou código", html)
        self.assertIn("Não clicar", html)
        self.assertIn("Usar canal oficial", html)
        self.assertIn("A mensagem pressiona o usuário.", html)
        self.assertIn("Ela pede ação rápida.", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertLess(
            html.index("Mensagem analisada"),
            html.index("Por que essa era a resposta?"),
        )
        self.assertLess(
            html.index("Por que essa era a resposta?"),
            html.index("Sinais identificados"),
        )
        self.assertLess(
            html.index("Sinais identificados"),
            html.index("Recomendações"),
        )

    def test_avancar_exercicio_reabre_resposta(self) -> None:
        estado = {
            "indice_exercicio": 3,
            "respondido": True,
            "ultimo_acerto": True,
            "ultima_classificacao_esperada": "moderado",
        }

        avancar_exercicio(estado)

        self.assertEqual(estado["indice_exercicio"], 4)
        self.assertFalse(estado["respondido"])
        self.assertIsNone(estado["ultimo_acerto"])
        self.assertIsNone(estado["ultima_classificacao_esperada"])


if __name__ == "__main__":
    unittest.main()
