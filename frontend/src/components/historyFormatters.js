export const truncateFilename = (filename, maxLength, unknownLabel = 'Unknown file') => {
  if (!filename) {
    return unknownLabel
  }

  if (filename.length <= maxLength) {
    return filename
  }

  const ext = filename.includes('.') ? `.${filename.split('.').pop()}` : ''
  const nameWithoutExt = filename.slice(0, filename.length - ext.length)
  const truncatedName = `${nameWithoutExt.slice(0, maxLength - ext.length - 3)}...`
  return truncatedName + ext
}
