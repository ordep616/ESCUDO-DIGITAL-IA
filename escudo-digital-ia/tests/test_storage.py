"""Testes das metricas de consumo permitidas."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from storage import carregar_consumo, calcular_tamanho_entrada
from storage import registrar_consumo_basico


class ConsumoBasicoTests(unittest.TestCase):
    def test_carregar_consumo_ausente_retorna_metricas_zeradas(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "consumo.db"

            consumo = carregar_consumo(caminho)

        self.assertEqual(consumo["total_chamadas"], 0)
        self.assertEqual(consumo["total_caracteres_entrada"], 0)
        self.assertEqual(consumo["ultima_entrada_tokens_aproximados"], 0)

    def test_calcula_tamanho_de_entrada(self) -> None:
        tamanho = calcular_tamanho_entrada("abcde")

        self.assertEqual(tamanho["caracteres"], 5)
        self.assertEqual(tamanho["tokens_aproximados"], 2)

    def test_rejeita_entrada_que_nao_seja_string(self) -> None:
        with self.assertRaisesRegex(TypeError, "texto_entrada deve ser uma string"):
            calcular_tamanho_entrada(None)  # type: ignore[arg-type]

    def test_registra_consumo_sem_salvar_mensagem_integral(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "consumo.db"

            consumo = registrar_consumo_basico("abcde", caminho)
            conteudo_salvo = caminho.read_bytes()

            with sqlite3.connect(caminho) as conexao:
                registro = conexao.execute(
                    """
                    SELECT caracteres_entrada, tokens_aproximados, criado_em
                    FROM consumo
                    """
                ).fetchone()

        self.assertEqual(consumo["total_chamadas"], 1)
        self.assertEqual(consumo["total_caracteres_entrada"], 5)
        self.assertEqual(consumo["total_tokens_aproximados"], 2)
        self.assertEqual(consumo["media_caracteres_por_chamada"], 5)
        self.assertEqual(consumo["ultima_entrada_caracteres"], 5)
        self.assertIsNotNone(registro)
        self.assertEqual(registro[0], 5)
        self.assertEqual(registro[1], 2)
        self.assertTrue(registro[2])
        self.assertNotIn(b"abcde", conteudo_salvo)

    def test_acumula_multiplas_chamadas(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "consumo.db"

            registrar_consumo_basico("abcde", caminho)
            consumo = registrar_consumo_basico("abcdefgh", caminho)

        self.assertEqual(consumo["total_chamadas"], 2)
        self.assertEqual(consumo["total_caracteres_entrada"], 13)
        self.assertEqual(consumo["total_tokens_aproximados"], 4)
        self.assertEqual(consumo["media_caracteres_por_chamada"], 6.5)
        self.assertEqual(consumo["media_tokens_aproximados_por_chamada"], 2)
        self.assertEqual(consumo["ultima_entrada_caracteres"], 8)
        self.assertEqual(consumo["ultima_entrada_tokens_aproximados"], 2)


if __name__ == "__main__":
    unittest.main()
