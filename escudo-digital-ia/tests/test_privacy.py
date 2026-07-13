"""Testes da anonimização de CPF e telefone."""

import unittest

from privacy import anonimizar_cpf_telefone


class AnonimizarCpfTelefoneTests(unittest.TestCase):
    def test_anonimiza_cpf_formatado(self) -> None:
        texto = "O CPF fictício é 123.456.789-00."

        resultado = anonimizar_cpf_telefone(texto)

        self.assertEqual(resultado, "O CPF fictício é [CPF OCULTADO].")
        self.assertNotIn("123.456.789-00", resultado)

    def test_anonimiza_cpf_sem_pontuacao(self) -> None:
        resultado = anonimizar_cpf_telefone("CPF fictício: 12345678900")

        self.assertEqual(resultado, "CPF fictício: [CPF OCULTADO]")

    def test_anonimiza_celular_com_ddd(self) -> None:
        resultado = anonimizar_cpf_telefone("Ligue para (62) 99999-9999.")

        self.assertEqual(resultado, "Ligue para [TELEFONE OCULTADO].")

    def test_anonimiza_telefone_fixo(self) -> None:
        resultado = anonimizar_cpf_telefone("Telefone: (11) 3333-4444")

        self.assertEqual(resultado, "Telefone: [TELEFONE OCULTADO]")

    def test_anonimiza_telefone_com_codigo_do_pais(self) -> None:
        resultado = anonimizar_cpf_telefone("Contato: +55 (21) 98888-7777")

        self.assertEqual(resultado, "Contato: [TELEFONE OCULTADO]")

    def test_anonimiza_varios_dados_no_mesmo_texto(self) -> None:
        texto = (
            "CPF 123.456.789-00, celular (62) 99999-9999 "
            "e telefone (11) 3333-4444."
        )

        resultado = anonimizar_cpf_telefone(texto)

        self.assertEqual(resultado.count("[CPF OCULTADO]"), 1)
        self.assertEqual(resultado.count("[TELEFONE OCULTADO]"), 2)
        self.assertNotIn("123.456.789-00", resultado)
        self.assertNotIn("99999-9999", resultado)
        self.assertNotIn("3333-4444", resultado)

    def test_preserva_texto_sem_dados_reconhecidos(self) -> None:
        texto = "Mensagem fictícia sem CPF ou telefone."

        self.assertEqual(anonimizar_cpf_telefone(texto), texto)

    def test_nao_anonimiza_numero_dentro_de_sequencia_maior(self) -> None:
        texto = "Identificador: 912345678900"

        self.assertEqual(anonimizar_cpf_telefone(texto), texto)

    def test_rejeita_entrada_que_nao_seja_string(self) -> None:
        with self.assertRaisesRegex(TypeError, "texto deve ser uma string"):
            anonimizar_cpf_telefone(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
