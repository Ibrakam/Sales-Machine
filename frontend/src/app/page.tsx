import Link from 'next/link'
import { Target, ArrowRight, Sparkles, Users, MessageCircle, Instagram } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col items-center justify-center p-4">
      <div className="text-center relative z-10 max-w-6xl mx-auto">
        <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl mb-8 shadow-2xl">
          <Target className="w-12 h-12 text-white" />
        </div>
        
        <h1 className="text-6xl font-bold text-white mb-6 leading-tight">
          AI Sales Assistant
        </h1>
        
        <p className="text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
          Platform for selling IT services: CRM for leads, AI assistant in admin panel and automatic import of requests from Instagram.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link 
            href="/auth/login" 
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl text-lg"
          >
            Sign In
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <Link
            href="/docs"
            className="inline-flex items-center px-8 py-4 bg-white/10 backdrop-blur-xl text-white font-semibold rounded-2xl border border-white/30 hover:bg-white/20 transition-all duration-200 text-lg"
          >
            Documentation
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-200">
            <Users className="w-12 h-12 text-blue-400 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-white mb-4">Lead Management Center</h3>
            <p className="text-gray-300">
              Statuses "New / In Progress / Completed", notes and conversation history in one card — everything for B2B IT tasks.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-200">
            <MessageCircle className="w-12 h-12 text-purple-400 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-white mb-4">AI Manager Chat</h3>
            <p className="text-gray-300">
              Built-in assistant suggests answers, prepares deal plans and helps create commercial proposals.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-200">
            <Instagram className="w-12 h-12 text-pink-400 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-white mb-4">Instagram Integration</h3>
            <p className="text-gray-300">
              Import requests from Direct: contact, "instagram" tag and client request are added automatically.
            </p>
          </div>
        </div>
        
        <div className="mt-16 p-6 bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 max-w-md mx-auto">
          <div className="flex items-center justify-center mb-3">
            <Sparkles className="h-5 w-5 text-yellow-400 mr-2" />
            <p className="text-sm text-gray-300">Demo Access</p>
          </div>
          <p className="text-white font-medium">admin@example.com / password</p>
        </div>
      </div>
    </div>
  )
}
