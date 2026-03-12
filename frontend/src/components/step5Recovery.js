import { getStep2RecoveryState } from './step2Recovery.js'

export const getStep5RecoveryState = ({ simulation = null, envStatus = null } = {}) => {
  const recoveryState = getStep2RecoveryState(simulation || {})
  if (!recoveryState) {
    return null
  }

  if (!envStatus || envStatus.env_alive) {
    return null
  }

  return recoveryState
}
