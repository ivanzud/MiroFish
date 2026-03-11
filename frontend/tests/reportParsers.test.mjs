import test from 'node:test'
import assert from 'node:assert/strict'

import {
  extractFinalContent,
  getInterviewAnswerForQuestion,
  isMissingPlatformReply,
  parseInterview,
  parseInsightForge,
  parsePanorama,
  parseQuickSearch,
} from '../src/components/reportParsers.js'

test('parseInterview supports the existing Chinese report-tool format', () => {
  const parsed = parseInterview(`**采访主题:** 武大处分事件后续
**采访人数:** 1 / 2

### 采访对象选择理由
1. **校友_345（index=1）**：作为校友代表，能观察舆情变化。

### 采访实录
#### 采访 #1:
校友
**校友_345** (校友代表)
_简介: 持续关注学校舆情。_

**Q:**
1. 你怎么看？
2. 下一步会怎样？

**A:**
【Twitter平台回答】
问题1：会先出现激烈讨论。

问题2：随后会逐渐回归理性。

【Reddit平台回答】
（该平台未获得回复）

**关键引言:**
> "会先出现激烈讨论。"

### 采访摘要与核心观点
校友群体预计会先激烈讨论，再回归理性。`)

  assert.equal(parsed.topic, '武大处分事件后续')
  assert.equal(parsed.agentCount, '1 / 2')
  assert.equal(parsed.interviews[0].bio, '持续关注学校舆情。')
  assert.deepEqual(parsed.interviews[0].questions, ['你怎么看？', '下一步会怎样？'])
  assert.equal(getInterviewAnswerForQuestion(parsed.interviews[0], 0, 'twitter'), '会先出现激烈讨论。')
  assert.equal(getInterviewAnswerForQuestion(parsed.interviews[0], 1, 'twitter'), '随后会逐渐回归理性。')
  assert.equal(parsed.summary, '校友群体预计会先激烈讨论，再回归理性。')
})

test('parseInterview supports English headings and placeholders', () => {
  const parsed = parseInterview(`**Interview Topic:** Campus policy fallout
**Interviewed Agents:** 1 / 3

### Why These Interviewees
1. **Alumni_12 (index=1)**: Represents the alumni audience.

### Interview Transcript
#### Interview #1:
Alumni Voice
**Alumni_12** (Alumni)
_Bio: Follows every school policy thread._

**Q:**
1. What happens first?
2. What happens next?

**A:**
【Twitter Reply】
Question 1: The discussion spikes immediately.

Question 2: It cools off after official clarification.

【Reddit Reply】
(No reply from this platform)

**Key Quotes:**
> "The discussion spikes immediately."

### Interview Summary and Key Takeaways
The audience reacts fast, then waits for clarification.`)

  assert.equal(parsed.topic, 'Campus policy fallout')
  assert.equal(parsed.agentCount, '1 / 3')
  assert.equal(parsed.interviews[0].selectionReason, 'Represents the alumni audience.')
  assert.deepEqual(parsed.interviews[0].questions, ['What happens first?', 'What happens next?'])
  assert.equal(getInterviewAnswerForQuestion(parsed.interviews[0], 0, 'twitter'), 'The discussion spikes immediately.')
  assert.equal(getInterviewAnswerForQuestion(parsed.interviews[0], 1, 'twitter'), 'It cools off after official clarification.')
  assert.equal(isMissingPlatformReply(parsed.interviews[0].redditAnswer), true)
  assert.equal(parsed.summary, 'The audience reacts fast, then waits for clarification.')
})

