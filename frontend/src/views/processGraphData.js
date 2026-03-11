export const mapProcessGraphData = ({
  nodes = [],
  edges = [],
  unnamedNodeLabel,
  unknownNodeLabel,
}) => {
  const nodeMap = {}
  nodes.forEach((node) => {
    nodeMap[node.uuid] = node
  })

  const mappedNodes = nodes.map((node) => ({
    id: node.uuid,
    name: node.name || unnamedNodeLabel,
    type: node.labels?.find((label) => label !== 'Entity' && label !== 'Node') || 'Entity',
    rawData: node,
  }))

  const nodeIds = new Set(mappedNodes.map((node) => node.id))
  const mappedEdges = edges
    .filter((edge) => nodeIds.has(edge.source_node_uuid) && nodeIds.has(edge.target_node_uuid))
    .map((edge) => ({
      source: edge.source_node_uuid,
      target: edge.target_node_uuid,
      type: edge.fact_type || edge.name || 'RELATED_TO',
      rawData: {
        ...edge,
        source_name: nodeMap[edge.source_node_uuid]?.name || unknownNodeLabel,
        target_name: nodeMap[edge.target_node_uuid]?.name || unknownNodeLabel,
      },
    }))

  return {
    nodes: mappedNodes,
    edges: mappedEdges,
  }
}
