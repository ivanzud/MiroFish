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
