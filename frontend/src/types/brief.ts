export interface SummaryPayload {
  project_title: string
  problem?: string | null
  solution?: string | null
  target_users: string[]
  success_metrics: string[]
  constraints: string[]
  timeline?: string | null
  resources: string[]
  documents: string[]
  opportunity_areas: string[]
}

export interface LovableBrief {
  project_title: string
  project_description: string
  purpose: string
  expected_outcomes: string[]
  business_model: string[]
  constraints: string[]
  timeline: string
  target_users: string[]
  documents: string[]
  opportunity_areas: string[]
  suggested_reads: string[]
  ideas_board: string[]
  success_metrics: string[]
}

export interface BriefPayload {
  summary: SummaryPayload
  brief: LovableBrief
  follow_up_questions: string[]
  thread_id: string
  assistant_message: string
}

export interface ConversationTurn {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface DocumentReference {
  id: string
  name: string
  url?: string | null
  notes?: string | null
}

export interface BriefRunRequest {
  conversation?: ConversationTurn[]
  documents?: DocumentReference[]
  prompt?: string
  thread_id?: string
}
