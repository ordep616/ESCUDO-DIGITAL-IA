"""Testes do avaliador sem chamadas externas à API."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluator import avaliar_caso, calcular_metricas, carregar_casos
from evaluator import caminho_resultados_prompt, classificar_resultado
from evaluator import executar_avaliacao, filtrar_casos_por_ids
from evaluator import salvar_resultados, selecionar_prompt
from prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2


RESPOSTA_VALIDA = {
    "classificacao": "alto_risco",
    "confianca": 0.9,
    "sinais": ["urgencia"],
    "recomendacoes": ["usar_canal_oficial"],
    "explicacao_simples": "Mensagem suspeita.",
    "informacao_insuficiente": False,
}


class EvaluatorTests(unittest.TestCase):
    def test_carrega_os_trinta_casos_reais(self) -> None:
        casos = carregar_casos()

        self.assertEqual(len(casos), 30)
        self.assertEqual(casos[0]["id"], "caso_01")
        self.assertEqual(casos[-1]["id"], "caso_30")

    def test_rejeita_arquivo_com_json_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "casos.json"
            caminho.write_text("não é json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                carregar_casos(caminho)

    def test_classifica_acerto_e_tipos_de_erro(self) -> None:
        self.assertEqual(
            classificar_resultado("alto_risco", "alto_risco"),
            "acerto",
        )
        self.assertEqual(
            classificar_resultado("baixo_risco", "alto_risco"),
            "falso_positivo",
        )
        self.assertEqual(
            classificar_resultado("alto_risco", "baixo_risco"),
            "falso_negativo",
        )
        self.assertEqual(
            classificar_resultado("moderado", "baixo_risco"),
            "erro_classificacao",
        )
        self.assertEqual(
            classificar_resultado("moderado", None, json_valido=False),
            "resposta_invalida",
        )

    def test_avalia_resposta_valida_sem_copiar_mensagem(self) -> None:
        caso = {
            "id": "caso_teste",
            "mensagem": "Mensagem que não deve aparecer no resultado.",
            "classificacao_esperada": "alto_risco",
        }

        resultado = avaliar_caso(caso, RESPOSTA_VALIDA)

        self.assertEqual(resultado["resultado"], "acerto")
        self.assertTrue(resultado["json_valido"])
        self.assertNotIn("mensagem", resultado)

    def test_avalia_resposta_invalida(self) -> None:
        caso = {
            "id": "caso_teste",
            "classificacao_esperada": "alto_risco",
        }

        resultado = avaliar_caso(caso, {"classificacao": "alto_risco"})

        self.assertEqual(resultado["resultado"], "resposta_invalida")
        self.assertFalse(resultado["json_valido"])
        self.assertTrue(resultado["erros_validacao"])

    def test_calcula_metricas(self) -> None:
        resultados = [
            {"resultado": "acerto"},
            {"resultado": "acerto"},
            {"resultado": "falso_positivo"},
            {"resultado": "falso_negativo"},
            {"resultado": "resposta_invalida"},
            {"resultado": "erro_classificacao"},
        ]

        metricas = calcular_metricas(resultados)

        self.assertEqual(metricas["total_casos"], 6)
        self.assertEqual(metricas["acertos"], 2)
        self.assertEqual(metricas["erros"], 4)
        self.assertEqual(metricas["falsos_positivos"], 1)
        self.assertEqual(metricas["falsos_negativos"], 1)
        self.assertEqual(metricas["respostas_invalidas"], 1)
        self.assertEqual(metricas["outros_erros"], 1)
        self.assertEqual(metricas["taxa_acerto"], 33.33)

    def test_calcula_metricas_de_lista_vazia(self) -> None:
        metricas = calcular_metricas([])

        self.assertEqual(metricas["total_casos"], 0)
        self.assertEqual(metricas["taxa_acerto"], 0.0)

    def test_salva_resultados_sem_mensagem(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "resultados.json"
            resultados = [
                {
                    "id": "caso_teste",
                    "esperado": "alto_risco",
                    "obtido": "alto_risco",
                    "json_valido": True,
                    "resultado": "acerto",
                    "erros_validacao": [],
                    "mensagem": "ESTE TEXTO NÃO PODE SER SALVO",
                }
            ]

            salvar_resultados(resultados, "v1", caminho)
            conteudo = caminho.read_text(encoding="utf-8")
            dados = json.loads(conteudo)

        self.assertNotIn("ESTE TEXTO NÃO PODE SER SALVO", conteudo)
        self.assertNotIn("mensagem", dados["resultados"][0])
        self.assertEqual(dados["versao_prompt"], "v1")
        self.assertEqual(dados["metricas"]["acertos"], 1)

    def test_seleciona_prompt_e_caminho_de_resultado_por_versao(self) -> None:
        self.assertEqual(selecionar_prompt("v1"), SYSTEM_PROMPT_V1)
        self.assertEqual(selecionar_prompt("v2"), SYSTEM_PROMPT_V2)
        self.assertEqual(
            caminho_resultados_prompt("v2").name,
            "resultados_prompt_v2.json",
        )

    def test_filtra_casos_por_ids(self) -> None:
        casos = [
            {
                "id": "caso_01",
                "mensagem": "a",
                "classificacao_esperada": "baixo_risco",
            },
            {
                "id": "caso_02",
                "mensagem": "b",
                "classificacao_esperada": "moderado",
            },
        ]

        filtrados = filtrar_casos_por_ids(casos, ["caso_02"])

        self.assertEqual([caso["id"] for caso in filtrados], ["caso_02"])

    def test_rejeita_id_de_caso_inexistente(self) -> None:
        casos = [
            {
                "id": "caso_01",
                "mensagem": "a",
                "classificacao_esperada": "baixo_risco",
            },
        ]

        with self.assertRaisesRegex(ValueError, "casos não encontrados"):
            filtrar_casos_por_ids(casos, ["caso_99"])

    @patch("evaluator.registrar_consumo_basico")
    @patch("evaluator.analisar_mensagem")
    def test_executa_avaliacao_v2_sem_chamada_real_a_api(
        self,
        analisar,
        registrar_consumo,
    ) -> None:
        resposta_textual = dict(RESPOSTA_VALIDA)
        resposta_textual["classificacao"] = "alto_risco"
        analisar.return_value = json.dumps(resposta_textual)

        with tempfile.TemporaryDirectory() as diretorio:
            diretorio_path = Path(diretorio)
            casos_path = diretorio_path / "casos.json"
            resultados_path = diretorio_path / "resultados_prompt_v2.json"
            casos_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "caso_15",
                            "mensagem": (
                                "Você foi selecionado para uma vaga. "
                                "Contato: teste@example.com"
                            ),
                            "classificacao_esperada": "alto_risco",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            dados = executar_avaliacao(
                "v2",
                caminho_casos=casos_path,
                caminho_resultados=resultados_path,
                saida=lambda _texto: None,
            )
            resultado_foi_salvo = resultados_path.exists()

        self.assertEqual(dados["versao_prompt"], "v2")
        self.assertEqual(dados["metricas"]["total_casos"], 1)
        self.assertEqual(analisar.call_args.args[1], SYSTEM_PROMPT_V2)
        mensagem_anonimizada = (
            "Você foi selecionado para uma vaga. "
            "Contato: [E-MAIL OCULTADO]"
        )
        self.assertEqual(analisar.call_args.args[0], mensagem_anonimizada)
        registrar_consumo.assert_called_once_with(mensagem_anonimizada)
        self.assertTrue(resultado_foi_salvo)

    def test_rejeita_versao_de_prompt_invalida(self) -> None:
        with self.assertRaisesRegex(ValueError, "versão do prompt"):
            salvar_resultados([], "v3", "/tmp/nao_deve_ser_criado.json")


if __name__ == "__main__":
    unittest.main()
