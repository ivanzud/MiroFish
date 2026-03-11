import { deriveInterviewTimeoutSeconds, resolveTimeoutMs } from '../api/timeout.js'

const PLATFORM_ORDER = {
  reddit: 0,
  twitter: 1,
}

const PLATFORM_LABELS = {
  reddit: 'Reddit',
  twitter: 'Twitter',
}

export const getPlatformLabel = (platform, t) =>
  t ? t(`step5.platforms.${platform}`) : (PLATFORM_LABELS[platform] || platform)

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

export const formatAgentRole = (profile, fallbackRole, t) => {
  const role = profile?.profession || fallbackRole
  const platformLabel = profile?.platform ? getPlatformLabel(profile.platform, t) : profile?.platformLabel

  return platformLabel ? `${platformLabel} · ${role}` : role
}

const isTimeoutMessage = (message) => /timeout|timed out/i.test(message)
const INTERVIEW_TIMEOUT_PREFIXES = [
  '等待Interview响应超时',
  'Waiting for Interview response timed out',
]
const ENV_CLOSED_PATTERNS = [
  /模拟环境未运行或已关闭/,
  /The simulation environment is not running or has already closed/i,
  /The environment is not running or has already closed/i,
  /The environment is already closed/i,
]

const isInterviewTimeoutMessage = (message) =>
  INTERVIEW_TIMEOUT_PREFIXES.some((prefix) => message.includes(prefix)) || isTimeoutMessage(message)

const isClosedEnvironmentMessage = (message) =>
  ENV_CLOSED_PATTERNS.some((pattern) => pattern.test(message))

export const summarizeInterviewEnvStatus = (envStatus, t) => {
  if (!envStatus) {
    return ''
  }

  const availablePlatforms = []
  if (envStatus.reddit_available) {
    availablePlatforms.push(getPlatformLabel('reddit', t))
  }
  if (envStatus.twitter_available) {
    availablePlatforms.push(getPlatformLabel('twitter', t))
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
      unavailablePlatforms.add(getPlatformLabel(platform, t))
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

  if (isClosedEnvironmentMessage(normalized)) {
    return t('step5.interviewEnvClosedError')
  }

  if (isInterviewTimeoutMessage(normalized)) {
    return t('step5.interviewTimeoutError', { message: normalized })
  }

  return normalized
}

export const summarizeInterviewTimeoutBudget = ({
  requestTimeoutMs,
  selectedCount = 0,
  t,
}) => {
  const requestSeconds = Math.floor(resolveTimeoutMs(requestTimeoutMs) / 1000)
  const singleSeconds = deriveInterviewTimeoutSeconds({
    requestTimeoutMs,
    interviewsCount: 1,
  })

  if (!Number.isFinite(selectedCount) || selectedCount <= 0) {
    return t('step5.interviewTimeoutHintNoSelection', {
      singleSeconds,
      requestSeconds,
    })
  }

  return t('step5.interviewTimeoutHintWithSelection', {
    singleSeconds,
    selectedCount: Math.floor(selectedCount),
    batchSeconds: deriveInterviewTimeoutSeconds({
      requestTimeoutMs,
      interviewsCount: selectedCount,
    }),
    requestSeconds,
  })
}
