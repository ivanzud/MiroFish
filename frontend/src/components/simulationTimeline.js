const ACTION_TYPE_KEY_MAP = {
  CREATE_POST: 'post',
  REPOST: 'repost',
  LIKE_POST: 'like',
  CREATE_COMMENT: 'comment',
  LIKE_COMMENT: 'like',
  DO_NOTHING: 'idle',
  FOLLOW: 'follow',
  SEARCH_POSTS: 'search',
  QUOTE_POST: 'quote',
  UPVOTE_POST: 'upvote',
  DOWNVOTE_POST: 'downvote',
}

const PLATFORM_ACTION_KEYS = {
  twitter: ['post', 'like', 'repost', 'quote', 'follow', 'idle'],
  reddit: ['post', 'comment', 'like', 'dislike', 'search', 'trend', 'follow', 'mute', 'refresh', 'idle'],
}

export const getTimelinePlatformName = (platform, t) =>
  t(`step3.platformNames.${platform}`)

export const getTimelineAvailableActions = (platform, t) =>
  (PLATFORM_ACTION_KEYS[platform] || []).map((key) => t(`step3.availableActionList.${key}`))

export const getTimelineActionTypeLabel = (type, t) => {
  const key = ACTION_TYPE_KEY_MAP[type]
  return key ? t(`step3.actionTypes.${key}`) : type || t('step3.actionTypes.unknown')
}

export const describeTimelineAction = (action, t) => {
  const args = action?.action_args || {}

  switch (action?.action_type) {
    case 'REPOST':
      return t('step3.repostedFrom', { user: args.original_author_name || t('step3.unknownUser') })
    case 'LIKE_POST':
      return t('step3.likedPost', { user: args.post_author_name || t('step3.unknownUser') })
    case 'CREATE_COMMENT':
      return t('step3.replyToPost', { id: args.post_id || '-' })
    case 'SEARCH_POSTS':
      return t('step3.searchQuery')
    case 'FOLLOW':
      return t('step3.followedUser', { user: args.target_user || args.user_id || t('step3.unknownUser') })
    case 'UPVOTE_POST':
      return t('step3.upvotedPost')
    case 'DOWNVOTE_POST':
      return t('step3.downvotedPost')
    case 'DO_NOTHING':
      return t('step3.actionSkipped')
    default:
      return ''
  }
}
