import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildInterviewRequest,
  extractInterviewResponseContent,
  formatInterviewFailureMessage,
  formatAgentRole,
  getEnabledProfilePlatforms,
  getPlatformLabel,
  getInterviewGuardMessage,
  mergeInteractionProfiles,
  summarizeInterviewTimeoutBudget,
  summarizeInterviewEnvStatus,
} from '../src/components/step5Profiles.js'

const t = (key, params = {}) => `${key}:${JSON.stringify(params)}`

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
      { profession: 'Analyst', platform: 'reddit' },
      'Unknown',
      t
    ),
    'step5.platforms.reddit:{} · Analyst'
  )
})

test('getPlatformLabel uses locale translator when available', () => {
  assert.equal(getPlatformLabel('twitter', t), 'step5.platforms.twitter:{}')
})

test('getEnabledProfilePlatforms keeps only enabled simulation platforms', () => {
  assert.deepEqual(
    getEnabledProfilePlatforms({
      enable_twitter: true,
      enable_reddit: false,
    }),
    ['twitter']
  )

  assert.deepEqual(
    getEnabledProfilePlatforms({
      enable_twitter: true,
      enable_reddit: true,
    }),
    ['reddit', 'twitter']
  )
})

test('summarizeInterviewEnvStatus reports ready platforms', () => {
  assert.equal(
    summarizeInterviewEnvStatus(
      {
        env_alive: true,
        reddit_available: true,
        twitter_available: false,
      },
      t
    ),
    'step5.interviewEnvReadyBanner:{"platforms":"step5.platforms.reddit:{}"}'
  )
})

test('getInterviewGuardMessage blocks closed environments and unavailable platforms', () => {
  assert.equal(
    getInterviewGuardMessage(
      {
        env_alive: false,
        reddit_available: false,
        twitter_available: false,
      },
      [{ platform: 'reddit' }],
      t
    ),
    'step5.interviewEnvClosedError:{}'
  )

  assert.equal(
    getInterviewGuardMessage(
      {
        env_alive: true,
        reddit_available: true,
        twitter_available: false,
      },
      [{ platform: 'twitter' }],
      t
    ),
    'step5.interviewPlatformUnavailable:{"platforms":"step5.platforms.twitter:{}"}'
  )
})

test('formatInterviewFailureMessage normalizes timeout and env-closed backend errors', () => {
  assert.equal(
    formatInterviewFailureMessage('模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。', t),
    'step5.interviewEnvClosedError:{}'
  )

  assert.equal(
    formatInterviewFailureMessage(
      'The simulation environment is not running or has already closed. Make sure the simulation completed and is in wait-for-commands mode.',
      t
    ),
    'step5.interviewEnvClosedError:{}'
  )

  assert.equal(
    formatInterviewFailureMessage('The environment is already closed', t),
    'step5.interviewEnvClosedError:{}'
  )

  assert.equal(
    formatInterviewFailureMessage('等待Interview响应超时: 300s', t),
    'step5.interviewTimeoutError:{"message":"等待Interview响应超时: 300s"}'
  )

  assert.equal(
    formatInterviewFailureMessage('Waiting for Interview response timed out: 300s', t),
    'step5.interviewTimeoutError:{"message":"Waiting for Interview response timed out: 300s"}'
  )

  assert.equal(
    formatInterviewFailureMessage('等待批量Interview响应超时: 300s', t),
    'step5.interviewTimeoutError:{"message":"等待批量Interview响应超时: 300s"}'
  )

  assert.equal(
    formatInterviewFailureMessage('等待全局Interview响应超时: 300s', t),
    'step5.interviewTimeoutError:{"message":"等待全局Interview响应超时: 300s"}'
  )

  assert.equal(
    formatInterviewFailureMessage('Timed out while waiting for the batch interview response: 300s', t),
    'step5.interviewTimeoutError:{"message":"Timed out while waiting for the batch interview response: 300s"}'
  )

  assert.equal(
    formatInterviewFailureMessage('Timed out while waiting for the global interview response: 300s', t),
    'step5.interviewTimeoutError:{"message":"Timed out while waiting for the global interview response: 300s"}'
  )
})

test('summarizeInterviewTimeoutBudget explains single and batch budgets', () => {
  assert.equal(
    summarizeInterviewTimeoutBudget({ requestTimeoutMs: 300000, selectedCount: 0, t }),
    'step5.interviewTimeoutHintNoSelection:{"singleSeconds":90,"requestSeconds":300}'
  )

  assert.equal(
    summarizeInterviewTimeoutBudget({ requestTimeoutMs: 300000, selectedCount: 4, t }),
    'step5.interviewTimeoutHintWithSelection:{"singleSeconds":90,"selectedCount":4,"batchSeconds":150,"requestSeconds":300}'
  )
})