test('parseInterview accepts alternate English section labels and question prefixes', () => {
  const parsed = parseInterview(`**Topic:** Platform reaction outlook
**Agents Interviewed:** 1 / 2

### Selection Rationale
- Select Analyst_7: Covers cross-platform reaction patterns.

### Interview Transcript
#### Interview #1:
Analyst Desk
**Analyst_7** (Policy Analyst)
_Profile: Tracks how narratives move between communities._

**Questions:**
Question 1: What is the first visible shift?
Question 2: What follows after clarification?

**Answer:**
【Twitter Response】
Question 1: Engagement spikes around the accusation.

Question 2: Attention softens once official details arrive.

【Reddit Response】
[No Reply]

**Quotes:**
> "Engagement spikes around the accusation."

### Key Takeaways
The reaction peaks early, then moderates after clarification.`)

  assert.equal(parsed.topic, 'Platform reaction outlook')
  assert.equal(parsed.agentCount, '1 / 2')
  assert.equal(parsed.interviews[0].bio, 'Tracks how narratives move between communities.')
  assert.equal(parsed.interviews[0].selectionReason, 'Covers cross-platform reaction patterns.')
  assert.deepEqual(parsed.interviews[0].questions, [
    'What is the first visible shift?',
    'What follows after clarification?',
  ])
  assert.equal(
    getInterviewAnswerForQuestion(parsed.interviews[0], 0, 'twitter'),
    'Engagement spikes around the accusation.'
  )
  assert.equal(
    getInterviewAnswerForQuestion(parsed.interviews[0], 1, 'twitter'),
    'Attention softens once official details arrive.'
  )
  assert.equal(isMissingPlatformReply(parsed.interviews[0].redditAnswer), true)
  assert.equal(parsed.summary, 'The reaction peaks early, then moderates after clarification.')
})

test('parseQuickSearch supports both Chinese and English formats', () => {
  const chinese = parseQuickSearch(`搜索查询: 武大 处分
找到 2 条相关事实

### 相关事实:
1. 第一条事实
2. 第二条事实

### 相关边:
- 学校 --[发布]--> 通知

### 相关节点:
- **学校** (组织)
`)

  assert.equal(chinese.query, '武大 处分')
  assert.equal(chinese.count, 2)
  assert.deepEqual(chinese.facts, ['第一条事实', '第二条事实'])
  assert.deepEqual(chinese.edges, [{ source: '学校', relation: '发布', target: '通知' }])
  assert.deepEqual(chinese.nodes, [{ name: '学校', type: '组织' }])

  const english = parseQuickSearch(`Search Query: campus statement
Found 3 relevant facts

### Relevant Facts:
1. Fact one
2. Fact two
3. Fact three

### Related Edges:
- University --[issued]--> statement

### Related Nodes:
- **University** (Organization)
- Student forum
`)

  assert.equal(english.query, 'campus statement')
  assert.equal(english.count, 3)
  assert.deepEqual(english.facts, ['Fact one', 'Fact two', 'Fact three'])
  assert.deepEqual(english.edges, [{ source: 'University', relation: 'issued', target: 'statement' }])
  assert.deepEqual(english.nodes, [
    { name: 'University', type: 'Organization' },
    { name: 'Student forum', type: '' },
  ])
})

