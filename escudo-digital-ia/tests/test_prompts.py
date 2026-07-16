"""Testes das versões de prompt."""

import unittest

from prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2
from prompts import montar_system_prompt


class PromptTests(unittest.TestCase):
    def test_prompt_v1_permanece_preservado(self) -> None:
        self.assertEqual(SYSTEM_PROMPT_V1, montar_system_prompt())
        self.assertNotIn("Prompt V2", SYSTEM_PROMPT_V1)

    def test_prompt_v2_adiciona_regras_sem_remover_json(self) -> None:
        self.assertNotEqual(SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2)
        self.assertIn("aplicativo, portal, site ou canal oficial", SYSTEM_PROMPT_V2)
        self.assertIn("oportunidades de trabalho", SYSTEM_PROMPT_V2)
        self.assertIn("mensagens genéricas ou vagas", SYSTEM_PROMPT_V2)
        self.assertIn('"classificacao"', SYSTEM_PROMPT_V2)
        self.assertIn("baixo_risco", SYSTEM_PROMPT_V2)
        self.assertIn("moderado", SYSTEM_PROMPT_V2)
        self.assertIn("alto_risco", SYSTEM_PROMPT_V2)
        self.assertIn("informacao_insuficiente", SYSTEM_PROMPT_V2)


if __name__ == "__main__":
    unittest.main()
