import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildHistoryReportDownloadUrl,
  triggerHistoryReportDownload,
} from '../src/components/historyReportDownload.js'

test('buildHistoryReportDownloadUrl trims the base URL and encodes report IDs', () => {
  assert.equal(
    buildHistoryReportDownloadUrl('report alpha/1', 'https://example.test/base/'),
    'https://example.test/base/api/report/report%20alpha%2F1/download'
  )
})

test('triggerHistoryReportDownload creates and clicks a temporary anchor', () => {
  const appended = []
  const removed = []
  const anchor = {
    href: '',
    download: '',
    rel: '',
    style: {},
    clicked: false,
    click() {
      this.clicked = true
    },
    remove() {
      removed.push(this.download)
    },
  }
  const documentRef = {
    body: {
      appendChild(node) {
        appended.push(node)
      },
    },
    createElement(tag) {
      assert.equal(tag, 'a')
      return anchor
    },
  }

  const downloaded = triggerHistoryReportDownload('report_123', {
    baseURL: 'https://mirofish.example.test/',
    documentRef,
  })

  assert.equal(downloaded, true)
  assert.equal(anchor.href, 'https://mirofish.example.test/api/report/report_123/download')
  assert.equal(anchor.download, 'report_123.md')
  assert.equal(anchor.rel, 'noopener')
  assert.equal(anchor.clicked, true)
  assert.deepEqual(appended, [anchor])
  assert.deepEqual(removed, ['report_123.md'])
})

test('triggerHistoryReportDownload returns false when report ID or document is unavailable', () => {
  assert.equal(triggerHistoryReportDownload('', { baseURL: 'https://example.test', documentRef: null }), false)
  assert.equal(triggerHistoryReportDownload('report_123', { baseURL: 'https://example.test', documentRef: null }), false)
})
