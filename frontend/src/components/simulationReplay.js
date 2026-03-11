export const isReplayOnlyRoute = (value) => value === '1' || value === 'true'

export const shouldAutoStartSimulation = ({ replayOnly = false, resumed = false }) =>
  !replayOnly && !resumed
