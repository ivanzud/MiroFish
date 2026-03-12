const NON_WORD_RE = /[^\p{L}\p{N}]+/gu
const PERSON_PREFIXES = [
  '美国总统',
  '总统',
  'president',
  'formerpresident',
  'currentpresident',
  'ceo',
  'founder',
  'cofounder',
  'professor',
  'doctor',
  'dr',
  'mr',
  'mrs',
  'ms',
  'sir',
]
const ORG_SUFFIXES = [
  '有限责任公司',
  '股份有限公司',
  '有限公司',
  '集团',
  '公司',
  'corporation',
  'corp',
  'inc',
  'ltd',
  'llc',
  'university',
]
const PERSON_TYPE_HINTS = [
  'person',
  'student',
  'alumni',
  'player',
  'leader',
  'figure',
  'expert',
  'human',
  '人物',
  '学生',
  '校友',
  '个人',
  '公众人物',
]
const ORG_TYPE_HINTS = [
  'organization',
  'company',
  'institution',
  'agency',
  'university',
  'media',
  'group',
  '企业',
  '机构',
  '组织',
]

const getNodeType = (node) =>
  node.labels?.find((label) => label !== 'Entity' && label !== 'Node') || 'Entity'

const normalizeEntityName = (name) =>
  (name || '').normalize('NFKC').trim().toLowerCase().replace(NON_WORD_RE, '')

const stripKnownAffixes = (normalizedName, entityType) => {
  const normalizedType = (entityType || '').trim().toLowerCase()
  let stripped = normalizedName

  if (PERSON_TYPE_HINTS.some((hint) => normalizedType.includes(hint))) {
    for (const prefix of PERSON_PREFIXES) {
      if (stripped.startsWith(prefix) && stripped.length > prefix.length + 1) {
        stripped = stripped.slice(prefix.length)
        break
      }
    }
  }

  if (ORG_TYPE_HINTS.some((hint) => normalizedType.includes(hint))) {
    for (const suffix of ORG_SUFFIXES) {
      if (stripped.endsWith(suffix) && stripped.length > suffix.length + 1) {
        stripped = stripped.slice(0, -suffix.length)
        break
      }
    }
  }

  return stripped || normalizedName
}

const getAliasKey = (node) => {
  const normalizedName = normalizeEntityName(node.name)
  if (!normalizedName) {
    return ''
  }
  return stripKnownAffixes(normalizedName, getNodeType(node))
}

const areDuplicateNodes = (left, right) => {
  const leftType = getNodeType(left)
  const rightType = getNodeType(right)
  if (!leftType || leftType !== rightType) {
    return false
  }

  const leftName = normalizeEntityName(left.name)
  const rightName = normalizeEntityName(right.name)
  if (!leftName || !rightName) {
    return false
  }

  if (leftName === rightName) {
    return true
  }

  const leftKey = getAliasKey(left)
  const rightKey = getAliasKey(right)
  if (!leftKey || leftKey !== rightKey || leftKey.length < 2) {
    return false
  }

  const [shorter, longer] = [leftName, rightName].sort((a, b) => a.length - b.length)
  return shorter.length >= 2 && longer.includes(shorter)
}

const getNodeScore = (node) => {
  const attributeCount = Object.keys(node.attributes || {}).length
  const summaryLength = (node.summary || '').length
  const labelCount = (node.labels || []).length
  return attributeCount * 10 + summaryLength + labelCount
}

const pickPrimaryNode = (left, right) => {
  const leftName = normalizeEntityName(left.name)
  const rightName = normalizeEntityName(right.name)

  if (leftName && rightName && leftName.length !== rightName.length) {
    return leftName.length < rightName.length ? left : right
  }

  return getNodeScore(left) >= getNodeScore(right) ? left : right
}

const uniqueValues = (values) => [...new Set(values.filter(Boolean))]

