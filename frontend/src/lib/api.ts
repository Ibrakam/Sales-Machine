import {
  ChatRequestPayload,
  ChatResponsePayload,
  CreateInteractionPayload,
  CreateLeadPayload,
  InstagramAccount,
  InstagramAccountPayload,
  InstagramSyncResponse,
  Lead,
  LeadInteraction,
  LeadListResponse,
  UpdateLeadPayload,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: number
  email: string
  name: string
  role: string
  is_active: boolean
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (options.headers) {
      Object.assign(headers, options.headers)
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Server error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) {
      return null as T
    }

    return response.json() as Promise<T>
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
    
    this.setToken(response.access_token)
    return response
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me')
  }

  async refreshToken(): Promise<LoginResponse> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await this.request<LoginResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    
    this.setToken(response.access_token)
    return response
  }

  logout() {
    this.setToken(null)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('refresh_token')
    }
  }

  // Leads
  async getLeads(): Promise<LeadListResponse> {
    return this.request<LeadListResponse>('/api/v1/leads/')
  }

  async createLead(lead: CreateLeadPayload): Promise<Lead> {
    return this.request<Lead>('/api/v1/leads/', {
      method: 'POST',
      body: JSON.stringify(lead),
    })
  }

  async updateLead(id: number, lead: UpdateLeadPayload): Promise<Lead> {
    return this.request<Lead>(`/api/v1/leads/${id}`, {
      method: 'PUT',
      body: JSON.stringify(lead),
    })
  }

  async deleteLead(id: number): Promise<void> {
    await this.request(`/api/v1/leads/${id}`, {
      method: 'DELETE',
    })
  }

  async getLeadInteractions(leadId: number): Promise<LeadInteraction[]> {
    return this.request<LeadInteraction[]>(`/api/v1/leads/${leadId}/interactions`)
  }

  async createLeadInteraction(
    leadId: number,
    payload: CreateInteractionPayload
  ): Promise<LeadInteraction> {
    return this.request<LeadInteraction>(`/api/v1/leads/${leadId}/interactions`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  // Chat with AI agent
  async chatWithAgent(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
    return this.request<ChatResponsePayload>('/api/v1/ai/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  // Messages
  async generateMessage(data: any) {
    return this.request('/api/v1/messages/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getMessages() {
    return this.request('/api/v1/messages/')
  }

  // Analytics
  async getAnalytics() {
    return this.request('/api/v1/analytics/')
  }

  // CRM
  async getCrmConnections() {
    return this.request('/api/v1/crm/connections')
  }

  async createCrmConnection(data: any) {
    return this.request('/api/v1/crm/connections', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Instagram
  async getInstagramAccount(): Promise<InstagramAccount | null> {
    return this.request<InstagramAccount | null>('/api/v1/instagram/account')
  }

  async upsertInstagramAccount(payload: InstagramAccountPayload): Promise<InstagramAccount> {
    return this.request<InstagramAccount>('/api/v1/instagram/account', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async updateInstagramAccount(payload: Partial<InstagramAccountPayload> & { status?: string }) {
    return this.request<InstagramAccount>('/api/v1/instagram/account', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  }

  async syncInstagram(): Promise<InstagramSyncResponse> {
    return this.request<InstagramSyncResponse>('/api/v1/instagram/sync', {
      method: 'POST',
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
