import test from 'node:test'
import assert from 'node:assert/strict'

import { truncateFilename } from '../src/components/historyFormatters.js'

test('truncateFilename returns the localized fallback when filename is missing', () => {
  assert.equal(truncateFilename('', 20, 'Unknown file'), 'Unknown file')
  assert.equal(truncateFilename(null, 20, '未知文件'), '未知文件')
})

test('truncateFilename preserves short filenames', () => {
  assert.equal(truncateFilename('notes.md', 20, 'Unknown file'), 'notes.md')
})

test('truncateFilename truncates long filenames while preserving the extension', () => {
  assert.equal(
    truncateFilename('very-long-simulation-notes.md', 20, 'Unknown file'),
    'very-long-simu....md'
  )
})
