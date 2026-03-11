import test from 'node:test'
import assert from 'node:assert/strict'

import {
  describeTimelineAction,
  getTimelineActionTypeLabel,
  getTimelineAvailableActions,
  getTimelinePlatformName,
} from '../src/components/simulationTimeline.js'

const t = (key, params = {}) => `${key}:${JSON.stringify(params)}`

test('timeline helpers resolve localized platform names and action lists', () => {
  assert.equal(getTimelinePlatformName('twitter', t), 'step3.platformNames.twitter:{}')

  assert.deepEqual(getTimelineAvailableActions('reddit', t), [
    'step3.availableActionList.post:{}',
    'step3.availableActionList.comment:{}',
    'step3.availableActionList.like:{}',
    'step3.availableActionList.dislike:{}',
    'step3.availableActionList.search:{}',
    'step3.availableActionList.trend:{}',
    'step3.availableActionList.follow:{}',
    'step3.availableActionList.mute:{}',
    'step3.availableActionList.refresh:{}',
    'step3.availableActionList.idle:{}',
  ])
})

test('timeline helpers localize badge labels and dynamic action descriptions', () => {
  assert.equal(getTimelineActionTypeLabel('UPVOTE_POST', t), 'step3.actionTypes.upvote:{}')

  assert.equal(
    describeTimelineAction(
      { action_type: 'REPOST', action_args: { original_author_name: 'alice' } },
      t
    ),
    'step3.repostedFrom:{"user":"alice"}'
  )

  assert.equal(
    describeTimelineAction({ action_type: 'DO_NOTHING', action_args: {} }, t),
    'step3.actionSkipped:{}'
  )
})
