"""Testes do modo Aprender."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aprender import carregar_exercicios, executar_modo_aprender


def exercicio_valido(numero: int = 1) -> dict[str, object]:
    return {
        "id": f"exercicio_{numero:02d}",
        "mensagem": "Mensagem fictícia para treino.",
        "classificacao_esperada": "alto_risco",
        "sinais": ["urgencia"],
        "explicacao": "A mensagem cria pressão e pede ação rápida.",
        "recomendacoes": ["nao_responder", "usar_canal_oficial"],
    }


def lista_dez_exercicios() -> list[dict[str, object]]:
    return [exercicio_valido(numero) for numero in range(1, 11)]


def salvar_json_temporario(dados: object, diretorio: str) -> Path:
    caminho = Path(diretorio) / "exercicios_aprender.json"
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False),
        encoding="utf-8",
    )
    return caminho


class AprenderTests(unittest.TestCase):
    def test_carrega_e_valida_dez_exercicios(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(lista_dez_exercicios(), diretorio)

            exercicios = carregar_exercicios(caminho)

        self.assertEqual(len(exercicios), 10)
        self.assertEqual(exercicios[0]["id"], "exercicio_01")
        self.assertEqual(exercicios[0]["classificacao_esperada"], "alto_risco")

    def test_carrega_base_oficial_de_exercicios(self) -> None:
        exercicios = carregar_exercicios()

        self.assertEqual(len(exercicios), 10)
        self.assertEqual(exercicios[0]["id"], "exercicio_01")

    def test_rejeita_arquivo_que_nao_seja_lista(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario({"id": "exercicio_01"}, diretorio)

            with self.assertRaisesRegex(ValueError, "deve conter uma lista"):
                carregar_exercicios(caminho)

    def test_rejeita_quantidade_diferente_de_dez(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(
                [exercicio_valido(1)],
                diretorio,
            )

            with self.assertRaisesRegex(ValueError, "exatamente 10 exercicios"):
                carregar_exercicios(caminho)

    def test_rejeita_exercicio_sem_campo_obrigatorio(self) -> None:
        exercicios = lista_dez_exercicios()
        del exercicios[0]["mensagem"]

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(exercicios, diretorio)

            with self.assertRaisesRegex(ValueError, "campo ausente"):
                carregar_exercicios(caminho)

    def test_rejeita_classificacao_esperada_invalida(self) -> None:
        exercicios = lista_dez_exercicios()
        exercicios[0]["classificacao_esperada"] = "risco_extremo"

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(exercicios, diretorio)

            with self.assertRaisesRegex(
                ValueError,
                "classificacao_esperada invalida",
            ):
                carregar_exercicios(caminho)

    def test_fluxo_educativo_mostra_resultado_final(self) -> None:
        exercicios = lista_dez_exercicios()
        respostas = iter(["alto_risco"] * 10)
        saidas = []

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(exercicios, diretorio)

            codigo = executar_modo_aprender(
                entrada=lambda _prompt: next(respostas),
                saida=saidas.append,
                caminho=caminho,
            )

        texto = "\n".join(saidas)
        self.assertEqual(codigo, 0)
        self.assertIn("Resultado: você acertou.", texto)
        self.assertIn("Sinais: urgencia", texto)
        self.assertIn("Explicação:", texto)
        self.assertIn("Recomendações: nao_responder, usar_canal_oficial", texto)
        self.assertIn("Acertos: 10/10", texto)
        self.assertIn("Aproveitamento: 100.0%", texto)

    def test_fluxo_nao_chama_api(self) -> None:
        respostas = iter(["alto_risco"] * 10)

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = salvar_json_temporario(lista_dez_exercicios(), diretorio)

            with patch("ai_service.analisar_mensagem") as analisar:
                executar_modo_aprender(
                    entrada=lambda _prompt: next(respostas),
                    saida=lambda _texto: None,
                    caminho=caminho,
                )

        analisar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
