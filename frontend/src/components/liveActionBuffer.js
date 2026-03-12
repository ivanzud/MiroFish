export const DEFAULT_MAX_TIMELINE_ACTIONS = 1000

export const buildLiveActionId = (action = {}) =>
  action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`

export const mergeLiveActions = ({
  existingActions = [],
  existingIds = new Set(),
  incomingActions = [],
  latestActionTimestamp = '',
  maxActions = DEFAULT_MAX_TIMELINE_ACTIONS,
} = {}) => {
  const nextActions = [...existingActions]
  const nextIds = new Set(existingIds)
  let nextLatestTimestamp = latestActionTimestamp

  incomingActions.forEach((action) => {
    const actionId = buildLiveActionId(action)

    if (!nextIds.has(actionId)) {
      nextIds.add(actionId)
      nextActions.push({
        ...action,
        _uniqueId: actionId,
      })
    }

    if (action.timestamp && action.timestamp > nextLatestTimestamp) {
      nextLatestTimestamp = action.timestamp
    }
  })

  if (maxActions > 0 && nextActions.length > maxActions) {
    const removedActions = nextActions.splice(0, nextActions.length - maxActions)
    removedActions.forEach((action) => {
      nextIds.delete(action._uniqueId || buildLiveActionId(action))
    })
  }

  return {
    actions: nextActions,
    actionIds: nextIds,
    latestActionTimestamp: nextLatestTimestamp,
  }
}
