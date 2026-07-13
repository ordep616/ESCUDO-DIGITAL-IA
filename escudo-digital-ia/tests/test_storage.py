"""Testes das metricas de consumo permitidas."""

import json
import tempfile
import unittest
from pathlib import Path

from storage import carregar_consumo, calcular_tamanho_entrada
from storage import registrar_consumo_basico


class ConsumoBasicoTests(unittest.TestCase):
    def test_carregar_consumo_ausente_retorna_metricas_zeradas(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "consumo.json"

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
            caminho = Path(diretorio) / "consumo.json"

            consumo = registrar_consumo_basico("abcde", caminho)
            conteudo_salvo = caminho.read_text(encoding="utf-8")
            dados_salvos = json.loads(conteudo_salvo)

        self.assertEqual(consumo["total_chamadas"], 1)
        self.assertEqual(consumo["total_caracteres_entrada"], 5)
        self.assertEqual(consumo["total_tokens_aproximados"], 2)
        self.assertEqual(consumo["media_caracteres_por_chamada"], 5)
        self.assertEqual(consumo["ultima_entrada_caracteres"], 5)
        self.assertEqual(dados_salvos, consumo)
        self.assertNotIn("abcde", conteudo_salvo)

    def test_acumula_multiplas_chamadas(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "consumo.json"

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
