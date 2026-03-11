import test from 'node:test'
import assert from 'node:assert/strict'

import { getDisplayedAliasNames, hasMergedAliases } from '../src/components/graphAliasDetails.js'

test('getDisplayedAliasNames removes the canonical node name and preserves alias order', () => {
  const aliases = getDisplayedAliasNames({
    name: '特朗普',
    alias_names: ['特朗普', '美国总统特朗普', 'Donald Trump'],
  })

  assert.deepEqual(aliases, ['美国总统特朗普', 'Donald Trump'])
  assert.equal(hasMergedAliases({ name: '特朗普', alias_names: ['特朗普', '美国总统特朗普'] }), true)
})

test('getDisplayedAliasNames tolerates missing data and duplicate aliases', () => {
  assert.deepEqual(getDisplayedAliasNames(null), [])
  assert.deepEqual(
    getDisplayedAliasNames({
      name: 'Alice',
      alias_names: ['Alice', 'Alice', 'Alice Chen'],
    }),
    ['Alice Chen'],
  )
  assert.equal(hasMergedAliases({ name: 'Alice', alias_names: ['Alice'] }), false)
})
