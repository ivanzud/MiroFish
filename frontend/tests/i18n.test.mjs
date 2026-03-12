import test from 'node:test'
import assert from 'node:assert/strict'

import { getStoredLocale, normalizeLocale, resolveBrowserLocale } from '../src/i18n/index.js'

const originalWindow = global.window

test.afterEach(() => {
  if (originalWindow === undefined) {
    delete global.window
  } else {
    global.window = originalWindow
  }
})

test('normalizeLocale maps supported language tags to app locales', () => {
  assert.equal(normalizeLocale('en-US'), 'en')
  assert.equal(normalizeLocale('zh-CN'), 'zh')
  assert.equal(normalizeLocale(' fr-FR '), null)
})

test('resolveBrowserLocale falls back to zh when browser language is unsupported', () => {
  assert.equal(resolveBrowserLocale('fr-FR'), 'zh')
  assert.equal(resolveBrowserLocale(undefined), 'zh')
})

test('getStoredLocale prefers an explicit stored locale', () => {
  global.window = {
    localStorage: {
      getItem(key) {
        assert.equal(key, 'mirofish-locale')
        return 'zh'
      },
    },
    navigator: {
      language: 'en-US',
    },
  }

  assert.equal(getStoredLocale(), 'zh')
})

test('getStoredLocale uses the browser locale on first run when no preference is saved', () => {
  global.window = {
    localStorage: {
      getItem() {
        return null
      },
    },
    navigator: {
      language: 'en-US',
    },
  }

  assert.equal(getStoredLocale(), 'en')
})

test('getStoredLocale falls back to zh when storage fails and browser locale is unsupported', () => {
  global.window = {
    localStorage: {
      getItem() {
        throw new Error('storage unavailable')
      },
    },
    navigator: {
      language: 'fr-FR',
    },
  }

  assert.equal(getStoredLocale(), 'zh')
})
