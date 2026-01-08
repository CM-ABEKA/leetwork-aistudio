import Link from 'next/link';
import { Brain, Sparkles, Zap, Shield } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-8 w-8 text-purple-400" />
              <span className="text-xl font-bold text-white">AI Model Studio</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-gray-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Get Started
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-8">
            <Sparkles className="h-4 w-4 text-purple-400" />
            <span className="text-sm text-purple-300">No Code Required</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Build AI Models
            <br />
            <span className="bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
              Without Writing Code
            </span>
          </h1>

          <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Transform raw data into production-ready AI models through an intuitive interface.
            Upload, clean, train, and deploy models across 13 AI domains.
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link
              href="/register"
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Start Building Free
            </Link>
            <Link
              href="/docs"
              className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors border border-white/20"
            >
              View Documentation
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mt-20">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="bg-purple-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Fast Setup</h3>
              <p className="text-gray-400 text-sm">
                Train your first model in under 15 minutes with our guided workflow.
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="bg-purple-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">13 AI Domains</h3>
              <p className="text-gray-400 text-sm">
                ML, NLP, Computer Vision, Audio, Time Series, and more specialized domains.
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="bg-purple-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Enterprise Ready</h3>
              <p className="text-gray-400 text-sm">
                Built-in security, audit trails, and compliance features for production use.
              </p>
            </div>
          </div>

          {/* Status */}
          <div className="mt-16 p-6 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
            <p className="text-yellow-300 font-medium">
              Currently in Development - Phase 0 (Foundation)
            </p>
            <p className="text-yellow-300/70 text-sm mt-1">
              MVP launching in Q2 2026 with Classical ML and NLP domains
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-400 text-sm">
            <p>© 2026 AI Model Studio. Built to democratize AI for everyone.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
