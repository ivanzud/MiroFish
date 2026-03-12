export const buildInteractionRoute = ({ reportId = '', simulationId = '' } = {}) => {
  if (typeof reportId === 'string' && reportId.trim()) {
    return {
      name: 'Interaction',
      params: { reportId: reportId.trim() },
    }
  }

  if (typeof simulationId === 'string' && simulationId.trim()) {
    return {
      name: 'InteractionSimulation',
      params: { simulationId: simulationId.trim() },
    }
  }

  return null
}
