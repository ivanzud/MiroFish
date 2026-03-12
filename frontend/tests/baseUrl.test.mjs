import test from 'node:test'
import assert from 'node:assert/strict'

import {
  API_BASE_OVERRIDE_KEY,
  clearStoredBaseURL,
  getStoredBaseURL,
  resolveBaseURL,
  setStoredBaseURL
} from '../src/api/baseUrl.js'

test('prefers explicit VITE_API_BASE_URL', () => {
  assert.equal(
    resolveBaseURL({
      envBaseURL: '  https://api.example.com/v1  ',
      location: new URL('http://localhost:3000')
    }),
    'https://api.example.com/v1'
  )
})

test('prefers persisted runtime override over env and location fallback', () => {
  assert.equal(
    resolveBaseURL({
      runtimeBaseURL: ' https://runtime.example.com/api/ ',
      envBaseURL: 'https://env.example.com/api',
      location: new URL('http://localhost:3000')
    }),
    'https://runtime.example.com/api'
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

test('persists a normalized runtime override in storage', () => {
  const storage = new Map()
  const mockStorage = {
    getItem(key) {
      return storage.has(key) ? storage.get(key) : null
    },
    setItem(key, value) {
      storage.set(key, value)
    },
    removeItem(key) {
      storage.delete(key)
    }
  }

  const savedValue = setStoredBaseURL(' https://api.example.com/root/ ', mockStorage)

  assert.equal(savedValue, 'https://api.example.com/root')
  assert.equal(storage.get(API_BASE_OVERRIDE_KEY), 'https://api.example.com/root')
  assert.equal(getStoredBaseURL(mockStorage), 'https://api.example.com/root')

  clearStoredBaseURL(mockStorage)

  assert.equal(getStoredBaseURL(mockStorage), '')
  assert.equal(storage.has(API_BASE_OVERRIDE_KEY), false)
})
