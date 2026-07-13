"""Testes de validacao da resposta estruturada da IA."""

import unittest

from validator import resposta_eh_valida, validar_resposta_ia


def resposta_valida() -> dict[str, object]:
    return {
        "classificacao": "alto_risco",
        "confianca": 0.92,
        "sinais": ["urgencia", "pedido_de_senha"],
        "recomendacoes": ["nao_clicar", "usar_canal_oficial"],
        "explicacao_simples": (
            "A mensagem cria pressao e solicita uma informacao sensivel."
        ),
        "informacao_insuficiente": False,
    }


class ValidatorTests(unittest.TestCase):
    def test_aceita_resposta_valida(self) -> None:
        resposta = resposta_valida()

        self.assertEqual(validar_resposta_ia(resposta), [])
        self.assertTrue(resposta_eh_valida(resposta))

    def test_rejeita_resposta_que_nao_seja_objeto(self) -> None:
        erros = validar_resposta_ia("texto solto")

        self.assertEqual(erros, ["resposta deve ser um objeto JSON"])

    def test_detecta_campos_ausentes(self) -> None:
        resposta = resposta_valida()
        del resposta["confianca"]
        del resposta["sinais"]

        erros = validar_resposta_ia(resposta)

        self.assertIn("campo ausente: confianca", erros)
        self.assertIn("campo ausente: sinais", erros)
        self.assertFalse(resposta_eh_valida(resposta))

    def test_rejeita_classificacao_invalida(self) -> None:
        resposta = resposta_valida()
        resposta["classificacao"] = "risco_extremo"

        self.assertIn("classificacao invalida", validar_resposta_ia(resposta))

    def test_rejeita_confianca_fora_do_intervalo(self) -> None:
        resposta = resposta_valida()
        resposta["confianca"] = 1.2

        self.assertIn(
            "confianca deve ser um numero entre 0 e 1",
            validar_resposta_ia(resposta),
        )

    def test_rejeita_confianca_booleana(self) -> None:
        resposta = resposta_valida()
        resposta["confianca"] = True

        self.assertIn(
            "confianca deve ser um numero entre 0 e 1",
            validar_resposta_ia(resposta),
        )

    def test_rejeita_sinais_que_nao_sejam_lista(self) -> None:
        resposta = resposta_valida()
        resposta["sinais"] = "urgencia"

        self.assertIn("sinais deve ser uma lista", validar_resposta_ia(resposta))

    def test_rejeita_recomendacoes_com_itens_invalidos(self) -> None:
        resposta = resposta_valida()
        resposta["recomendacoes"] = ["nao_clicar", ""]

        self.assertIn(
            "recomendacoes deve conter apenas textos nao vazios",
            validar_resposta_ia(resposta),
        )

    def test_rejeita_explicacao_vazia(self) -> None:
        resposta = resposta_valida()
        resposta["explicacao_simples"] = "   "

        self.assertIn(
            "explicacao_simples deve ser um texto nao vazio",
            validar_resposta_ia(resposta),
        )

    def test_rejeita_informacao_insuficiente_nao_booleana(self) -> None:
        resposta = resposta_valida()
        resposta["informacao_insuficiente"] = "false"

        self.assertIn(
            "informacao_insuficiente deve ser booleano",
            validar_resposta_ia(resposta),
        )


if __name__ == "__main__":
    unittest.main()
