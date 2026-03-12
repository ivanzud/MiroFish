import test from 'node:test'
import assert from 'node:assert/strict'

import {
  formatMainViewGraphRefreshLog,
  formatMainViewStepLog,
} from '../src/views/mainViewLogMessages.js'

const t = (key, params = {}) => `${key}:${JSON.stringify(params)}`

test('main view step logs localize forward and backward workflow transitions', () => {
  assert.equal(
    formatMainViewStepLog('enter', 2, 'Environment Setup', t),
    'mainView.logs.enterStep:{"step":2,"name":"Environment Setup"}'
  )

  assert.equal(
    formatMainViewStepLog('back', 1, 'Graph Build', t),
    'mainView.logs.returnStep:{"step":1,"name":"Graph Build"}'
  )
})

test('main view graph refresh log keeps translated labels and counts centralized', () => {
  assert.equal(
    formatMainViewGraphRefreshLog(12, 34, t),
    'mainView.logs.graphDataRefreshed:{"nodeCount":12,"edgeCount":34}'
  )
})
