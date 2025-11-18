'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Edit3,
  Filter,
  Instagram,
  LayoutDashboard,
  Lightbulb,
  Loader2,
  Mail,
  Menu,
  MessageCircle,
  Phone,
  Plus,
  RefreshCw,
  Search,
  Share2,
  Sparkles,
  Target,
  Trash2,
  TrendingUp,
  UserCircle,
  Users,
  X,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { formatCurrency, formatDate, formatDateTime, formatNumber } from '@/lib/utils'
import type {
  ChatHistoryMessage,
  CreateInteractionPayload,
  CreateLeadPayload,
  InstagramAccount,
  Lead,
  LeadInteraction,
  LeadSource,
  LeadStatus,
} from '@/types'

type SectionId = 'dashboard' | 'leads' | 'chat' | 'social' | 'profile'

const leadStatuses: { value: LeadStatus; label: string }[] = [
  { value: 'new', label: 'New' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
]

const leadSources: { value: LeadSource; label: string }[] = [
  { value: 'website', label: 'Website' },
  { value: 'social', label: 'Social Media' },
  { value: 'call', label: 'Call' },
  { value: 'other', label: 'Other' },
]

const statusLabels: Record<LeadStatus, string> = {
  new: 'New',
  in_progress: 'In Progress',
  completed: 'Completed',
}

const sourceLabels: Record<LeadSource, string> = {
  website: 'Website',
  social: 'Social Media',
  call: 'Call',
  other: 'Other',
}

const statusStyles: Record<LeadStatus, string> = {
  new: 'bg-blue-500/15 text-blue-100 border border-blue-500/40',
  in_progress: 'bg-amber-500/15 text-amber-100 border border-amber-500/40',
  completed: 'bg-emerald-500/15 text-emerald-100 border border-emerald-500/40',
}

const sourceStyles: Record<LeadSource, string> = {
  website: 'bg-sky-500/15 text-sky-100 border border-sky-500/40',
  social: 'bg-fuchsia-500/15 text-fuchsia-100 border border-fuchsia-500/40',
  call: 'bg-violet-500/15 text-violet-100 border border-violet-500/40',
  other: 'bg-slate-500/15 text-slate-100 border border-slate-500/40',
}

const interactionStyles: Record<string, string> = {
  admin: 'bg-blue-500/10 border border-blue-500/30',
  ai: 'bg-gradient-to-r from-purple-600/80 to-blue-600/80 text-white border border-white/10',
  client: 'bg-slate-800/60 border border-white/10',
}

const sectionDescriptions: Record<SectionId, string> = {
  dashboard: 'Live overview of conversion metrics, velocity and assistant tips.',
  leads: 'Kanban-style board inspired by amoCRM with quick context pop-ups.',
  chat: 'Ask the AI manager for follow-ups, proposals and battle cards.',
  social: 'Connect Instagram to import conversations and automate tagging.',
  profile: 'Keep your workspace identity and security preferences updated.',
}

const sidebarItems: { id: SectionId; label: string; description: string; icon: LucideIcon }[] = [
  { id: 'dashboard', label: 'Dashboard', description: 'Stats & insights', icon: LayoutDashboard },
  { id: 'leads', label: 'Leads', description: 'Pipeline view', icon: Users },
  { id: 'chat', label: 'AI Chat', description: 'Virtual manager', icon: MessageCircle },
  { id: 'social', label: 'Social Networks', description: 'Instagram automation', icon: Share2 },
  { id: 'profile', label: 'Profile', description: 'Personal settings', icon: UserCircle },
]

const PIPELINE_CURRENCY = 'USD'

const emptyLeadForm: CreateLeadPayload = {
  name: '',
  company: '',
  email: '',
  phone: '',
  status: 'new',
  source: 'website',
  notes: '',
  tags: ['new'],
}

interface ToastState {
  type: 'success' | 'error'
  message: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface QuickLeadForm {
  name: string
  company: string
}

const isSameDay = (first: Date, second: Date) => {
  return (
    first.getFullYear() === second.getFullYear() &&
    first.getMonth() === second.getMonth() &&
    first.getDate() === second.getDate()
  )
}

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading: isAuthLoading, logout } = useAuth()

  const [activeSection, setActiveSection] = useState<SectionId>('dashboard')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isPageLoading, setIsPageLoading] = useState(true)
  const [leads, setLeads] = useState<Lead[]>([])
  const [leadError, setLeadError] = useState<string | null>(null)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [leadInteractions, setLeadInteractions] = useState<LeadInteraction[]>([])
  const [isLeadRefreshing, setIsLeadRefreshing] = useState(false)
  const [leadSearch, setLeadSearch] = useState('')
  const [leadStatusFilter, setLeadStatusFilter] = useState<LeadStatus | 'all'>('all')
  const [leadFormOpen, setLeadFormOpen] = useState(false)
  const [leadForm, setLeadForm] = useState<CreateLeadPayload>(emptyLeadForm)
  const [leadFormError, setLeadFormError] = useState<string | null>(null)
  const [isLeadSaving, setIsLeadSaving] = useState(false)
  const [quickLead, setQuickLead] = useState<QuickLeadForm>({ name: '', company: '' })
  const [isQuickSaving, setIsQuickSaving] = useState(false)
  const [newInteraction, setNewInteraction] = useState('')
  const [isInteractionSaving, setIsInteractionSaving] = useState(false)
  const [toast, setToast] = useState<ToastState | null>(null)

  const [chatLeadId, setChatLeadId] = useState<number | null>(null)
  const [chatHistory, setChatHistory] = useState<ChatHistoryMessage[]>([])
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatError, setChatError] = useState<string | null>(null)
  const [isChatLoading, setIsChatLoading] = useState(false)
  const chatBottomRef = useRef<HTMLDivElement | null>(null)

  const [instagramAccount, setInstagramAccount] = useState<InstagramAccount | null>(null)
  const [instagramForm, setInstagramForm] = useState({
    username: '',
    business_account_id: '',
    access_token: '',
  })
  const [instagramMessage, setInstagramMessage] = useState<string | null>(null)
  const [isInstagramSaving, setIsInstagramSaving] = useState(false)
  const [isInstagramSyncing, setIsInstagramSyncing] = useState(false)

  const [isLeadDetailsOpen, setIsLeadDetailsOpen] = useState(false)
  const [leadDetailsDraft, setLeadDetailsDraft] = useState<CreateLeadPayload>(emptyLeadForm)
  const [newTag, setNewTag] = useState('')
  const [isLeadUpdating, setIsLeadUpdating] = useState(false)

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3500)
      return () => clearTimeout(timer)
    }
  }, [toast])

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [chatMessages])

  useEffect(() => {
    if (selectedLead) {
      setLeadDetailsDraft({
        name: selectedLead.name ?? '',
        company: selectedLead.company ?? '',
        email: selectedLead.email ?? '',
        phone: selectedLead.phone ?? '',
        status: selectedLead.status,
        source: selectedLead.source ?? 'website',
        notes: selectedLead.notes ?? '',
        tags: selectedLead.tags ?? [],
      })
    } else {
      setLeadDetailsDraft(emptyLeadForm)
      setIsLeadDetailsOpen(false)
    }
  }, [selectedLead])

  useEffect(() => {
    if (isAuthLoading) {
      return
    }

    if (!user) {
      router.push('/auth/login')
      return
    }

    const bootstrap = async () => {
      try {
        setIsPageLoading(true)
        await Promise.all([loadLeads(), loadInstagramAccount()])
      } catch (error) {
        setLeadError(error instanceof Error ? error.message : 'Failed to load data')
      } finally {
        setIsPageLoading(false)
      }
    }

    bootstrap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, isAuthLoading, router])

  const loadLeads = async () => {
    try {
      setIsLeadRefreshing(true)
      const response = await apiClient.getLeads()
      setLeads(response.items)

      if (response.items.length > 0) {
        const leadToSelect = response.items.find((lead) => lead.id === selectedLead?.id) ?? response.items[0]
        setSelectedLead(leadToSelect)
        await loadLeadInteractions(leadToSelect.id)
      } else {
        setSelectedLead(null)
        setLeadInteractions([])
      }
    } catch (error) {
      setLeadError(error instanceof Error ? error.message : 'Error loading leads list')
    } finally {
      setIsLeadRefreshing(false)
    }
  }

  const loadLeadInteractions = async (leadId: number) => {
    try {
      const interactions = await apiClient.getLeadInteractions(leadId)
      setLeadInteractions(interactions)
    } catch (error) {
      setLeadError(error instanceof Error ? error.message : 'Failed to load lead history')
    }
  }

  const loadInstagramAccount = async () => {
    try {
      const account = await apiClient.getInstagramAccount()
      if (account) {
        setInstagramAccount(account)
        setInstagramForm({
          username: account.username,
          business_account_id: account.business_account_id ?? '',
          access_token: '',
        })
      }
    } catch (error) {
      setInstagramMessage(error instanceof Error ? error.message : 'Failed to get Instagram data')
    }
  }

  const filteredLeads = useMemo(() => {
    return leads.filter((lead) => {
      const matchesSearch =
        !leadSearch ||
        lead.name.toLowerCase().includes(leadSearch.toLowerCase()) ||
        (lead.email && lead.email.toLowerCase().includes(leadSearch.toLowerCase())) ||
        (lead.company && lead.company.toLowerCase().includes(leadSearch.toLowerCase()))

      const matchesStatus = leadStatusFilter === 'all' || lead.status === leadStatusFilter

      return matchesSearch && matchesStatus
    })
  }, [leads, leadSearch, leadStatusFilter])

  const pipelineSummary = useMemo(() => {
    return leadStatuses.map((status) => {
      const items = filteredLeads.filter((lead) => lead.status === status.value)
      const amount = items.reduce((sum, lead) => sum + (lead.score ?? 0), 0)
      return { ...status, count: items.length, amount }
    })
  }, [filteredLeads])

  const totalPipelineCount = useMemo(
    () => pipelineSummary.reduce((sum, column) => sum + column.count, 0),
    [pipelineSummary]
  )

  const totalPipelineValue = useMemo(
    () => pipelineSummary.reduce((sum, column) => sum + column.amount, 0),
    [pipelineSummary]
  )

  const leadStats = useMemo(() => {
    const total = leads.length
    const newCount = leads.filter((lead) => lead.status === 'new').length
    const inProgress = leads.filter((lead) => lead.status === 'in_progress').length
    const completed = leads.filter((lead) => lead.status === 'completed').length
    const social = leads.filter((lead) => lead.source === 'social').length
    const averageScore = total
      ? Math.round(
          leads.reduce((sum, lead) => sum + (lead.score ?? 0), 0) / total
        )
      : 0
    const conversionRate = total ? Math.round((completed / Math.max(total, 1)) * 100) : 0

    return {
      total,
      newCount,
      inProgress,
      completed,
      social,
      averageScore,
      conversionRate,
    }
  }, [leads])

  const weeklyActivity = useMemo(() => {
    const today = new Date()
    return Array.from({ length: 7 }).map((_, index) => {
      const date = new Date()
      date.setDate(today.getDate() - (6 - index))
      const count = leads.filter((lead) => isSameDay(new Date(lead.created_at), date)).length
      return {
        label: date.toLocaleDateString('en-US', { weekday: 'short' }),
        count,
      }
    })
  }, [leads])

  const pipelineDistribution = useMemo(() => {
    return leadStatuses.map((status) => ({
      ...status,
      count: leads.filter((lead) => lead.status === status.value).length,
    }))
  }, [leads])

  const dashboardTips = useMemo(() => {
    return [
      {
        title: 'Prioritize warm conversations',
        description: `${leadStats.inProgress} leads are waiting for the next touchpoint. Block 30 minutes for callbacks today.`,
      },
      {
        title: 'Instagram is working',
        description: `${leadStats.social} contacts came from social media. Enable auto syncing to keep the pipeline filled.`,
      },
      {
        title: 'Use AI for victory plans',
        description: 'Open the AI chat and ask for a battle card or pricing scenario before every call.',
      },
    ]
  }, [leadStats.inProgress, leadStats.social])

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type })
  }

  const handleOpenLeadForm = () => {
    setLeadForm(emptyLeadForm)
    setLeadFormError(null)
    setLeadFormOpen(true)
  }

  const handleLeadSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!leadForm.name.trim()) {
      setLeadFormError('Please specify lead name')
      return
    }

    setIsLeadSaving(true)
    setLeadFormError(null)
    try {
      await apiClient.createLead({
        ...leadForm,
        status: leadForm.status ?? 'new',
        source: leadForm.source ?? 'website',
        tags: leadForm.tags?.filter(Boolean),
      })
      showToast('Lead created successfully')
      setLeadFormOpen(false)
      await loadLeads()
      setActiveSection('leads')
    } catch (error) {
      setLeadFormError(error instanceof Error ? error.message : 'Failed to create lead')
    } finally {
      setIsLeadSaving(false)
    }
  }

  const handleQuickLeadAdd = async () => {
    if (!quickLead.name.trim()) {
      showToast('Add a name to create a lead', 'error')
      return
    }

    setIsQuickSaving(true)
    try {
      await apiClient.createLead({
        name: quickLead.name.trim(),
        company: quickLead.company.trim() || undefined,
        status: 'new',
        source: 'website',
        tags: ['new'],
      })
      setQuickLead({ name: '', company: '' })
      showToast('Lead added to pipeline')
      await loadLeads()
      setActiveSection('leads')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Failed to add lead', 'error')
    } finally {
      setIsQuickSaving(false)
    }
  }

  const handleLeadUpdate = async (payload: Partial<CreateLeadPayload>) => {
    if (!selectedLead) return
    try {
      const updated = await apiClient.updateLead(selectedLead.id, payload)
      setLeads((prev) => prev.map((lead) => (lead.id === updated.id ? updated : lead)))
      setSelectedLead(updated)
      showToast('Lead data updated')
    } catch (error) {
      setLeadError(error instanceof Error ? error.message : 'Failed to update lead')
    }
  }

  const handleLeadDetailsSave = async () => {
    if (!selectedLead) return
    setIsLeadUpdating(true)
    try {
      await handleLeadUpdate({
        name: leadDetailsDraft.name,
        company: leadDetailsDraft.company,
        email: leadDetailsDraft.email,
        phone: leadDetailsDraft.phone,
        status: leadDetailsDraft.status,
        source: leadDetailsDraft.source,
        notes: leadDetailsDraft.notes,
      })
    } finally {
      setIsLeadUpdating(false)
    }
  }

  const handleAddTag = async () => {
    if (!selectedLead) return
    if (!newTag.trim()) return
    const tags = Array.from(new Set([...(selectedLead.tags ?? []), newTag.trim()]))
    await handleLeadUpdate({ tags })
    setNewTag('')
  }

  const handleRemoveTag = async (tag: string) => {
    if (!selectedLead) return
    const tags = (selectedLead.tags ?? []).filter((item) => item !== tag)
    await handleLeadUpdate({ tags })
  }

  const handleLeadCardOpen = (lead: Lead) => {
    setSelectedLead(lead)
    setIsLeadDetailsOpen(true)
    loadLeadInteractions(lead.id)
  }

  const handleDeleteLead = async () => {
    if (!selectedLead) return
    if (!confirm('Delete this lead?')) return

    try {
      await apiClient.deleteLead(selectedLead.id)
      showToast('Lead deleted', 'success')
      setIsLeadDetailsOpen(false)
      await loadLeads()
    } catch (error) {
      setLeadError(error instanceof Error ? error.message : 'Failed to delete lead')
    }
  }

  const handleInteractionSubmit = async () => {
    if (!selectedLead || !newInteraction.trim()) {
      return
    }

    const payload: CreateInteractionPayload = {
      message: newInteraction.trim(),
      author_type: 'admin',
    }

    setIsInteractionSaving(true)
    try {
      await apiClient.createLeadInteraction(selectedLead.id, payload)
      setNewInteraction('')
      await loadLeadInteractions(selectedLead.id)
      showToast('Comment saved')
    } catch (error) {
      setLeadError(error instanceof Error ? error.message : 'Failed to save comment')
    } finally {
      setIsInteractionSaving(false)
    }
  }

  const handleChatSend = async () => {
    const message = chatInput.trim()
    if (!message) return

    setChatError(null)
    setChatInput('')
    const timestamp = new Date().toISOString()
    setChatMessages((prev) => [...prev, { role: 'user', content: message, timestamp }])
    setChatHistory((prev) => [...prev, { role: 'user', content: message }])
    setIsChatLoading(true)

    try {
      const response = await apiClient.chatWithAgent({
        message,
        lead_id: chatLeadId ?? undefined,
        history: chatHistory,
      })

      const reply = response.reply || 'Ready for next questions!'
      const replyTimestamp = new Date().toISOString()

      setChatMessages((prev) => [...prev, { role: 'assistant', content: reply, timestamp: replyTimestamp }])
      setChatHistory((prev) => [...prev, { role: 'assistant', content: reply }])

      if (chatLeadId && selectedLead?.id === chatLeadId) {
        await loadLeadInteractions(chatLeadId)
      }
    } catch (error) {
      setChatError(error instanceof Error ? error.message : 'AI agent temporarily unavailable')
    } finally {
      setIsChatLoading(false)
    }
  }

  const handleInstagramSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!instagramForm.username.trim()) {
      setInstagramMessage('Please specify Instagram business account username')
      return
    }

    setIsInstagramSaving(true)
    setInstagramMessage(null)
    try {
      const account = await apiClient.upsertInstagramAccount({
        username: instagramForm.username.trim(),
        business_account_id: instagramForm.business_account_id || undefined,
        access_token: instagramForm.access_token || undefined,
      })
      setInstagramAccount(account)
      showToast('Instagram account connected')
    } catch (error) {
      setInstagramMessage(error instanceof Error ? error.message : 'Failed to connect account')
    } finally {
      setIsInstagramSaving(false)
    }
  }

  const handleInstagramSync = async () => {
    setIsInstagramSyncing(true)
    setInstagramMessage(null)
    try {
      const result = await apiClient.syncInstagram()
      setInstagramMessage(`Leads imported: ${result.synced}`)
      await loadLeads()
      setActiveSection('leads')
    } catch (error) {
      setInstagramMessage(error instanceof Error ? error.message : 'Failed to sync leads')
    } finally {
      setIsInstagramSyncing(false)
    }
  }

  const activeItem = sidebarItems.find((item) => item.id === activeSection)
  const weeklyMax = Math.max(1, ...weeklyActivity.map((day) => day.count))
  const pipelineMax = Math.max(1, ...pipelineDistribution.map((item) => item.count))

  if (isPageLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl">
            <Sparkles className="w-8 h-8 text-white animate-pulse" />
          </div>
          <p className="text-lg text-white/80">Loading workspace...</p>
        </div>
      </div>
    )
  }

  const renderHeaderAction = () => {
    if (activeSection === 'leads') {
      return (
        <Button onClick={handleOpenLeadForm} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Lead
        </Button>
      )
    }

    if (activeSection === 'social') {
      return (
        <Button onClick={handleInstagramSync} disabled={isInstagramSyncing} className="gap-2">
          {isInstagramSyncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Sync Instagram
        </Button>
      )
    }

    if (activeSection === 'chat') {
      return (
        <Button
          variant="secondary"
          className="gap-2"
          onClick={() => {
            setChatMessages([])
            setChatHistory([])
          }}
        >
          <Sparkles className="h-4 w-4" />
          Reset Thread
        </Button>
      )
    }

    return null
  }

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
          <Target className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-sm uppercase tracking-wide text-white/60">AI Sales Assistant</p>
          <p className="text-lg font-semibold text-white">Revenue Hub</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {sidebarItems.map((item) => {
          const Icon = item.icon
          const isActive = activeSection === item.id
          return (
            <button
              key={item.id}
              onClick={() => {
                setActiveSection(item.id)
                setIsSidebarOpen(false)
              }}
              className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left transition ${
                isActive ? 'bg-white/10 text-white shadow-lg shadow-blue-500/20' : 'text-white/70 hover:bg-white/5'
              }`}
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-500' : 'bg-slate-800/80'}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold">{item.label}</p>
                <p className="text-xs text-white/60">{item.description}</p>
              </div>
            </button>
          )
        })}
      </nav>
      <div className="border-t border-white/5 px-5 py-6 text-sm text-white/60">
        <p>Need help? Ping the AI manager for scripts or connect support@team.</p>
      </div>
    </div>
  )

  return (
    <div className="relative flex min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-purple-950 text-white">
      <button
        className="fixed left-4 top-4 z-40 flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-white shadow-lg md:hidden"
        onClick={() => setIsSidebarOpen(true)}
      >
        <Menu className="h-5 w-5" />
      </button>

      <aside className="hidden w-64 flex-col border-r border-white/5 bg-slate-950/80 md:flex xl:w-72">
        {sidebarContent}
      </aside>

      {isSidebarOpen && (
        <div className="fixed inset-0 z-30 flex md:hidden">
          <div className="w-72 border-r border-white/5 bg-slate-950/95">
            {sidebarContent}
          </div>
          <div className="flex-1 bg-black/40" onClick={() => setIsSidebarOpen(false)} />
        </div>
      )}

      <div className="flex flex-1 flex-col">
        <header className="border-b border-white/5 bg-white/5 px-4 py-4 backdrop-blur md:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-wide text-white/60">Workspace · {activeItem?.label}</p>
              <h1 className="text-3xl font-semibold">{activeItem?.label}</h1>
              <p className="text-white/70">{sectionDescriptions[activeSection]}</p>
            </div>
            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              {renderHeaderAction()}
              <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-2">
                <div className="text-right">
                  <p className="text-sm font-semibold">{user?.email}</p>
                  <p className="text-xs text-white/60">{user?.role}</p>
                </div>
                <Button variant="outline" size="sm" onClick={logout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-10">
          {toast && (
            <Alert
              variant={toast.type === 'error' ? 'destructive' : 'default'}
              className="mb-6 border-white/10 bg-white/10 text-white backdrop-blur"
            >
              <AlertTitle>{toast.type === 'error' ? 'Error' : 'Success'}</AlertTitle>
              <AlertDescription>{toast.message}</AlertDescription>
            </Alert>
          )}

          {leadError && (
            <Alert variant="destructive" className="mb-6 border-red-500/40 bg-red-500/10 text-red-100">
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>{leadError}</AlertDescription>
            </Alert>
          )}

          {activeSection === 'dashboard' && (
            <div className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <Card className="border-white/5 bg-white/5 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0">
                    <div>
                      <CardDescription className="text-xs uppercase tracking-wide text-white/60">Pipeline</CardDescription>
                      <CardTitle className="text-3xl">{formatNumber(leadStats.total)}</CardTitle>
                    </div>
                    <div className="rounded-2xl bg-white/10 p-3">
                      <Users className="h-5 w-5" />
                    </div>
                  </CardHeader>
                  <CardContent className="text-sm text-white/70">Total leads in workspace</CardContent>
                </Card>
                <Card className="border-white/5 bg-white/5 text-white">
                  <CardHeader className="flex flex-col space-y-1">
                    <CardDescription className="text-xs uppercase tracking-wide text-white/60">In Progress</CardDescription>
                    <CardTitle className="text-3xl">{formatNumber(leadStats.inProgress)}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-white/70">Actively negotiated deals</CardContent>
                </Card>
                <Card className="border-white/5 bg-white/5 text-white">
                  <CardHeader className="flex flex-col space-y-1">
                    <CardDescription className="text-xs uppercase tracking-wide text-white/60">Conversion</CardDescription>
                    <CardTitle className="text-3xl">{leadStats.conversionRate}%</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-white/70">Won vs total</CardContent>
                </Card>
                <Card className="border-white/5 bg-white/5 text-white">
                  <CardHeader className="flex flex-col space-y-1">
                    <CardDescription className="text-xs uppercase tracking-wide text-white/60">Avg. Lead Score</CardDescription>
                    <CardTitle className="text-3xl">{formatNumber(leadStats.averageScore)}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-white/70">AI priority indicator</CardContent>
                </Card>
              </div>

              <div className="grid gap-6 lg:grid-cols-3">
                <Card className="border-white/5 bg-white/5 text-white lg:col-span-2">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle>Weekly Activity</CardTitle>
                      <CardDescription className="text-white/70">Leads created by day</CardDescription>
                    </div>
                    <TrendingUp className="h-5 w-5 text-emerald-300" />
                  </CardHeader>
                  <CardContent>
                    <div className="flex h-56 items-end gap-4">
                      {weeklyActivity.map((day) => (
                        <div key={day.label} className="flex flex-1 flex-col items-center gap-2">
                          <div className="flex h-44 w-10 items-end rounded-full border border-white/10 bg-white/5">
                            <div
                              className="w-full rounded-full bg-gradient-to-t from-blue-500 to-purple-500"
                              style={{ height: `${(day.count / weeklyMax) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-white/60">{day.label}</span>
                          <span className="text-xs font-semibold">{day.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-white/5 bg-white/5 text-white">
                  <CardHeader>
                    <CardTitle>Pipeline Health</CardTitle>
                    <CardDescription className="text-white/70">Status distribution</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {pipelineDistribution.map((item) => (
                      <div key={item.value}>
                        <div className="flex items-center justify-between text-sm">
                          <span>{item.label}</span>
                          <span className="text-white/60">{item.count}</span>
                        </div>
                        <div className="mt-2 h-2 rounded-full bg-white/10">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                            style={{ width: `${(item.count / pipelineMax) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                {dashboardTips.map((tip) => (
                  <div key={tip.title} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                    <Lightbulb className="h-6 w-6 text-amber-300" />
                    <h3 className="mt-4 text-lg font-semibold">{tip.title}</h3>
                    <p className="text-sm text-white/70">{tip.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'leads' && (
            <div className="space-y-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex flex-1 flex-wrap gap-3">
                  <div className="relative min-w-[220px] flex-1">
                    <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <Input
                      value={leadSearch}
                      onChange={(event) => setLeadSearch(event.target.value)}
                      placeholder="Search by name, company or email"
                      className="h-12 rounded-2xl border-white/20 bg-white/5 pl-12"
                    />
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm">
                    <Filter className="h-4 w-4" />
                    <select
                      value={leadStatusFilter}
                      onChange={(event) => setLeadStatusFilter(event.target.value as LeadStatus | 'all')}
                      className="bg-transparent text-sm font-medium outline-none"
                    >
                      <option value="all">All statuses</option>
                      {leadStatuses.map((status) => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Button
                    variant="outline"
                    className="gap-2 rounded-2xl"
                    onClick={loadLeads}
                    disabled={isLeadRefreshing}
                  >
                    {isLeadRefreshing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    Refresh
                  </Button>
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="flex flex-wrap gap-6">
                    <div>
                      <p className="text-xs uppercase text-white/60">Active deals</p>
                      <p className="text-2xl font-semibold">{formatNumber(totalPipelineCount)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase text-white/60">Pipeline value</p>
                      <p className="text-2xl font-semibold">
                        {formatCurrency(totalPipelineValue, PIPELINE_CURRENCY)}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {pipelineSummary.map((column) => (
                      <div
                        key={column.value}
                        className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-2 text-xs"
                      >
                        <p className="font-semibold text-white">{column.label}</p>
                        <p className="text-white/60">
                          {formatNumber(column.count)} • {formatCurrency(column.amount, PIPELINE_CURRENCY)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                {leadStatuses.map((status) => {
                  const columnLeads = filteredLeads.filter((lead) => lead.status === status.value)
                  const columnSummary = pipelineSummary.find((item) => item.value === status.value)
                  const columnAmount = columnSummary?.amount ?? 0
                  const columnCount = columnSummary?.count ?? columnLeads.length
                  const isNewColumn = status.value === 'new'
                  return (
                    <div key={status.value} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-xs uppercase text-white/60">{status.label}</p>
                          <p className="text-2xl font-semibold">{formatNumber(columnCount)}</p>
                          <p className="text-sm text-white/60">
                            {formatCurrency(columnAmount, PIPELINE_CURRENCY)}
                          </p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[status.value]}`}>
                          {status.label}
                        </span>
                      </div>
                      <div className="mt-4 space-y-3">
                        {isNewColumn && (
                          <div className="rounded-2xl border border-dashed border-white/25 bg-slate-950/40 p-4">
                            <p className="text-sm font-semibold text-white">Quick add</p>
                            <p className="text-xs text-white/60">Save a lead in two fields, details can wait.</p>
                            <Input
                              value={quickLead.name}
                              onChange={(event) => setQuickLead({ ...quickLead, name: event.target.value })}
                              placeholder="Lead name"
                              className="mt-3 rounded-xl border-white/10 bg-slate-950/70"
                            />
                            <Input
                              value={quickLead.company}
                              onChange={(event) => setQuickLead({ ...quickLead, company: event.target.value })}
                              placeholder="Company"
                              className="mt-2 rounded-xl border-white/10 bg-slate-950/70"
                            />
                            <Button
                              onClick={handleQuickLeadAdd}
                              disabled={isQuickSaving}
                              className="mt-3 w-full gap-2 rounded-xl"
                            >
                              {isQuickSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                              Add to board
                            </Button>
                          </div>
                        )}
                        {columnLeads.length === 0 && (
                          <p className="rounded-2xl border border-dashed border-white/20 bg-slate-900/30 p-4 text-sm text-white/50">
                            Nothing here yet
                          </p>
                        )}
                        {columnLeads.map((lead) => {
                          const leadValue =
                            typeof lead.score === 'number'
                              ? formatCurrency(lead.score, PIPELINE_CURRENCY)
                              : null
                          const contactLine = lead.email || lead.phone || 'No contacts yet'
                          return (
                            <button
                              key={lead.id}
                              onClick={() => handleLeadCardOpen(lead)}
                              className={`group w-full rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-left shadow-sm transition hover:border-blue-400/60 hover:bg-slate-950 ${
                                selectedLead?.id === lead.id && isLeadDetailsOpen ? 'ring-2 ring-blue-400/60' : ''
                              }`}
                            >
                              <div className="flex items-center justify-between text-sm font-semibold">
                                <span>{lead.name}</span>
                                {leadValue && <span className="text-xs text-white/60">{leadValue}</span>}
                              </div>
                              <p className="mt-1 text-xs text-white/60">{lead.company || 'Company not specified'}</p>
                              <div className="mt-3 text-[11px] text-white/60">
                                <div className="flex items-center justify-between">
                                  <span className="truncate">{contactLine}</span>
                                  <span>{formatDate(lead.created_at)}</span>
                                </div>
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {lead.tags?.length ? (
                                    lead.tags.slice(0, 3).map((tag) => (
                                      <span key={tag} className="rounded-full bg-white/10 px-2 py-1 text-white/70">
                                        #{tag}
                                      </span>
                                    ))
                                  ) : (
                                    <span className="text-white/40">No tags</span>
                                  )}
                                  {lead.source && (
                                    <span className={`rounded-full px-2 py-1 ${sourceStyles[lead.source]}`}>
                                      {sourceLabels[lead.source]}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <p className="mt-3 text-[11px] text-blue-200 opacity-0 transition group-hover:opacity-100">
                                Open card →
                              </p>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {activeSection === 'chat' && (
            <div className="grid gap-6 lg:grid-cols-3">
              <Card className="border-white/10 bg-white/5 text-white lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-200" />
                    AI Chat with Virtual Manager
                  </CardTitle>
                  <CardDescription className="text-white/70">
                    Ask for follow-up scripts, commercial proposals or qualification ideas. The assistant adapts to context.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <div>
                      <Label className="text-xs uppercase text-white/60">Lead Context</Label>
                      <select
                        value={chatLeadId ?? ''}
                        onChange={(event) => {
                          const value = event.target.value
                          setChatLeadId(value ? Number(value) : null)
                          setChatHistory([])
                          setChatMessages([])
                        }}
                        className="mt-1 rounded-2xl border border-white/20 bg-white/5 px-3 py-2 text-sm text-white"
                      >
                        <option value="">No context</option>
                        {leads.map((lead) => (
                          <option key={lead.id} value={lead.id}>
                            {lead.name} — {statusLabels[lead.status]}
                          </option>
                        ))}
                      </select>
                    </div>
                    {chatLeadId && (
                      <div className="rounded-2xl border border-white/20 bg-white/5 px-4 py-2 text-xs text-white/70">
                        AI will use timeline and notes for tone and personalization.
                      </div>
                    )}
                  </div>

                  <div className="h-[420px] space-y-3 overflow-y-auto rounded-3xl border border-white/10 bg-slate-950/40 p-4">
                    {chatMessages.length === 0 ? (
                      <div className="flex h-full flex-col items-center justify-center space-y-3 text-center text-white/60">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/10">
                          <MessageCircle className="h-6 w-6" />
                        </div>
                        <p>Ask the assistant to plan a cadence, polish an answer or draft a contract intro.</p>
                      </div>
                    ) : (
                      chatMessages.map((message, index) => (
                        <div key={`${message.timestamp}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div
                            className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                              message.role === 'user'
                                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                                : 'bg-white/10 text-white border border-white/10'
                            }`}
                          >
                            <p>{message.content}</p>
                            <span className="mt-2 block text-[10px] text-white/60">{formatDateTime(message.timestamp)}</span>
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={chatBottomRef} />
                  </div>

                  {chatError && (
                    <Alert variant="destructive" className="border-red-400/40 bg-red-500/10 text-red-100">
                      <AlertTitle>Error</AlertTitle>
                      <AlertDescription>{chatError}</AlertDescription>
                    </Alert>
                  )}

                  <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                    <Label className="text-xs uppercase text-white/60">Your request</Label>
                    <textarea
                      value={chatInput}
                      onChange={(event) => setChatInput(event.target.value)}
                      placeholder="For example: Draft a discovery call recap for this client focusing on automation ROI."
                      className="mt-2 min-h-[120px] w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm text-white placeholder:text-white/50 focus:border-blue-400 focus:outline-none"
                    />
                    <div className="mt-3 flex justify-end">
                      <Button onClick={handleChatSend} disabled={isChatLoading} className="gap-2">
                        {isChatLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                        Send to AI
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-white/5 text-white">
                <CardHeader>
                  <CardTitle>Conversation shortcuts</CardTitle>
                  <CardDescription className="text-white/70">Use prompts to move faster</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-white/70">
                  <p>• "Summarize the last touchpoints for lead X and list blockers."</p>
                  <p>• "Prepare a three-step nurture plan for social media leads."</p>
                  <p>• "Draft pricing arguments comparing in-house vs outsourcing."</p>
                  <p>• "Generate a follow-up email with urgency and specific next steps."</p>
                </CardContent>
              </Card>
            </div>
          )}

          {activeSection === 'social' && (
            <div className="space-y-6">
              <div className="grid gap-6 lg:grid-cols-3">
                <Card className="border-white/10 bg-white/5 text-white lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Instagram integration</CardTitle>
                    <CardDescription className="text-white/70">Connect the business account to import dialogs as leads</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleInstagramSubmit} className="space-y-4">
                      <div>
                        <Label className="text-xs uppercase text-white/60">Username</Label>
                        <Input
                          value={instagramForm.username}
                          onChange={(event) => setInstagramForm({ ...instagramForm, username: event.target.value })}
                          placeholder="@company-account"
                          className="mt-2 rounded-2xl border-white/20 bg-white/5"
                        />
                      </div>
                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <Label className="text-xs uppercase text-white/60">Business Account ID</Label>
                          <Input
                            value={instagramForm.business_account_id}
                            onChange={(event) =>
                              setInstagramForm({ ...instagramForm, business_account_id: event.target.value })
                            }
                            placeholder="1784..."
                            className="mt-2 rounded-2xl border-white/20 bg-white/5"
                          />
                        </div>
                        <div>
                          <Label className="text-xs uppercase text-white/60">Access Token</Label>
                          <Input
                            value={instagramForm.access_token}
                            onChange={(event) => setInstagramForm({ ...instagramForm, access_token: event.target.value })}
                            placeholder="EAAG..."
                            className="mt-2 rounded-2xl border-white/20 bg-white/5"
                          />
                        </div>
                      </div>
                      <div className="flex flex-wrap items-center gap-3">
                        <Button type="submit" disabled={isInstagramSaving} className="gap-2">
                          {isInstagramSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Instagram className="h-4 w-4" />}
                          Connect account
                        </Button>
                        <Button
                          type="button"
                          variant="secondary"
                          className="gap-2"
                          onClick={handleInstagramSync}
                          disabled={isInstagramSyncing}
                        >
                          {isInstagramSyncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                          Import new leads
                        </Button>
                      </div>
                      {instagramMessage && (
                        <p className="text-sm text-white/70">{instagramMessage}</p>
                      )}
                    </form>
                  </CardContent>
                </Card>

                <Card className="border-white/10 bg-white/5 text-white">
                  <CardHeader>
                    <CardTitle>Connection status</CardTitle>
                    <CardDescription className="text-white/70">Current channel insights</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    {instagramAccount ? (
                      <>
                        <p><span className="text-white/60">Username:</span> {instagramAccount.username}</p>
                        <p><span className="text-white/60">Status:</span> {instagramAccount.status}</p>
                        {instagramAccount.last_sync_at && (
                          <p><span className="text-white/60">Last sync:</span> {formatDateTime(instagramAccount.last_sync_at)}</p>
                        )}
                        <p><span className="text-white/60">Connected on:</span> {formatDate(instagramAccount.connected_at ?? instagramAccount.created_at)}</p>
                      </>
                    ) : (
                      <p className="text-white/70">No account connected yet.</p>
                    )}
                    <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4 text-xs text-white/70">
                      Leads are tagged automatically with source "social" and keep original message context.
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {activeSection === 'profile' && (
            <div className="grid gap-6 lg:grid-cols-3">
              <Card className="border-white/10 bg-white/5 text-white lg:col-span-2">
                <CardHeader>
                  <CardTitle>Personal profile</CardTitle>
                  <CardDescription className="text-white/70">Workspace identity visible to the team</CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label className="text-xs uppercase text-white/60">Full Name</Label>
                    <Input
                      value={user?.name || ''}
                      readOnly
                      className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                    />
                    <p className="mt-1 text-xs text-white/50">Editable soon</p>
                  </div>
                  <div>
                    <Label className="text-xs uppercase text-white/60">Email</Label>
                    <Input value={user?.email || ''} readOnly className="mt-2 rounded-2xl border-white/20 bg-slate-950/40" />
                  </div>
                  <div>
                    <Label className="text-xs uppercase text-white/60">Role</Label>
                    <Input value={user?.role || ''} readOnly className="mt-2 rounded-2xl border-white/20 bg-slate-950/40" />
                  </div>
                  <div>
                    <Label className="text-xs uppercase text-white/60">Notifications</Label>
                    <Input value="Enabled" readOnly className="mt-2 rounded-2xl border-white/20 bg-slate-950/40" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-white/5 text-white">
                <CardHeader>
                  <CardTitle>Security</CardTitle>
                  <CardDescription className="text-white/70">Two-factor and tokens</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-white/70">
                  <p>• MFA is recommended for admins.</p>
                  <p>• Rotate API tokens every 90 days.</p>
                  <Button variant="secondary" className="w-full">Generate new token</Button>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>

      {selectedLead && isLeadDetailsOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center overflow-y-auto bg-slate-950/80 px-4 py-6 sm:px-6 sm:py-10">
          <div className="w-full max-w-5xl rounded-3xl border border-white/10 bg-slate-950 text-white shadow-2xl">
            <div className="flex max-h-[92vh] flex-col overflow-hidden">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 px-6 py-5">
                <div>
                  <p className="text-xs uppercase text-white/60">Lead card</p>
                  <h2 className="text-2xl font-semibold">{selectedLead.name}</h2>
                  <p className="text-sm text-white/60">{selectedLead.company || 'No company specified'}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="secondary"
                    className="gap-2"
                    onClick={() => {
                      setChatLeadId(selectedLead.id)
                      setChatHistory([])
                      setChatMessages([])
                      setIsLeadDetailsOpen(false)
                      setActiveSection('chat')
                    }}
                  >
                    <Sparkles className="h-4 w-4" />
                    Open AI dialog
                  </Button>
                  <Button variant="outline" size="icon" onClick={() => setIsLeadDetailsOpen(false)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="grid flex-1 gap-6 overflow-y-auto px-6 py-6 lg:grid-cols-[1.1fr,0.9fr]">
                <div className="space-y-6">
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold">Overview</p>
                      <Button onClick={handleLeadDetailsSave} disabled={isLeadUpdating} className="gap-2">
                        {isLeadUpdating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Edit3 className="h-4 w-4" />}
                        Save changes
                      </Button>
                    </div>
                    <div className="mt-4 grid gap-4 md:grid-cols-2">
                      <div>
                        <Label className="text-xs uppercase text-white/60">Name</Label>
                        <Input
                          value={leadDetailsDraft.name}
                          onChange={(event) => setLeadDetailsDraft({ ...leadDetailsDraft, name: event.target.value })}
                          className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                        />
                      </div>
                      <div>
                        <Label className="text-xs uppercase text-white/60">Company</Label>
                        <Input
                          value={leadDetailsDraft.company}
                          onChange={(event) => setLeadDetailsDraft({ ...leadDetailsDraft, company: event.target.value })}
                          className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                        />
                      </div>
                      <div>
                        <Label className="text-xs uppercase text-white/60">Email</Label>
                        <Input
                          value={leadDetailsDraft.email}
                          onChange={(event) => setLeadDetailsDraft({ ...leadDetailsDraft, email: event.target.value })}
                          className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                        />
                      </div>
                      <div>
                        <Label className="text-xs uppercase text-white/60">Phone</Label>
                        <Input
                          value={leadDetailsDraft.phone}
                          onChange={(event) => setLeadDetailsDraft({ ...leadDetailsDraft, phone: event.target.value })}
                          className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                        />
                      </div>
                      <div>
                        <Label className="text-xs uppercase text-white/60">Status</Label>
                        <select
                          value={leadDetailsDraft.status}
                          onChange={(event) =>
                            setLeadDetailsDraft({ ...leadDetailsDraft, status: event.target.value as LeadStatus })
                          }
                          className="mt-2 w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2"
                        >
                          {leadStatuses.map((status) => (
                            <option key={status.value} value={status.value}>
                              {status.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label className="text-xs uppercase text-white/60">Source</Label>
                        <select
                          value={leadDetailsDraft.source}
                          onChange={(event) =>
                            setLeadDetailsDraft({ ...leadDetailsDraft, source: event.target.value as LeadSource })
                          }
                          className="mt-2 w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2"
                        >
                          {leadSources.map((source) => (
                            <option key={source.value} value={source.value}>
                              {sourceLabels[source.value]}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <Label className="text-xs uppercase text-white/60">Manager notes</Label>
                      <textarea
                        value={leadDetailsDraft.notes}
                        onChange={(event) => setLeadDetailsDraft({ ...leadDetailsDraft, notes: event.target.value })}
                        className="mt-2 min-h-[120px] w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm"
                        placeholder="For example: Interested in CRM integration and Instagram automation deployment."
                      />
                    </div>

                    <div className="mt-4">
                      <Label className="text-xs uppercase text-white/60">Tags</Label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {selectedLead.tags?.map((tag) => (
                          <button
                            key={tag}
                            type="button"
                            onClick={() => handleRemoveTag(tag)}
                            className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70 hover:bg-white/20"
                          >
                            #{tag} ×
                          </button>
                        ))}
                        <div className="flex items-center gap-2 rounded-full border border-dashed border-white/30 px-3 py-1">
                          <input
                            value={newTag}
                            onChange={(event) => setNewTag(event.target.value)}
                            placeholder="Add tag"
                            className="w-24 bg-transparent text-xs text-white placeholder:text-white/50 focus:outline-none"
                          />
                          <button type="button" className="text-xs text-blue-300" onClick={handleAddTag}>
                            Add
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="mt-6 flex flex-wrap gap-3 text-sm">
                      {selectedLead.email && (
                        <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                          <Mail className="h-4 w-4" />
                          {selectedLead.email}
                        </span>
                      )}
                      {selectedLead.phone && (
                        <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                          <Phone className="h-4 w-4" />
                          {selectedLead.phone}
                        </span>
                      )}
                    </div>

                    <div className="mt-6 flex justify-between">
                      <Button variant="secondary" onClick={handleDeleteLead} className="gap-2 text-red-200">
                        <Trash2 className="h-4 w-4" />
                        Delete lead
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold">Timeline</p>
                      <span className="text-xs text-white/50">{leadInteractions.length} records</span>
                    </div>
                    <div className="mt-4 max-h-[360px] space-y-3 overflow-y-auto pr-2">
                      {leadInteractions.length === 0 ? (
                        <p className="text-sm text-white/60">No history yet. Log the first touchpoint.</p>
                      ) : (
                        leadInteractions.map((interaction) => (
                          <div
                            key={interaction.id}
                            className={`rounded-2xl p-4 text-sm ${interactionStyles[interaction.author_type] ?? 'bg-white/10'}`}
                          >
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold uppercase">
                                {interaction.author_name || (interaction.author_type === 'ai' ? 'AI Sales Assistant' : 'Manager')}
                              </span>
                              <span className="text-white/60">{formatDateTime(interaction.created_at)}</span>
                            </div>
                            <p className="mt-2 leading-relaxed">{interaction.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                    <div className="mt-4">
                      <Label className="text-xs uppercase text-white/60">Add note</Label>
                      <textarea
                        value={newInteraction}
                        onChange={(event) => setNewInteraction(event.target.value)}
                        placeholder="Document a call, demo or AI recommendation"
                        className="mt-2 min-h-[100px] w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm"
                      />
                      <Button onClick={handleInteractionSubmit} disabled={isInteractionSaving} className="mt-3 gap-2">
                        {isInteractionSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                        Log interaction
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {leadFormOpen && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-950/80 px-4">
          <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-slate-950 p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-white/60">Create lead</p>
                <h3 className="text-2xl font-semibold">New opportunity</h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setLeadFormOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <form onSubmit={handleLeadSubmit} className="mt-6 space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-xs uppercase text-white/60">Name</Label>
                  <Input
                    value={leadForm.name}
                    onChange={(event) => setLeadForm({ ...leadForm, name: event.target.value })}
                    placeholder="Elena Petrova"
                    className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                  />
                </div>
                <div>
                  <Label className="text-xs uppercase text-white/60">Company</Label>
                  <Input
                    value={leadForm.company}
                    onChange={(event) => setLeadForm({ ...leadForm, company: event.target.value })}
                    placeholder="Digital Studio"
                    className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                  />
                </div>
                <div>
                  <Label className="text-xs uppercase text-white/60">Email</Label>
                  <Input
                    value={leadForm.email}
                    onChange={(event) => setLeadForm({ ...leadForm, email: event.target.value })}
                    placeholder="client@company.com"
                    className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                  />
                </div>
                <div>
                  <Label className="text-xs uppercase text-white/60">Phone</Label>
                  <Input
                    value={leadForm.phone}
                    onChange={(event) => setLeadForm({ ...leadForm, phone: event.target.value })}
                    placeholder="+1 555 123 45 67"
                    className="mt-2 rounded-2xl border-white/20 bg-slate-950/40"
                  />
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-xs uppercase text-white/60">Status</Label>
                  <select
                    value={leadForm.status}
                    onChange={(event) => setLeadForm({ ...leadForm, status: event.target.value as LeadStatus })}
                    className="mt-2 w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2"
                  >
                    {leadStatuses.map((status) => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs uppercase text-white/60">Source</Label>
                  <select
                    value={leadForm.source}
                    onChange={(event) => setLeadForm({ ...leadForm, source: event.target.value as LeadSource })}
                    className="mt-2 w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2"
                  >
                    {leadSources.map((source) => (
                      <option key={source.value} value={source.value}>
                        {source.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <Label className="text-xs uppercase text-white/60">Notes</Label>
                <textarea
                  value={leadForm.notes}
                  onChange={(event) => setLeadForm({ ...leadForm, notes: event.target.value })}
                  placeholder="Context, budget, tasks"
                  className="mt-2 min-h-[120px] w-full rounded-2xl border border-white/20 bg-slate-950/40 px-3 py-2 text-sm"
                />
              </div>
              {leadFormError && <p className="text-sm text-red-300">{leadFormError}</p>}
              <div className="flex justify-end gap-3">
                <Button type="button" variant="outline" onClick={() => setLeadFormOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLeadSaving} className="gap-2">
                  {isLeadSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  Save lead
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
