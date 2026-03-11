import test from 'node:test'
import assert from 'node:assert/strict'

import { formatApiError } from '../src/api/errors.js'

const t = (key, params = {}) => {
  const messages = {
    'process.unknownError': 'Unknown error',
    'process.requestTimeout': 'Timed out',
    'process.backendUnavailable': `Backend unavailable at ${params.apiBase}`
  }
  return messages[key]
}

test('returns backend error payload when present', () => {
  const message = formatApiError({
    err: {
      message: 'Error',
      response: {
        data: {
          error: '后端配置不完整: ZEP_API_KEY 未配置'
        }
      }
    },
    t,
    resolveBaseURL: () => 'http://localhost:5001',
    locationOrigin: 'http://localhost:3000'
  })

  assert.equal(message, '后端配置不完整: ZEP_API_KEY 未配置')
})

test('formats network errors with resolved backend url', () => {
  const message = formatApiError({
    err: { message: 'Network Error' },
    t,
    resolveBaseURL: () => 'https://api.example.test',
    locationOrigin: 'http://localhost:3000'
  })

  assert.equal(message, 'Backend unavailable at https://api.example.test')
})
