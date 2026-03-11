import test from 'node:test'
import assert from 'node:assert/strict'

import { buildBackendDiagnosticModel } from '../src/components/apiConfigDiagnostics.js'

const t = (key) => {
  const messages = {
    'common.none': 'None',
    'apiConfig.diagnostics.configured': 'Backend config detected',
    'apiConfig.diagnostics.incomplete': 'Backend config needs attention',
    'apiConfig.diagnostics.modeLabel': 'Backend mode',
    'apiConfig.diagnostics.sourceLabel': 'Resolved config source',
    'apiConfig.diagnostics.envLabel': 'Resolved env vars',
    'apiConfig.diagnostics.baseUrlLabel': 'Backend LLM base URL',
    'apiConfig.diagnostics.modelLabel': 'Backend model',
    'apiConfig.diagnostics.modeOpenAICompatible': 'OpenAI-compatible',
    'apiConfig.diagnostics.sourceOpenAIAliases': 'Direct OPENAI_* aliases',
    'apiConfig.diagnostics.sourceProjectAliases': 'Project LLM_* aliases',
    'apiConfig.diagnostics.sourceUnknown': 'Not resolved',
  }

  return messages[key]
}

test('buildBackendDiagnosticModel highlights direct OPENAI alias resolution', () => {
  const diagnostic = buildBackendDiagnosticModel({
    summary: {
      llm: {
        configured: true,
        backend_mode: 'openai_compatible',
        base_url: 'https://api.openai.com/v1',
        model: 'gpt-4.1-mini',
        sources: {
          api_key_env: 'OPENAI_API_KEY',
          base_url_env: 'OPENAI_API_BASE_URL',
          model_env: 'OPENAI_MODEL',
          uses_openai_aliases: true,
          uses_project_aliases: false,
        },
      },
    },
    validation: {
      is_valid: true,
    },
  }, t)

  assert.equal(diagnostic.tone, 'ready')
  assert.equal(diagnostic.headline, 'Backend config detected')
  assert.deepEqual(diagnostic.rows, [
    { label: 'Backend mode', value: 'OpenAI-compatible' },
    { label: 'Resolved config source', value: 'Direct OPENAI_* aliases' },
    { label: 'Resolved env vars', value: 'OPENAI_API_KEY / OPENAI_API_BASE_URL / OPENAI_MODEL' },
    { label: 'Backend LLM base URL', value: 'https://api.openai.com/v1' },
    { label: 'Backend model', value: 'gpt-4.1-mini' },
  ])
})

test('buildBackendDiagnosticModel falls back cleanly for project aliases and missing values', () => {
  const diagnostic = buildBackendDiagnosticModel({
    summary: {
      llm: {
        configured: false,
        sources: {
          uses_project_aliases: true,
          uses_openai_aliases: false,
        },
      },
    },
    validation: {
      is_valid: false,
    },
  }, t)

  assert.equal(diagnostic.tone, 'warning')
  assert.equal(diagnostic.headline, 'Backend config needs attention')
  assert.deepEqual(diagnostic.rows, [
    { label: 'Backend mode', value: 'None' },
    { label: 'Resolved config source', value: 'Project LLM_* aliases' },
    { label: 'Resolved env vars', value: 'None' },
    { label: 'Backend LLM base URL', value: 'None' },
    { label: 'Backend model', value: 'None' },
  ])
})
