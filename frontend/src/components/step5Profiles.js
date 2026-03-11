const PLATFORM_ORDER = {
  reddit: 0,
  twitter: 1,
}

const PLATFORM_LABELS = {
  reddit: 'Reddit',
  twitter: 'Twitter',
}

const normalizeAgentId = (value, fallbackIndex) => {
  const parsed = Number.parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : fallbackIndex
}

export const normalizePlatformProfiles = (platform, profiles = []) => {
  if (!Array.isArray(profiles)) {
    return []
  }

  return profiles.map((profile, index) => {
    const agentId = normalizeAgentId(profile?.agent_id, index)

    return {
      ...profile,
      agent_id: agentId,
      platform,
      platformLabel: PLATFORM_LABELS[platform] || platform,
      profileKey: `${platform}_${agentId}`,
    }
  })
}

export const mergeInteractionProfiles = (entries = []) => {
  return entries
    .flatMap(({ platform, profiles }) => normalizePlatformProfiles(platform, profiles))
    .sort((left, right) => {
      const platformDelta =
        (PLATFORM_ORDER[left.platform] ?? Number.MAX_SAFE_INTEGER) -
        (PLATFORM_ORDER[right.platform] ?? Number.MAX_SAFE_INTEGER)

      if (platformDelta !== 0) {
        return platformDelta
      }

      return left.agent_id - right.agent_id
    })
}

export const buildInterviewRequest = (profile, prompt) => ({
  agent_id: profile.agent_id,
  prompt,
  platform: profile.platform,
})

export const extractInterviewResponseContent = (payload, profile) => {
  const resultData = payload?.result || payload || {}
  const results = resultData.results || resultData
  const preferredKeys = [
    `${profile.platform}_${profile.agent_id}`,
    `reddit_${profile.agent_id}`,
    `twitter_${profile.agent_id}`,
  ]

  if (results && typeof results === 'object' && !Array.isArray(results)) {
    for (const key of preferredKeys) {
      const match = results[key]
      if (match?.response || match?.answer) {
        return match.response || match.answer
      }
    }

    for (const value of Object.values(results)) {
      if (value?.response || value?.answer) {
        return value.response || value.answer
      }
    }
  }

  if (Array.isArray(results)) {
    const matched = results.find((item) => {
      const itemAgentId = normalizeAgentId(item?.agent_id, -1)
      return itemAgentId === profile.agent_id && (!item?.platform || item.platform === profile.platform)
    }) || results[0]

    if (matched?.response || matched?.answer) {
      return matched.response || matched.answer
    }
  }

  return null
}

export const formatAgentRole = (profile, fallbackRole) => {
  const role = profile?.profession || fallbackRole
  const platformLabel = profile?.platformLabel

  return platformLabel ? `${platformLabel} · ${role}` : role
}

const isTimeoutMessage = (message) => /timeout|timed out/i.test(message)

export const summarizeInterviewEnvStatus = (envStatus, t) => {
  if (!envStatus) {
    return ''
  }

  const availablePlatforms = []
  if (envStatus.reddit_available) {
    availablePlatforms.push('Reddit')
  }
  if (envStatus.twitter_available) {
    availablePlatforms.push('Twitter')
  }

  if (!envStatus.env_alive) {
    return t('step5.interviewEnvClosedBanner')
  }

  if (availablePlatforms.length === 0) {
    return t('step5.interviewEnvNoPlatformBanner')
  }

  return t('step5.interviewEnvReadyBanner', { platforms: availablePlatforms.join(' / ') })
}

export const getInterviewGuardMessage = (envStatus, profiles, t) => {
  if (!envStatus?.env_alive) {
    return t('step5.interviewEnvClosedError')
  }

  const unavailablePlatforms = new Set()
  for (const profile of profiles || []) {
    const platform = profile?.platform
    if (!platform) {
      continue
    }

    if (!envStatus[`${platform}_available`]) {
      unavailablePlatforms.add(PLATFORM_LABELS[platform] || platform)
    }
  }

  if (unavailablePlatforms.size > 0) {
    return t('step5.interviewPlatformUnavailable', {
      platforms: Array.from(unavailablePlatforms).join(' / '),
    })
  }

  return ''
}

export const formatInterviewFailureMessage = (message, t) => {
  const normalized = typeof message === 'string' ? message.trim() : ''
  if (!normalized) {
    return t('step5.requestFailed')
  }

  if (normalized.includes('模拟环境未运行或已关闭')) {
    return t('step5.interviewEnvClosedError')
  }

  if (normalized.includes('等待Interview响应超时') || isTimeoutMessage(normalized)) {
    return t('step5.interviewTimeoutError', { message: normalized })
  }

  return normalized
}
