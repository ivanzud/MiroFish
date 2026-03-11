import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildLiveActionId,
  mergeLiveActions,
} from '../src/components/liveActionBuffer.js'

test('buildLiveActionId prefers server id when present', () => {
  assert.equal(
    buildLiveActionId({
      id: 'action-1',
      timestamp: '2026-03-11T14:00:00',
      platform: 'twitter',
      agent_id: 1,
      action_type: 'CREATE_POST',
    }),
    'action-1'
  )
})

test('mergeLiveActions deduplicates incoming events and keeps the latest timestamp', () => {
  const merged = mergeLiveActions({
    incomingActions: [
      {
        timestamp: '2026-03-11T14:00:00',
        platform: 'twitter',
        agent_id: 1,
        action_type: 'CREATE_POST',
      },
      {
        timestamp: '2026-03-11T14:00:00',
        platform: 'twitter',
        agent_id: 1,
        action_type: 'CREATE_POST',
      },
      {
        timestamp: '2026-03-11T14:00:01',
        platform: 'reddit',
        agent_id: 2,
        action_type: 'CREATE_COMMENT',
      },
    ],
  })

  assert.equal(merged.actions.length, 2)
  assert.deepEqual(
    merged.actions.map((action) => action._uniqueId),
    [
      '2026-03-11T14:00:00-twitter-1-CREATE_POST',
      '2026-03-11T14:00:01-reddit-2-CREATE_COMMENT',
    ]
  )
  assert.equal(merged.latestActionTimestamp, '2026-03-11T14:00:01')
})

test('mergeLiveActions trims the oldest buffered events when the cap is exceeded', () => {
  const merged = mergeLiveActions({
    existingActions: [
      {
        timestamp: '2026-03-11T14:00:00',
        platform: 'twitter',
        agent_id: 1,
        action_type: 'CREATE_POST',
        _uniqueId: '2026-03-11T14:00:00-twitter-1-CREATE_POST',
      },
      {
        timestamp: '2026-03-11T14:00:01',
        platform: 'reddit',
        agent_id: 2,
        action_type: 'CREATE_COMMENT',
        _uniqueId: '2026-03-11T14:00:01-reddit-2-CREATE_COMMENT',
      },
    ],
    existingIds: new Set([
      '2026-03-11T14:00:00-twitter-1-CREATE_POST',
      '2026-03-11T14:00:01-reddit-2-CREATE_COMMENT',
    ]),
    incomingActions: [
      {
        timestamp: '2026-03-11T14:00:02',
        platform: 'twitter',
        agent_id: 3,
        action_type: 'LIKE_POST',
      },
    ],
    maxActions: 2,
  })

  assert.deepEqual(
    merged.actions.map((action) => action._uniqueId),
    [
      '2026-03-11T14:00:01-reddit-2-CREATE_COMMENT',
      '2026-03-11T14:00:02-twitter-3-LIKE_POST',
    ]
  )
  assert.equal(
    merged.actionIds.has('2026-03-11T14:00:00-twitter-1-CREATE_POST'),
    false
  )
})
