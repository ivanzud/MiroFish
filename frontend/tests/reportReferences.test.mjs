import test from 'node:test'
import assert from 'node:assert/strict'

import { resolveReportReferenceValue } from '../src/components/reportReferences.js'

test('resolveReportReferenceValue preserves real report IDs', () => {
  assert.equal(resolveReportReferenceValue('report_123', 'Not available yet'), 'report_123')
})

test('resolveReportReferenceValue falls back to localized unavailable copy for blank IDs', () => {
  assert.equal(resolveReportReferenceValue('', 'Not available yet'), 'Not available yet')
  assert.equal(resolveReportReferenceValue('   ', '暂未生成'), '暂未生成')
  assert.equal(resolveReportReferenceValue(null, 'Not available yet'), 'Not available yet')
})
