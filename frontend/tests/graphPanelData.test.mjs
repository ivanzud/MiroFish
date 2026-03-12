import test from 'node:test'
import assert from 'node:assert/strict'

import { normalizeGraphPanelData, summarizeGraphData } from '../src/components/graphPanelData.js'

test('graph panel data collapses duplicate aliases and remaps shared edges', () => {
  const result = normalizeGraphPanelData({
    unnamedNodeLabel: 'Untitled',
    unknownNodeLabel: 'Unknown',
    graphData: {
      nodes: [
        { uuid: 'node-1', name: '美国总统特朗普', labels: ['Entity', 'Person'], attributes: { title: 'President' } },
        { uuid: 'node-2', name: '特朗普', labels: ['Entity', 'Person'], summary: 'Shorter canonical label' },
        { uuid: 'node-3', name: '美国', labels: ['Entity', 'Location'] },
      ],
      edges: [
        { source_node_uuid: 'node-1', target_node_uuid: 'node-3', fact_type: 'LEADS' },
        { source_node_uuid: 'node-2', target_node_uuid: 'node-3', fact_type: 'LEADS' },
      ],
    },
  })

  assert.deepEqual(result.nodes, [
    {
      id: 'node-2',
      name: '特朗普',
      type: 'Person',
      rawData: {
        uuid: 'node-2',
        name: '特朗普',
        labels: ['Entity', 'Person'],
        summary: 'Shorter canonical label',
        attributes: { title: 'President' },
        alias_names: ['特朗普', '美国总统特朗普'],
        merged_node_uuids: ['node-2', 'node-1'],
      },
    },
    {
      id: 'node-3',
      name: '美国',
      type: 'Location',
      rawData: {
        uuid: 'node-3',
        name: '美国',
        labels: ['Entity', 'Location'],
      },
    },
  ])

  assert.deepEqual(result.edges, [
    {
      source: 'node-2',
      target: 'node-3',
      type: 'LEADS',
      rawData: {
        source_node_uuid: 'node-2',
        target_node_uuid: 'node-3',
        fact_type: 'LEADS',
        source_name: '特朗普',
        target_name: '美国',
      },
    },
  ])

  assert.deepEqual(result.entityTypes, [
    { name: 'Person', count: 1, color: '#FF6B35' },
    { name: 'Location', count: 1, color: '#004E89' },
  ])
})

test('graph panel summary reports deduplicated node and edge counts', () => {
  const result = summarizeGraphData({
    unnamedNodeLabel: 'Untitled',
    unknownNodeLabel: 'Unknown',
    graphData: {
      nodes: [
        { uuid: 'node-1', name: '美国总统特朗普', labels: ['Entity', 'Person'] },
        { uuid: 'node-2', name: '特朗普', labels: ['Entity', 'Person'] },
        { uuid: 'node-3', name: '美国', labels: ['Entity', 'Location'] },
      ],
      edges: [
        { source_node_uuid: 'node-1', target_node_uuid: 'node-3', fact_type: 'LEADS' },
        { source_node_uuid: 'node-2', target_node_uuid: 'node-3', fact_type: 'LEADS' },
      ],
    },
  })

  assert.equal(result.nodeCount, 2)
  assert.equal(result.edgeCount, 1)
  assert.deepEqual(result.entityTypes, [
    { name: 'Person', count: 1, color: '#FF6B35' },
    { name: 'Location', count: 1, color: '#004E89' },
  ])
})
