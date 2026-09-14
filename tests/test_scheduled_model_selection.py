#!/usr/bin/env python3
"""No network. Check both daily call sites and generation payload compatibility."""
import ast
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from channels import auto_reply


class ModelSelectionTests(unittest.TestCase):
    def test_review_and_maintainer_use_openai_override(self):
        tree = ast.parse((ROOT/'.github/scripts/runner.py').read_text())
        expressions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == 'model' and isinstance(kw.value, ast.Call):
                        call = kw.value
                        if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == 'OPENAI_MODEL':
                            expressions.append(ast.Expression(call))
        self.assertEqual(len(expressions), 2, 'both review and maintainer must use override')
        for expr in expressions:
            with patch.dict(os.environ, {'OPENAI_MODEL': 'test-explicit-model'}, clear=True):
                self.assertEqual(eval(compile(expr, '<model>', 'eval'), {'os': os}), 'test-explicit-model')
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(eval(compile(expr, '<model>', 'eval'), {'os': os}), 'gpt-6-astra')

    def test_autonomous_worker_has_independent_model_override(self):
        workflow = (ROOT/'.github/workflows/autonomous-goose-tarik.yml').read_text()
        self.assertIn(
            "GOOSE_MODEL: ${{ vars.TARIK_AUTONOMOUS_MODEL || vars.OPENAI_MODEL || 'gpt-6-astra' }}",
            workflow,
        )
        self.assertIn('**State:** retired', (ROOT/'recipes/autonomous-goose/tarik-mission.md').read_text())

    def test_astra_reply_uses_modern_token_parameter(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test-only','OPENAI_MODEL':'gpt-6-astra'}, clear=True), \
             patch.object(auto_reply, '_load_local_env_fallbacks'), \
             patch.object(auto_reply, '_http', return_value={'choices':[{'message':{'content':'OK'}}]}) as request:
            self.assertEqual(auto_reply.call_amigo_llm('tarik', 'System', 'Prompt'), 'OK')
            payload = request.call_args.args[2]
            self.assertEqual(payload['model'], 'gpt-6-astra')
            self.assertEqual(payload['max_completion_tokens'], 1200)
            self.assertNotIn('max_tokens', payload)
            self.assertNotIn('temperature', payload)

    def test_legacy_model_override_remains_compatible(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test-only','OPENAI_MODEL':'gpt-4o'}, clear=True), \
             patch.object(auto_reply, '_load_local_env_fallbacks'), \
             patch.object(auto_reply, '_http', return_value={'choices':[{'message':{'content':'OK'}}]}) as request:
            auto_reply.call_amigo_llm('tarik', 'System', 'Prompt')
            payload = request.call_args.args[2]
            self.assertEqual(payload['max_tokens'], 1200)
            self.assertNotIn('max_completion_tokens', payload)

    def test_retired_mission_stays_retired(self):
        self.assertIn('**State:** retired', (ROOT/'recipes/autonomous-goose/tarik-mission.md').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
