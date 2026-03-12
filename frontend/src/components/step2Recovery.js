import { buildSimulationReplayRoute, hasReplayableSimulationState } from './historyPlayback.js'

export const getStep2RecoveryState = (simulation = {}) => {
  if (!hasReplayableSimulationState(simulation)) {
    return null
  }

  const runnerStatus = simulation.runner_status || 'idle'
  const route = buildSimulationReplayRoute(simulation.simulation_id)

  if (runnerStatus === 'running' || runnerStatus === 'starting') {
    return {
      noticeKey: 'step2.savedRunResumeNotice',
      actionKey: 'step2.openSavedRun',
      route,
    }
  }

  if (runnerStatus === 'failed') {
    return {
      noticeKey: 'step2.savedRunFailedNotice',
      actionKey: 'step2.restartPreparedRun',
      route,
    }
  }

  if (runnerStatus === 'stopped') {
    return {
      noticeKey: 'step2.savedRunStoppedNotice',
      actionKey: 'step2.restartPreparedRun',
      route,
    }
  }

  if (runnerStatus === 'completed') {
    return {
      noticeKey: 'step2.savedRunCompletedNotice',
      actionKey: 'step2.openSavedRun',
      route,
    }
  }

  return {
    noticeKey: 'step2.savedRunReplayNotice',
    actionKey: 'step2.openSavedRun',
    route,
  }
}