test('parseInsightForge supports both Chinese and English formats', () => {
  const chinese = parseInsightForge(`分析问题: 武大处分事件
预测场景: 未来一周舆情如何变化
相关预测事实: 2
涉及实体: 1
关系链: 1

### 分析的子问题
1. 官方会不会回应？
2. 舆情会不会降温？

### 【关键事实】
1. "学校已经发布通报"
2. "讨论仍在持续"

### 【核心实体】
- **学校** (组织)
摘要: "事件主体"
相关事实: 2

### 【关系链】
- 学校 --[发布]--> 通报
`)

  assert.equal(chinese.query, '武大处分事件')
  assert.equal(chinese.simulationRequirement, '未来一周舆情如何变化')
  assert.deepEqual(chinese.stats, { facts: 2, entities: 1, relationships: 1 })
  assert.deepEqual(chinese.subQueries, ['官方会不会回应？', '舆情会不会降温？'])
  assert.deepEqual(chinese.facts, ['学校已经发布通报', '讨论仍在持续'])
  assert.deepEqual(chinese.entities, [
    { name: '学校', type: '组织', summary: '事件主体', relatedFactsCount: 2 },
  ])
  assert.deepEqual(chinese.relations, [
    { source: '学校', relation: '发布', target: '通报' },
  ])

  const english = parseInsightForge(`Analysis Question: Campus discipline fallout
Prediction Scenario: How sentiment changes over the next week
Relevant Prediction Facts: 3
Entities Involved: 2
Relationship Chains: 1

### Analysis Subquestions
1. Will the school issue another statement?
2. Does discussion cool off after clarification?

### Key Facts
1. "The university already issued a statement"
2. "Students are still debating online"

### Core Entities
- **University** (Organization)
Summary: "Primary institution in the event"
Related Facts: 2
- **Student Forum** (Community)
Summary: "Tracks the reaction"
Related Facts: 1

### Relationship Chains
- University --[issued]--> statement
`)

  assert.equal(english.query, 'Campus discipline fallout')
  assert.equal(english.simulationRequirement, 'How sentiment changes over the next week')
  assert.deepEqual(english.stats, { facts: 3, entities: 2, relationships: 1 })
  assert.deepEqual(english.subQueries, [
    'Will the school issue another statement?',
    'Does discussion cool off after clarification?',
  ])
  assert.deepEqual(english.facts, [
    'The university already issued a statement',
    'Students are still debating online',
  ])
  assert.deepEqual(english.entities, [
    { name: 'University', type: 'Organization', summary: 'Primary institution in the event', relatedFactsCount: 2 },
    { name: 'Student Forum', type: 'Community', summary: 'Tracks the reaction', relatedFactsCount: 1 },
  ])
  assert.deepEqual(english.relations, [
    { source: 'University', relation: 'issued', target: 'statement' },
  ])
})

test('parsePanorama supports both Chinese and English formats', () => {
  const chinese = parsePanorama(`查询: 武大舆情
总节点数: 5
总边数: 4
当前有效事实: 2
历史/过期事实: 1

### 【当前有效事实】
1. "学校回应仍在传播"
2. "讨论热度开始下降"

### 【历史/过期事实】
1. "早期传言已失效"

### 【涉及实体】
- **学校** (组织)
- **校友** (群体)
`)

  assert.equal(chinese.query, '武大舆情')
  assert.deepEqual(chinese.stats, { nodes: 5, edges: 4, activeFacts: 2, historicalFacts: 1 })
  assert.deepEqual(chinese.activeFacts, ['学校回应仍在传播', '讨论热度开始下降'])
  assert.deepEqual(chinese.historicalFacts, ['早期传言已失效'])
  assert.deepEqual(chinese.entities, [
    { name: '学校', type: '组织' },
    { name: '校友', type: '群体' },
  ])

  const english = parsePanorama(`Query: campus sentiment
Total Nodes: 7
Total Edges: 9
Current Active Facts: 2
Historical/Expired Facts: 1

### Current Active Facts
1. "Official clarification is still being shared"
2. "Most replies are less heated now"

### Historical/Expired Facts
1. "An early rumor has been disproven"

### Entities Involved
- **University** (Organization)
- **Alumni** (Audience)
`)

  assert.equal(english.query, 'campus sentiment')
  assert.deepEqual(english.stats, { nodes: 7, edges: 9, activeFacts: 2, historicalFacts: 1 })
  assert.deepEqual(english.activeFacts, [
    'Official clarification is still being shared',
    'Most replies are less heated now',
  ])
  assert.deepEqual(english.historicalFacts, ['An early rumor has been disproven'])
  assert.deepEqual(english.entities, [
    { name: 'University', type: 'Organization' },
    { name: 'Alumni', type: 'Audience' },
  ])
})

test('extractFinalContent accepts English and Chinese final-answer markers', () => {
  assert.equal(extractFinalContent('Final Answer:\nHello world'), 'Hello world')
  assert.equal(extractFinalContent('最终答案：\n你好，世界'), '你好，世界')
  assert.equal(extractFinalContent('<final_answer>done</final_answer>'), 'done')
})
