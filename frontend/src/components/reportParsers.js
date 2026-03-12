const NO_REPLY_MARKERS = new Set([
  '（该平台未获得回复）',
  '(该平台未获得回复)',
  '[无回复]',
  '(no reply from this platform)',
  '[no reply]',
  'no reply from this platform',
])

const INTERVIEW_REASON_SKIP_RE = /^(?:未选|综上|最终选择|not selected|overall|final selection)/i
const INTERVIEW_SPLIT_RE = /####\s*(?:采访|Interview)\s*#\d+:/i
const INTERVIEW_TOPIC_RE = /\*\*(?:采访主题|Interview Topic|Topic):\*\*\s*(.+?)(?:\n|$)/i
const INTERVIEW_COUNT_RE = /\*\*(?:采访人数|Interview(?:ed)? Agents?|Agents Interviewed):\*\*\s*(\d+)\s*\/\s*(\d+)/i
const INTERVIEW_REASON_RE = /###\s*(?:采访对象选择理由|Why These Interviewees|Interviewee Selection Rationale|Selection Rationale)\n([\s\S]*?)(?=\n---\n|\n###\s*(?:采访实录|Interview Transcript))/i
const INTERVIEW_BIO_RE = /_(?:简介|Bio|Profile):\s*([\s\S]*?)_\n/i
const INTERVIEW_SUMMARY_RE = /###\s*(?:采访摘要与核心观点|Interview Summary(?: and Key Takeaways)?|Key Takeaways)\n([\s\S]*?)$/i
const INTERVIEW_QUOTES_RE = /\*\*(?:关键引言|Key Quotes|Quotes):\*\*\n([\s\S]*?)(?=\n---|\n####|$)/i
const QUICK_QUERY_RE = /(?:搜索查询|Search Query):\s*(.+?)(?:\n|$)/i
const QUICK_COUNT_RE = /(?:找到|Found)\s*(\d+)\s*(?:条(?:相关(?:信息|事实))?|relevant (?:items|facts|results)?)/i
const QUICK_FACTS_RE = /###\s*(?:相关事实|Relevant Facts):\n([\s\S]*?)(?=\n###|$)/i
const QUICK_EDGES_RE = /###\s*(?:相关边|Related Edges):\n([\s\S]*?)(?=\n###|$)/i
const QUICK_NODES_RE = /###\s*(?:相关节点|Related Nodes):\n([\s\S]*?)(?=\n###|$)/i
const INSIGHT_QUERY_RE = /(?:分析问题|Analysis Question):\s*(.+?)(?:\n|$)/i
const INSIGHT_SCENARIO_RE = /(?:预测场景|Prediction Scenario):\s*(.+?)(?:\n|$)/i
const INSIGHT_FACT_COUNT_RE = /(?:相关预测事实|Relevant Prediction Facts):\s*(\d+)/i
const INSIGHT_ENTITY_COUNT_RE = /(?:涉及实体|Entities Involved):\s*(\d+)/i
const INSIGHT_RELATION_COUNT_RE = /(?:关系链|Relationship Chains):\s*(\d+)/i
const INSIGHT_SUBQUERIES_RE = /###\s*(?:分析的子问题|Analysis Subquestions)\n([\s\S]*?)(?=\n###|$)/i
const INSIGHT_FACTS_RE = /###\s*(?:【关键事实】|Key Facts)\n([\s\S]*?)(?=\n###|$)/i
const INSIGHT_ENTITIES_RE = /###\s*(?:【核心实体】|Core Entities)\n([\s\S]*?)(?=\n###|$)/i
const INSIGHT_ENTITY_SUMMARY_RE = /(?:摘要|Summary):\s*"?(.+?)"?(?:\n|$)/i
const INSIGHT_ENTITY_RELATED_RE = /(?:相关事实|Related Facts):\s*(\d+)/i
const INSIGHT_RELATIONS_RE = /###\s*(?:【关系链】|Relationship Chains)\n([\s\S]*?)(?=\n###|$)/i
const PANORAMA_QUERY_RE = /(?:查询|Query):\s*(.+?)(?:\n|$)/i
const PANORAMA_NODES_RE = /(?:总节点数|Total Nodes):\s*(\d+)/i
const PANORAMA_EDGES_RE = /(?:总边数|Total Edges):\s*(\d+)/i
const PANORAMA_ACTIVE_COUNT_RE = /(?:当前有效事实|Current Active Facts):\s*(\d+)/i
const PANORAMA_HISTORICAL_COUNT_RE = /(?:历史\/过期事实|Historical\/Expired Facts):\s*(\d+)/i
const PANORAMA_ACTIVE_RE = /###\s*(?:【当前有效事实】|Current Active Facts)\n([\s\S]*?)(?=\n###|$)/i
const PANORAMA_HISTORICAL_RE = /###\s*(?:【历史\/过期事实】|Historical\/Expired Facts)\n([\s\S]*?)(?=\n###|$)/i
const PANORAMA_ENTITIES_RE = /###\s*(?:【涉及实体】|Entities Involved)\n([\s\S]*?)(?=\n###|$)/i
const QUESTION_PREFIX_RE = /(?:^|[\r\n]+)(?:问题|Question)\s*(\d+)[：:]\s*/g
const NUMBERED_PREFIX_RE = /(?:^|[\r\n]+)(\d+)\.\s+/g
const FINAL_ANSWER_RE = /Final\s*Answer:\s*\n*([\s\S]*)$/i
const CHINESE_FINAL_ANSWER_RE = /最终答案[:：]\s*\n*([\s\S]*)$/i
const QUESTION_SECTION_RE = /\*\*(?:Q|Questions?):\*\*\s*([\s\S]*?)(?=\n\n\*\*(?:A|Answer):\*\*|\*\*(?:A|Answer):\*\*)/i
const ANSWER_SECTION_RE = /\*\*(?:A|Answer):\*\*\s*([\s\S]*?)(?=\*\*(?:关键引言|Key Quotes|Quotes)|$)/i
const QUESTION_PREFIX_SPLIT_RE = /(?:^|[\r\n]+)(?:问题|Question)\s*\d+[：:]\s*/i
const TWITTER_SECTION_RE = /【Twitter(?:平台回答| Reply| Response| Answer)】\n?([\s\S]*?)(?=【Reddit(?:平台回答| Reply| Response| Answer)】|$)/i
const REDDIT_SECTION_RE = /【Reddit(?:平台回答| Reply| Response| Answer)】\n?([\s\S]*?)$/i

export const isMissingPlatformReply = (text) => {
  if (!text) {
    return true
  }

  return NO_REPLY_MARKERS.has(text.trim().toLowerCase())
}

const collectNumberedLines = (text) =>
  text
    .split('\n')
    .filter((line) => /^\d+\./.test(line.trim()))
    .map((line) => line.replace(/^\d+\.\s*/, '').trim())
    .filter(Boolean)

const parseIndividualReasons = (reasonText) => {
  const reasons = {}
  if (!reasonText) {
    return reasons
  }

  const lines = reasonText.split(/\n+/)
  let currentName = null
  let currentReason = []

  for (const line of lines) {
    let headerMatch = line.match(/^\d+\.\s*\*\*([^*（(]+)(?:[（(]index\s*=?\s*\d+[)）])?\*\*[：:]\s*(.*)/)
    if (!headerMatch) {
      headerMatch = line.match(/^-\s*(?:选择|Select)\s*([^（(]+)(?:[（(]index\s*=?\s*\d+[)）])?[：:]\s*(.*)/i)
    }
    if (!headerMatch) {
      headerMatch = line.match(/^-\s*\*\*([^*（(]+)(?:[（(]index\s*=?\s*\d+[)）])?\*\*[：:]\s*(.*)/)
    }

    if (headerMatch) {
      if (currentName && currentReason.length > 0) {
        reasons[currentName] = currentReason.join(' ').trim()
      }
      currentName = headerMatch[1].trim()
      currentReason = headerMatch[2] ? [headerMatch[2].trim()] : []
      continue
    }

    if (currentName && line.trim() && !INTERVIEW_REASON_SKIP_RE.test(line.trim())) {
      currentReason.push(line.trim())
    }
  }

  if (currentName && currentReason.length > 0) {
    reasons[currentName] = currentReason.join(' ').trim()
  }

  return reasons
}

const splitQuestions = (questionText) => {
  if (!questionText) {
    return []
  }

  if (QUESTION_PREFIX_SPLIT_RE.test(questionText)) {
    const questions = []
    const prefixRe = new RegExp(QUESTION_PREFIX_RE.source, QUESTION_PREFIX_RE.flags)
    const matches = [...questionText.matchAll(prefixRe)]

    for (let index = 0; index < matches.length; index += 1) {
      const current = matches[index]
      const next = matches[index + 1]
      const start = current.index + current[0].length
      const end = next ? next.index : questionText.length
      const question = questionText.slice(start, end).trim()
      if (question) {
        questions.push(question)
      }
    }

    if (questions.length > 0) {
      return questions
    }
  }

  const questions = questionText.split(/\n\d+\.\s+/).filter((item) => item.trim())
  if (questions.length === 0) {
    return []
  }

  const firstQuestion = questionText.match(/^1\.\s+(.+)/)
  if (firstQuestion) {
    return [firstQuestion[1].trim(), ...questions.slice(1).map((item) => item.trim())]
  }

  return questions.map((item) => item.trim())
}

const splitAnswerByQuestions = (answerText) => {
  if (!answerText || isMissingPlatformReply(answerText)) {
    return ['']
  }

  const matches = []
  let match = null

  while ((match = QUESTION_PREFIX_RE.exec(answerText)) !== null) {
    matches.push({
      index: match.index,
      fullMatch: match[0],
    })
  }

  if (matches.length === 0) {
    while ((match = NUMBERED_PREFIX_RE.exec(answerText)) !== null) {
      matches.push({
        index: match.index,
        fullMatch: match[0],
      })
    }
  }

  if (matches.length <= 1) {
    const cleaned = answerText
      .replace(/^(?:问题|Question)\s*\d+[：:]\s*/i, '')
      .replace(/^\d+\.\s+/, '')
      .trim()
    return [cleaned || answerText]
  }

  const parts = []
  for (let index = 0; index < matches.length; index += 1) {
    const current = matches[index]
    const next = matches[index + 1]
    const start = current.index + current.fullMatch.length
    const end = next ? next.index : answerText.length
    parts.push(answerText.substring(start, end).replace(/[\r\n]+$/, '').trim())
  }

  return parts.some(Boolean) ? parts : [answerText]
}

export const getInterviewAnswerForQuestion = (interview, questionIndex, platform) => {
  const answer = platform === 'twitter'
    ? interview.twitterAnswer
    : (interview.redditAnswer || interview.twitterAnswer)

  if (!answer || isMissingPlatformReply(answer)) {
    return answer || ''
  }

  const answers = splitAnswerByQuestions(answer)
  if (answers.length > 1 && questionIndex < answers.length) {
    return answers[questionIndex] || ''
  }

  return questionIndex === 0 ? answer : ''
}

export const parseInterview = (text) => {
  const result = {
    topic: '',
    agentCount: '',
    successCount: 0,
    totalCount: 0,
    selectionReason: '',
    interviews: [],
    summary: '',
  }

  try {
    const topicMatch = text.match(INTERVIEW_TOPIC_RE)
    if (topicMatch) {
      result.topic = topicMatch[1].trim()
    }

    const countMatch = text.match(INTERVIEW_COUNT_RE)
    if (countMatch) {
      result.successCount = parseInt(countMatch[1], 10)
      result.totalCount = parseInt(countMatch[2], 10)
      result.agentCount = `${countMatch[1]} / ${countMatch[2]}`
    }

    const reasonMatch = text.match(INTERVIEW_REASON_RE)
    if (reasonMatch) {
      result.selectionReason = reasonMatch[1].trim()
    }

    const individualReasons = parseIndividualReasons(result.selectionReason)
    const interviewBlocks = text.split(INTERVIEW_SPLIT_RE).slice(1)

    interviewBlocks.forEach((block, index) => {
      const interview = {
        num: index + 1,
        title: '',
        name: '',
        role: '',
        bio: '',
        selectionReason: '',
        questions: [],
        twitterAnswer: '',
        redditAnswer: '',
        quotes: [],
      }

      const titleMatch = block.match(/^(.+?)\n/)
      if (titleMatch) {
        interview.title = titleMatch[1].trim()
      }

      const nameRoleMatch = block.match(/\*\*(.+?)\*\*\s*\((.+?)\)/)
      if (nameRoleMatch) {
        interview.name = nameRoleMatch[1].trim()
        interview.role = nameRoleMatch[2].trim()
        interview.selectionReason = individualReasons[interview.name] || ''
      }

      const bioMatch = block.match(INTERVIEW_BIO_RE)
      if (bioMatch) {
        interview.bio = bioMatch[1].trim().replace(/\.\.\.$/, '...')
      }

      const questionMatch = block.match(QUESTION_SECTION_RE)
      if (questionMatch) {
        interview.questions = splitQuestions(questionMatch[1].trim())
      }

      const answerMatch = block.match(ANSWER_SECTION_RE)
      if (answerMatch) {
        const answerText = answerMatch[1].trim()
        const twitterMatch = answerText.match(TWITTER_SECTION_RE)
        const redditMatch = answerText.match(REDDIT_SECTION_RE)

        if (twitterMatch) {
          interview.twitterAnswer = twitterMatch[1].trim()
        }
        if (redditMatch) {
          interview.redditAnswer = redditMatch[1].trim()
        }

        if (!twitterMatch && redditMatch) {
          if (!isMissingPlatformReply(interview.redditAnswer)) {
            interview.twitterAnswer = interview.redditAnswer
          }
        } else if (twitterMatch && !redditMatch) {
          if (!isMissingPlatformReply(interview.twitterAnswer)) {
            interview.redditAnswer = interview.twitterAnswer
          }
        } else if (!twitterMatch && !redditMatch) {
          interview.twitterAnswer = answerText
        }
      }

      const quotesMatch = block.match(INTERVIEW_QUOTES_RE)
      if (quotesMatch) {
        let quoteMatches = quotesMatch[1].match(/> "([^"]+)"/g)
        if (!quoteMatches) {
          quoteMatches = quotesMatch[1].match(/> [\u201C""]([^\u201D""]+)[\u201D""]/g)
        }
        if (quoteMatches) {
          interview.quotes = quoteMatches
            .map((quote) => quote.replace(/^> [\u201C""]|[\u201D""]$/g, '').trim())
            .filter(Boolean)
        }
      }

      if (interview.name || interview.title) {
        result.interviews.push(interview)
      }
    })

    const summaryMatch = text.match(INTERVIEW_SUMMARY_RE)
    if (summaryMatch) {
      result.summary = summaryMatch[1].trim()
    }
  } catch (error) {
    console.warn('Parse interview failed:', error)
  }

  return result
}

export const parseQuickSearch = (text) => {
  const result = {
    query: '',
    count: 0,
    facts: [],
    edges: [],
    nodes: [],
  }

  try {
    const queryMatch = text.match(QUICK_QUERY_RE)
    if (queryMatch) {
      result.query = queryMatch[1].trim()
    }

    const countMatch = text.match(QUICK_COUNT_RE)
    if (countMatch) {
      result.count = parseInt(countMatch[1], 10)
    }

    const factsSection = text.match(QUICK_FACTS_RE)
    if (factsSection) {
      result.facts = collectNumberedLines(factsSection[1])
    }

    const edgesSection = text.match(QUICK_EDGES_RE)
    if (edgesSection) {
      result.edges = edgesSection[1]
        .split('\n')
        .filter((line) => line.trim().startsWith('-'))
        .map((line) => {
          const match = line.match(/^-\s*(.+?)\s*--\[(.+?)\]-->\s*(.+)$/)
          if (!match) {
            return null
          }
          return {
            source: match[1].trim(),
            relation: match[2].trim(),
            target: match[3].trim(),
          }
        })
        .filter(Boolean)
    }

    const nodesSection = text.match(QUICK_NODES_RE)
    if (nodesSection) {
      result.nodes = nodesSection[1]
        .split('\n')
        .filter((line) => line.trim().startsWith('-'))
        .map((line) => {
          const typedNode = line.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
          if (typedNode) {
            return { name: typedNode[1].trim(), type: typedNode[2].trim() }
          }
          const simpleNode = line.match(/^-\s*(.+)$/)
          if (simpleNode) {
            return { name: simpleNode[1].trim(), type: '' }
          }
          return null
        })
        .filter(Boolean)
    }
  } catch (error) {
    console.warn('Parse quick_search failed:', error)
  }

  return result
}

export const parseInsightForge = (text) => {
  const result = {
    query: '',
    simulationRequirement: '',
    stats: { facts: 0, entities: 0, relationships: 0 },
    subQueries: [],
    facts: [],
    entities: [],
    relations: [],
  }

  try {
    const queryMatch = text.match(INSIGHT_QUERY_RE)
    if (queryMatch) {
      result.query = queryMatch[1].trim()
    }

    const scenarioMatch = text.match(INSIGHT_SCENARIO_RE)
    if (scenarioMatch) {
      result.simulationRequirement = scenarioMatch[1].trim()
    }

    const factMatch = text.match(INSIGHT_FACT_COUNT_RE)
    const entityMatch = text.match(INSIGHT_ENTITY_COUNT_RE)
    const relationMatch = text.match(INSIGHT_RELATION_COUNT_RE)
    if (factMatch) {
      result.stats.facts = parseInt(factMatch[1], 10)
    }
    if (entityMatch) {
      result.stats.entities = parseInt(entityMatch[1], 10)
    }
    if (relationMatch) {
      result.stats.relationships = parseInt(relationMatch[1], 10)
    }

    const subQueriesSection = text.match(INSIGHT_SUBQUERIES_RE)
    if (subQueriesSection) {
      result.subQueries = collectNumberedLines(subQueriesSection[1])
    }

    const factsSection = text.match(INSIGHT_FACTS_RE)
    if (factsSection) {
      result.facts = collectNumberedLines(factsSection[1]).map((line) =>
        line.replace(/^"|"$/g, '').trim()
      )
    }

    const entitiesSection = text.match(INSIGHT_ENTITIES_RE)
    if (entitiesSection) {
      const entityBlocks = entitiesSection[1]
        .split(/\n(?=- \*\*)/)
        .filter((block) => block.trim().startsWith('- **'))

      result.entities = entityBlocks
        .map((block) => {
          const nameMatch = block.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
          return {
            name: nameMatch ? nameMatch[1].trim() : '',
            type: nameMatch ? nameMatch[2].trim() : '',
            summary: block.match(INSIGHT_ENTITY_SUMMARY_RE)?.[1]?.trim() || '',
            relatedFactsCount: parseInt(block.match(INSIGHT_ENTITY_RELATED_RE)?.[1] || '0', 10),
          }
        })
        .filter((entity) => entity.name)
    }

    const relationsSection = text.match(INSIGHT_RELATIONS_RE)
    if (relationsSection) {
      result.relations = relationsSection[1]
        .split('\n')
        .filter((line) => line.trim().startsWith('-'))
        .map((line) => {
          const match = line.match(/^-\s*(.+?)\s*--\[(.+?)\]-->\s*(.+)$/)
          if (!match) {
            return null
          }
          return {
            source: match[1].trim(),
            relation: match[2].trim(),
            target: match[3].trim(),
          }
        })
        .filter(Boolean)
    }
  } catch (error) {
    console.warn('Parse insight_forge failed:', error)
  }

  return result
}

export const parsePanorama = (text) => {
  const result = {
    query: '',
    stats: { nodes: 0, edges: 0, activeFacts: 0, historicalFacts: 0 },
    activeFacts: [],
    historicalFacts: [],
    entities: [],
  }

  try {
    const queryMatch = text.match(PANORAMA_QUERY_RE)
    if (queryMatch) {
      result.query = queryMatch[1].trim()
    }

    const nodesMatch = text.match(PANORAMA_NODES_RE)
    const edgesMatch = text.match(PANORAMA_EDGES_RE)
    const activeMatch = text.match(PANORAMA_ACTIVE_COUNT_RE)
    const historicalMatch = text.match(PANORAMA_HISTORICAL_COUNT_RE)
    if (nodesMatch) {
      result.stats.nodes = parseInt(nodesMatch[1], 10)
    }
    if (edgesMatch) {
      result.stats.edges = parseInt(edgesMatch[1], 10)
    }
    if (activeMatch) {
      result.stats.activeFacts = parseInt(activeMatch[1], 10)
    }
    if (historicalMatch) {
      result.stats.historicalFacts = parseInt(historicalMatch[1], 10)
    }

    const activeSection = text.match(PANORAMA_ACTIVE_RE)
    if (activeSection) {
      result.activeFacts = collectNumberedLines(activeSection[1]).map((line) =>
        line.replace(/^"|"$/g, '').trim()
      )
    }

    const historicalSection = text.match(PANORAMA_HISTORICAL_RE)
    if (historicalSection) {
      result.historicalFacts = collectNumberedLines(historicalSection[1]).map((line) =>
        line.replace(/^"|"$/g, '').trim()
      )
    }

    const entitiesSection = text.match(PANORAMA_ENTITIES_RE)
    if (entitiesSection) {
      result.entities = entitiesSection[1]
        .split('\n')
        .filter((line) => line.trim().startsWith('-'))
        .map((line) => {
          const typedNode = line.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
          if (!typedNode) {
            return null
          }
          return { name: typedNode[1].trim(), type: typedNode[2].trim() }
        })
        .filter(Boolean)
    }
  } catch (error) {
    console.warn('Parse panorama failed:', error)
  }

  return result
}

export const extractFinalContent = (response) => {
  if (!response) {
    return null
  }

  const finalAnswerTagMatch = response.match(/<final_answer>([\s\S]*?)<\/final_answer>/)
  if (finalAnswerTagMatch) {
    return finalAnswerTagMatch[1].trim()
  }

  const finalAnswerMatch = response.match(FINAL_ANSWER_RE)
  if (finalAnswerMatch) {
    return finalAnswerMatch[1].trim()
  }

  const chineseFinalMatch = response.match(CHINESE_FINAL_ANSWER_RE)
  if (chineseFinalMatch) {
    return chineseFinalMatch[1].trim()
  }

  const trimmedResponse = response.trim()
  if (/^[#>]/.test(trimmedResponse)) {
    return trimmedResponse
  }

  if (response.length > 300 && (response.includes('**') || response.includes('>'))) {
    const thoughtMatch = response.match(/^Thought:[\s\S]*?(?=\n\n[^T]|\n\n$)/i)
    if (thoughtMatch) {
      const afterThought = response.substring(thoughtMatch[0].length).trim()
      if (afterThought.length > 100) {
        return afterThought
      }
    }
  }

  return null
}