const mergeDuplicateNodes = (nodes) => {
  const mergedNodes = []

  nodes.forEach((node) => {
    const preparedNode = {
      ...node,
      labels: [...(node.labels || [])],
      ...(node.attributes ? { attributes: { ...node.attributes } } : {}),
      __alias_names: uniqueValues([...(node.alias_names || []), node.name]),
      __merged_node_uuids: uniqueValues([...(node.merged_node_uuids || []), node.uuid]),
    }

    const duplicateIndex = mergedNodes.findIndex((existing) => areDuplicateNodes(existing, preparedNode))
    if (duplicateIndex === -1) {
      mergedNodes.push(preparedNode)
      return
    }

    const existing = mergedNodes[duplicateIndex]
    const primary = pickPrimaryNode(existing, preparedNode)
    const secondary = primary === existing ? preparedNode : existing

    mergedNodes[duplicateIndex] = {
      ...secondary,
      ...primary,
      labels: uniqueValues([...(primary.labels || []), ...(secondary.labels || [])]),
      ...((primary.attributes || secondary.attributes)
        ? {
            attributes: {
              ...(secondary.attributes || {}),
              ...(primary.attributes || {}),
            },
          }
        : {}),
      __alias_names: uniqueValues([
        ...(primary.__alias_names || []),
        ...(secondary.__alias_names || []),
        primary.name,
        secondary.name,
      ]),
      __merged_node_uuids: uniqueValues([
        ...(primary.__merged_node_uuids || []),
        ...(secondary.__merged_node_uuids || []),
      ]),
    }
  })

  const nodeIdRemap = {}
  const sanitizedNodes = mergedNodes.map((node) => {
    ;(node.__merged_node_uuids || []).forEach((uuid) => {
      nodeIdRemap[uuid] = node.uuid
    })

    const sanitizedNode = {
      ...node,
    }
    delete sanitizedNode.__alias_names
    delete sanitizedNode.__merged_node_uuids

    if ((node.__alias_names || []).length > 1) {
      sanitizedNode.alias_names = [...node.__alias_names]
    } else {
      delete sanitizedNode.alias_names
    }

    if ((node.__merged_node_uuids || []).length > 1) {
      sanitizedNode.merged_node_uuids = [...node.__merged_node_uuids]
    } else {
      delete sanitizedNode.merged_node_uuids
    }

    return sanitizedNode
  })

  return { mergedNodes: sanitizedNodes, nodeIdRemap }
}

export const mapProcessGraphData = ({
  nodes = [],
  edges = [],
  unnamedNodeLabel,
  unknownNodeLabel,
}) => {
  const { mergedNodes, nodeIdRemap } = mergeDuplicateNodes(nodes)
  const nodeMap = {}
  mergedNodes.forEach((node) => {
    nodeMap[node.uuid] = node
  })

  const mappedNodes = mergedNodes.map((node) => ({
    id: node.uuid,
    name: node.name || unnamedNodeLabel,
    type: getNodeType(node),
    rawData: node,
  }))

  const nodeIds = new Set(mappedNodes.map((node) => node.id))
  const seenEdgeKeys = new Set()
  const mappedEdges = edges
    .map((edge) => {
      const source = nodeIdRemap[edge.source_node_uuid] || edge.source_node_uuid
      const target = nodeIdRemap[edge.target_node_uuid] || edge.target_node_uuid
      const type = edge.fact_type || edge.name || 'RELATED_TO'
      return {
        source,
        target,
        type,
        rawData: {
          ...edge,
          source_node_uuid: source,
          target_node_uuid: target,
          source_name: nodeMap[source]?.name || unknownNodeLabel,
          target_name: nodeMap[target]?.name || unknownNodeLabel,
        },
      }
    })
    .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
    .filter((edge) => {
      const key = `${edge.source}::${edge.target}::${edge.type}`
      if (seenEdgeKeys.has(key)) {
        return false
      }
      seenEdgeKeys.add(key)
      return true
    })

  return {
    nodes: mappedNodes,
    edges: mappedEdges,
  }
}

export const getProcessGraphSignature = ({
  nodes = [],
  edges = [],
  unnamedNodeLabel = 'Unnamed',
  unknownNodeLabel = 'Unknown',
}) => {
  const mapped = mapProcessGraphData({
    nodes,
    edges,
    unnamedNodeLabel,
    unknownNodeLabel,
  })

  const nodeSignature = mapped.nodes
    .map((node) => ({
      id: node.id,
      name: node.name,
      type: node.type,
      aliases: [...(node.rawData?.alias_names || [])].sort(),
      merged: [...(node.rawData?.merged_node_uuids || [])].sort(),
    }))
    .sort((left, right) => left.id.localeCompare(right.id))

  const edgeSignature = mapped.edges
    .map((edge) => ({
      source: edge.source,
      target: edge.target,
      type: edge.type,
    }))
    .sort((left, right) => (
      `${left.source}::${left.target}::${left.type}`.localeCompare(
        `${right.source}::${right.target}::${right.type}`,
      )
    ))

  return JSON.stringify({
    nodes: nodeSignature,
    edges: edgeSignature,
  })
}
