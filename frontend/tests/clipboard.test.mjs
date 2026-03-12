import test from 'node:test'
import assert from 'node:assert/strict'

import { copyText } from '../src/utils/clipboard.js'

test('copyText writes to the provided clipboard object', async () => {
  const calls = []
  const clipboard = {
    async writeText(value) {
      calls.push(value)
    },
  }

  const copied = await copyText('report_123', clipboard)

  assert.equal(copied, true)
  assert.deepEqual(calls, ['report_123'])
})

test('copyText returns false when the value is blank', async () => {
  const clipboard = {
    async writeText() {
      throw new Error('should not be called')
    },
  }

  await assert.doesNotReject(async () => {
    const copied = await copyText('', clipboard)
    assert.equal(copied, false)
  })
})

test('copyText returns false when clipboard support is unavailable', async () => {
  const copied = await copyText('sim_123', null)
  assert.equal(copied, false)
})
