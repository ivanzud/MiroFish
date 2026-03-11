import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildInterviewRequest,
  extractInterviewResponseContent,
  formatAgentRole,
  mergeInteractionProfiles,
} from '../src/components/step5Profiles.js'

test('mergeInteractionProfiles keeps both platforms and annotates ids', () => {
  const merged = mergeInteractionProfiles([
    {
      platform: 'twitter',
      profiles: [{ username: 'tw-user' }],
    },
    {
      platform: 'reddit',
      profiles: [{ username: 'rd-user', agent_id: '4' }],
    },
  ])

  assert.deepEqual(
    merged.map(({ username, agent_id: agentId, platform, profileKey }) => ({
      username,
      agentId,
      platform,
      profileKey,
    })),
    [
      { username: 'rd-user', agentId: 4, platform: 'reddit', profileKey: 'reddit_4' },
      { username: 'tw-user', agentId: 0, platform: 'twitter', profileKey: 'twitter_0' },
    ]
  )
})

test('buildInterviewRequest preserves platform-specific targeting', () => {
  assert.deepEqual(
    buildInterviewRequest(
      { agent_id: 7, platform: 'twitter' },
      'hello'
    ),
    {
      agent_id: 7,
      prompt: 'hello',
      platform: 'twitter',
    }
  )
})

test('extractInterviewResponseContent prefers the selected platform result', () => {
  const content = extractInterviewResponseContent(
    {
      result: {
        results: {
          reddit_3: { response: 'reddit reply' },
          twitter_3: { response: 'twitter reply' },
        },
      },
    },
    { agent_id: 3, platform: 'twitter' }
  )

  assert.equal(content, 'twitter reply')
})

test('formatAgentRole includes platform label for mixed-platform lists', () => {
  assert.equal(
    formatAgentRole(
      { profession: 'Analyst', platformLabel: 'Reddit' },
      'Unknown'
    ),
    'Reddit · Analyst'
  )
})
