import test from 'node:test'
import assert from 'node:assert/strict'

import { getReportPreflightBlockReason } from '../src/components/reportCapability.js'

const t = (key) => {
  const messages = {
    'apiConfig.diagnostics.zepMissingNote': 'The direct LLM path is configured, but Step 1 graph build and graph-backed report tools still require ZEP_API_KEY until a non-Zep backend is landed.',
    'apiConfig.diagnostics.capabilityNeedsExistingSimulation': 'Needs an existing simulation environment',
    'apiConfig.diagnostics.capabilityNeedsBackendConfig': 'Needs backend config',
  }

  return messages[key]
}

test('getReportPreflightBlockReason returns empty when report tools are ready', () => {
  assert.equal(getReportPreflightBlockReason({
    summary: {
      capabilities: {
        direct_llm: { ready: true },
        graph_report_tools: { ready: true, requires_zep: true },
      },
    },
  }, t), '')
})

test('getReportPreflightBlockReason returns the direct-LLM Zep warning when Step 4 is Zep-gated', () => {
  assert.equal(getReportPreflightBlockReason({
    summary: {
      capabilities: {
        direct_llm: { ready: true },
        graph_report_tools: { ready: false, requires_zep: true },
      },
    },
  }, t), 'The direct LLM path is configured, but Step 1 graph build and graph-backed report tools still require ZEP_API_KEY until a non-Zep backend is landed.')
})

test('getReportPreflightBlockReason falls back to generic backend requirements when direct LLM is not ready', () => {
  assert.equal(getReportPreflightBlockReason({
    summary: {
      capabilities: {
        direct_llm: { ready: false },
        graph_report_tools: { ready: false },
      },
    },
  }, t), 'Needs backend config')
})
