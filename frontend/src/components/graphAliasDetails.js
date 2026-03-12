const uniqueValues = (values) => [...new Set((values || []).filter(Boolean))]

export const getDisplayedAliasNames = (node) => {
  if (!node) {
    return []
  }

  const canonicalName = typeof node.name === 'string' ? node.name.trim() : ''
  const aliases = uniqueValues(node.alias_names)

  return aliases.filter((alias) => alias !== canonicalName)
}

export const hasMergedAliases = (node) => getDisplayedAliasNames(node).length > 0
