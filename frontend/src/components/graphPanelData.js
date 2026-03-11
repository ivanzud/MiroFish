import { mapProcessGraphData } from '../views/processGraphData.js'

const ENTITY_TYPE_COLORS = ['#FF6B35', '#004E89', '#7B2D8E', '#1A936F', '#C5283D', '#E9724C', '#3498db', '#9b59b6', '#27ae60', '#f39c12']

export const normalizeGraphPanelData = ({
  graphData,
  unnamedNodeLabel = 'Unnamed',
  unknownNodeLabel = 'Unknown',
} = {}) => {
  if (!graphData) {
    return {
      nodes: [],
      edges: [],
      entityTypes: [],
    }
  }

  const mapped = mapProcessGraphData({
    nodes: graphData.nodes || [],
    edges: graphData.edges || [],
    unnamedNodeLabel,
    unknownNodeLabel,
  })

  const typeMap = {}
  mapped.nodes.forEach((node) => {
    const type = node.type || 'Entity'
    if (!typeMap[type]) {
      typeMap[type] = {
        name: type,
        count: 0,
        color: ENTITY_TYPE_COLORS[Object.keys(typeMap).length % ENTITY_TYPE_COLORS.length],
      }
    }
    typeMap[type].count += 1
  })

  return {
    nodes: mapped.nodes,
    edges: mapped.edges,
    entityTypes: Object.values(typeMap),
  }
}
