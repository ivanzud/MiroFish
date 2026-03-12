export const isReplayOnlyRoute = (value) => value === '1' || value === 'true'

export const shouldAutoStartSimulation = ({ replayOnly = false, resumed = false }) =>
  !replayOnly && !resumed

export const getReplayNoticeKey = ({ replayOnly = false, resumed = false, runnerStatus = '' }) => {
  if (!replayOnly) {
    return null
  }

  if (!resumed) {
    return 'step3.replayOnlyNoRunNotice'
  }

  if (runnerStatus === 'failed') {
    return 'step3.replayOnlyFailedNotice'
  }

  if (runnerStatus === 'stopped') {
    return 'step3.replayOnlyStoppedNotice'
  }

  return null
}

export const getRestartButtonLabelKey = ({ replayOnly = false, resumed = false, runnerStatus = '' }) => {
  if (!replayOnly) {
    return 'step3.restartSimulation'
  }

  if (!resumed) {
    return 'step3.startPreparedSimulation'
  }

  if (runnerStatus === 'failed' || runnerStatus === 'stopped') {
    return 'step3.restartPreparedSimulation'
  }

  return 'step3.restartSimulation'
}
