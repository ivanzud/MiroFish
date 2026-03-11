export const hasReplayableSimulationState = (simulation = {}) => {
  const runnerStatus = simulation.runner_status || 'idle'
  const currentRound = Number(simulation.current_round || 0)
  const totalRounds = Number(simulation.total_rounds || 0)

  if (['running', 'starting', 'completed', 'stopped', 'failed', 'stopping', 'paused'].includes(runnerStatus)) {
    return true
  }

  return currentRound > 0 || totalRounds > 0
}

export const buildSimulationReplayRoute = (simulationId) => ({
  name: 'SimulationRun',
  params: { simulationId },
  query: { replay: '1' },
})
