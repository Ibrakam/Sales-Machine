export type LeadStatus = 'new' | 'in_progress' | 'completed'
export type LeadSource = 'website' | 'social' | 'call' | 'other'

export interface Lead {
  id: number
  name: string
  email?: string | null
  phone?: string | null
  company?: string | null
  status: LeadStatus
  source?: LeadSource
  source_data?: Record<string, unknown> | null
  tags?: string[] | null
  custom_fields?: Record<string, unknown> | null
  notes?: string | null
  created_at: string
  updated_at?: string | null
  score?: number
  score_category?: string
}

export interface LeadListResponse {
  items: Lead[]
  total: number
  page: number
  size: number
  pages: number
}

export type InteractionAuthor = 'admin' | 'client' | 'ai'

export interface LeadInteraction {
  id: number
  lead_id: number
  author_type: InteractionAuthor
  author_name?: string | null
  message: string
  context?: Record<string, unknown> | null
  created_at: string
}

export interface CreateLeadPayload {
  name: string
  email?: string
  phone?: string
  company?: string
  status?: LeadStatus
  source?: LeadSource
  notes?: string
  tags?: string[]
}

export interface UpdateLeadPayload extends Partial<CreateLeadPayload> {}

export interface CreateInteractionPayload {
  message: string
  author_type?: InteractionAuthor
  author_name?: string
  context?: Record<string, unknown>
}

export interface ChatHistoryMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatRequestPayload {
  message: string
  lead_id?: number
  history?: ChatHistoryMessage[]
}

export interface ChatResponsePayload {
  reply: string
  lead_id?: number
  model?: string | null
  usage?: {
    prompt_tokens?: number | null
    completion_tokens?: number | null
    total_tokens?: number | null
  } | null
}

export interface InstagramAccount {
  id: number
  username: string
  business_account_id?: string | null
  profile_url?: string | null
  followers_count?: number | null
  status: string
  connected_at?: string | null
  last_sync_at?: string | null
  created_at: string
  updated_at?: string | null
  integration_metadata?: Record<string, unknown> | null
}

export interface InstagramAccountPayload {
  username: string
  business_account_id?: string
  profile_url?: string
  followers_count?: number
  access_token?: string
  integration_metadata?: Record<string, unknown>
}

export interface InstagramSyncResponse {
  synced: number
  created_leads: Lead[]
}
