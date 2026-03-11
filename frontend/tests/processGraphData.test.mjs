import test from 'node:test'
import assert from 'node:assert/strict'

import { mapProcessGraphData } from '../src/views/processGraphData.js'

test('process graph mapping localizes fallback node and edge labels', () => {
  const result = mapProcessGraphData({
    unnamedNodeLabel: 'Untitled',
    unknownNodeLabel: 'Unknown',
    nodes: [
      { uuid: 'node-1', name: '', labels: ['Entity', 'Person'] },
      { uuid: 'node-2', name: 'Alice', labels: ['Entity', 'Person'] },
    ],
    edges: [
      { source_node_uuid: 'node-1', target_node_uuid: 'node-2', fact_type: 'KNOWS' },
      { source_node_uuid: 'node-3', target_node_uuid: 'node-2', fact_type: 'IGNORED' },
    ],
  })

  assert.deepEqual(result.nodes, [
    {
      id: 'node-1',
      name: 'Untitled',
      type: 'Person',
      rawData: { uuid: 'node-1', name: '', labels: ['Entity', 'Person'] },
    },
    {
      id: 'node-2',
      name: 'Alice',
      type: 'Person',
      rawData: { uuid: 'node-2', name: 'Alice', labels: ['Entity', 'Person'] },
    },
  ])

  assert.deepEqual(result.edges, [
    {
      source: 'node-1',
      target: 'node-2',
      type: 'KNOWS',
      rawData: {
        source_node_uuid: 'node-1',
        target_node_uuid: 'node-2',
        fact_type: 'KNOWS',
        source_name: 'Unknown',
        target_name: 'Alice',
      },
    },
  ])
})

test('process graph mapping collapses obvious alias duplicates and remaps edges', () => {
  const result = mapProcessGraphData({
    unnamedNodeLabel: 'Untitled',
    unknownNodeLabel: 'Unknown',
    nodes: [
      { uuid: 'node-1', name: '美国总统特朗普', labels: ['Entity', 'Person'], attributes: { title: 'President' } },
      { uuid: 'node-2', name: '特朗普', labels: ['Entity', 'Person'], summary: 'Shorter canonical label' },
      { uuid: 'node-3', name: '美国', labels: ['Entity', 'Location'] },
    ],
    edges: [
      { source_node_uuid: 'node-1', target_node_uuid: 'node-3', fact_type: 'LEADS' },
      { source_node_uuid: 'node-2', target_node_uuid: 'node-3', fact_type: 'LEADS' },
    ],
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
})
