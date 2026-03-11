export const resolveTimeoutMs = (rawTimeout, fallback = 300000) => {
  const envTimeout = Number.parseInt(rawTimeout, 10)
  return Number.isFinite(envTimeout) && envTimeout > 0 ? envTimeout : fallback
}

export const deriveInterviewTimeoutSeconds = ({
  requestTimeoutMs = 300000,
  interviewsCount = 1,
  bufferSeconds = 5,
  baseSeconds = 90,
  perInterviewSeconds = 20,
}) => {
  const boundedCount = Number.isFinite(interviewsCount) && interviewsCount > 0
    ? Math.floor(interviewsCount)
    : 1
  const requestBudgetSeconds = Math.max(
    30,
    Math.floor(resolveTimeoutMs(requestTimeoutMs) / 1000) - bufferSeconds
  )
  const requestedSeconds = baseSeconds + Math.max(0, boundedCount - 1) * perInterviewSeconds

  return Math.max(30, Math.min(requestBudgetSeconds, requestedSeconds))
}
