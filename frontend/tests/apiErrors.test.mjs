import test from 'node:test'
import assert from 'node:assert/strict'

import { formatApiError } from '../src/api/errors.js'

const t = (key, params = {}) => {
  const messages = {
    'process.unknownError': 'Unknown error',
    'process.requestTimeout': 'Request timed out',
    'process.backendUnavailable': 'Backend unavailable at {apiBase}',
    'process.backendConfigIncomplete': 'Backend configuration is incomplete: {details}',
    'process.missingConfigKey': '{name} is not configured',
    'apiConfig.diagnostics.zepMissingNote': 'The direct LLM path is configured, but Step 1 graph build and graph-backed report tools still require ZEP_API_KEY until a non-Zep backend is landed.',
  }

  let message = messages[key]
  for (const [paramKey, value] of Object.entries(params)) {
    message = message.replace(`{${paramKey}}`, String(value))
  }
  return message
}

test('formatApiError appends direct-LLM capability guidance for Zep-gated report failures', () => {
  const message = formatApiError({
    err: {
      response: {
        data: {
          error: 'Backend configuration is incomplete: ZEP_API_KEY is not configured',
          data: {
            summary: {
              capabilities: {
                direct_llm: { ready: true },
                graph_report_tools: { ready: false, requires_zep: true },
              },
            },
          },
        },
      },
    },
    t,
  })

  assert.equal(
    message,
    'Backend configuration is incomplete: ZEP_API_KEY is not configured The direct LLM path is configured, but Step 1 graph build and graph-backed report tools still require ZEP_API_KEY until a non-Zep backend is landed.',
  )
})

test('formatApiError localizes nested backend config messages', () => {
  const message = formatApiError({
    err: {
      response: {
        data: {
          error: '后端配置不完整: OPENAI_API_KEY 未配置',
        },
      },
    },
    t,
  })

  assert.equal(message, 'Backend configuration is incomplete: OPENAI_API_KEY is not configured')
})

test('formatApiError resolves backend unavailable messages against the active base url', () => {
  const message = formatApiError({
    err: {
      message: 'Network Error',
    },
    t,
    resolveBaseURL: () => 'https://api.example.test',
    locationOrigin: 'http://localhost:5173',
  })

  assert.equal(message, 'Backend unavailable at https://api.example.test')
})
