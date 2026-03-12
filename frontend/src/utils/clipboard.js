export const copyText = async (value, clipboard = globalThis.navigator?.clipboard) => {
  if (!value || typeof value !== 'string') {
    return false
  }

  if (!clipboard || typeof clipboard.writeText !== 'function') {
    return false
  }

  await clipboard.writeText(value)
  return true
}
