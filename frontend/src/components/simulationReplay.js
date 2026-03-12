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

  return null
}
