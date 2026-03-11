import test from 'node:test'
import assert from 'node:assert/strict'

import { resolveBaseURL } from '../src/api/baseUrl.js'

test('prefers explicit VITE_API_BASE_URL', () => {
  assert.equal(
    resolveBaseURL({
      envBaseURL: '  https://api.example.com/v1  ',
      location: new URL('http://localhost:3000')
    }),
    'https://api.example.com/v1'
  )
})

test('rewrites the documented frontend port 3000 to backend port 5001', () => {
  assert.equal(
    resolveBaseURL({
      location: new URL('http://127.0.0.1:3000/process')
    }),
    'http://127.0.0.1:5001'
  )
})

test('keeps same-origin fallback for reverse-proxied deployments', () => {
  assert.equal(
    resolveBaseURL({
      location: new URL('https://mirofish.example.com/app')
    }),
    'https://mirofish.example.com'
  )
})
