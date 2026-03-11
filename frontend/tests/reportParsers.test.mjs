import test from 'node:test'
import assert from 'node:assert/strict'

import {
  extractFinalContent,
  getInterviewAnswerForQuestion,
  isMissingPlatformReply,
  parseInterview,
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

test('extractFinalContent accepts English and Chinese final-answer markers', () => {
  assert.equal(extractFinalContent('Final Answer:\nHello world'), 'Hello world')
  assert.equal(extractFinalContent('最终答案：\n你好，世界'), '你好，世界')
  assert.equal(extractFinalContent('<final_answer>done</final_answer>'), 'done')
})
