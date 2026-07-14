"""Testes das regras locais de segurança."""

import unittest

from safety import LIMITE_CARACTERES_MENSAGEM, validar_mensagem_usuario


class SafetyTests(unittest.TestCase):
    def test_aceita_mensagem_valida_e_remove_espacos(self) -> None:
        resultado = validar_mensagem_usuario("  mensagem fictícia  ")

        self.assertEqual(resultado, "mensagem fictícia")

    def test_rejeita_entrada_que_nao_seja_string(self) -> None:
        with self.assertRaisesRegex(TypeError, "mensagem deve ser uma string"):
            validar_mensagem_usuario(None)  # type: ignore[arg-type]

    def test_rejeita_mensagem_vazia(self) -> None:
        with self.assertRaisesRegex(ValueError, "Digite uma mensagem fictícia"):
            validar_mensagem_usuario("   ")

    def test_rejeita_mensagem_grande_demais(self) -> None:
        mensagem = "a" * (LIMITE_CARACTERES_MENSAGEM + 1)

        with self.assertRaisesRegex(ValueError, "grande demais"):
            validar_mensagem_usuario(mensagem)


if __name__ == "__main__":
    unittest.main()
