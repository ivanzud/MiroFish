export function formatMainViewStepLog(action, stepNumber, stepName, t) {
  const key = action === 'back'
    ? 'mainView.logs.returnStep'
    : 'mainView.logs.enterStep'

  return t(key, {
    step: stepNumber,
    name: stepName,
  })
}

export function formatMainViewGraphRefreshLog(nodeCount, edgeCount, t) {
  return t('mainView.logs.graphDataRefreshed', {
    nodeCount: nodeCount || 0,
    edgeCount: edgeCount || 0,
  })
}
