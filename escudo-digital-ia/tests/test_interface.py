"""Testes da apresentação da interface de terminal."""

import unittest

from interface import AVISO_SEGURANCA, formatar_resultado, texto_introducao


class InterfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resultado = {
            "classificacao": "alto_risco",
            "confianca": 0.92,
            "sinais": ["urgencia", "pedido_de_senha_ou_codigo"],
            "recomendacoes": [
                "nao_enviar_senhas_ou_codigos",
                "usar_canal_oficial",
            ],
            "explicacao_simples": "A mensagem pressiona o usuário.",
            "informacao_insuficiente": False,
        }

    def test_formata_resultado_para_leitura_humana(self) -> None:
        texto = formatar_resultado(self.resultado)

        self.assertIn("Classificação: ALTO RISCO", texto)
        self.assertIn("Certeza da análise: 92%", texto)
        self.assertIn(
            "não se a mensagem é confiável",
            texto,
        )
        self.assertIn("- Urgência", texto)
        self.assertIn("- Não envie senhas ou códigos", texto)
        self.assertIn("A mensagem pressiona o usuário.", texto)

    def test_formata_listas_vazias(self) -> None:
        self.resultado["sinais"] = []
        self.resultado["recomendacoes"] = []

        texto = formatar_resultado(self.resultado)

        self.assertEqual(texto.count("- Nenhum item identificado"), 2)

    def test_exibe_aviso_antes_e_depois_da_analise(self) -> None:
        self.assertIn(AVISO_SEGURANCA, texto_introducao())
        self.assertIn(AVISO_SEGURANCA, formatar_resultado(self.resultado))


if __name__ == "__main__":
    unittest.main()
