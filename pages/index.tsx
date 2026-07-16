"use client"

import Link from 'next/link';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#09090b]">
      {/* Top accent line */}
      <div className="accent-line" />

      {/* Navigation */}
      <nav className="flex justify-between items-center px-6 py-5 border-b border-white/10 max-w-6xl mx-auto">
        <span className="text-lg font-bold text-white">PRD Generator</span>
        <div className="flex items-center gap-4">
          <SignedIn>
            <Link
              href="/product"
              className="bg-white text-black font-medium py-2 px-5 rounded-lg transition-colors hover:bg-gray-200"
            >
              Go to App
            </Link>
            <UserButton />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <button className="text-gray-400 hover:text-white font-medium py-2 px-5 transition-colors">
                Sign In
              </button>
            </SignInButton>
            <Link
              href="/product"
              className="bg-white text-black font-medium py-2 px-5 rounded-lg transition-colors hover:bg-gray-200"
            >
              Get Started
            </Link>
          </SignedOut>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-6 pt-32 pb-24">
        <h1 className="text-7xl md:text-8xl font-bold tracking-tight text-white leading-[0.95]">
          Agentic PRD
          <br />
          Generation
          <br />
          in Minutes.
        </h1>
        <p className="text-lg text-gray-400 max-w-xl mt-8 leading-relaxed">
          Multi-agent AI workflow that transforms product ideas into comprehensive PRDs with structured requirements, quality evaluation, and Jira-ready tickets.
        </p>
        <div className="flex gap-4 mt-10">
          <Link
            href="/product"
            className="bg-violet-600 hover:bg-violet-500 text-white font-medium py-3 px-7 rounded-lg transition-colors"
          >
            Get Started
          </Link>
          <Link href="/faq" className="text-gray-400 border border-gray-700 hover:border-gray-500 font-medium py-3 px-7 rounded-lg transition-colors">
            Ask the PM FAQ
          </Link>
          <a href="#how-it-works" className="text-gray-400 border border-gray-700 hover:border-gray-500 font-medium py-3 px-7 rounded-lg transition-colors">
            Learn More
          </a>
        </div>
      </section>

      {/* Features — Full-width bands */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <p className="text-xs uppercase tracking-[0.2em] text-gray-500 mb-12">Agent Capabilities</p>

        <div className="border-t border-white/10">
          <div className="flex gap-8 py-8">
            <span className="text-violet-500 font-mono text-sm pt-1">01</span>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Intake Agent</h3>
              <p className="text-gray-400 text-sm max-w-lg">
                Analyzes your product idea and generates targeted clarifying questions to uncover missing context, ambiguities, and assumptions before drafting.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10">
          <div className="flex gap-8 py-8">
            <span className="text-violet-500 font-mono text-sm pt-1">02</span>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Research &amp; Writer Agents</h3>
              <p className="text-gray-400 text-sm max-w-lg">
                Research agent synthesizes market context and technical considerations. Writer agent produces a 15-section structured PRD with functional requirements, user flows, and acceptance criteria.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10">
          <div className="flex gap-8 py-8">
            <span className="text-violet-500 font-mono text-sm pt-1">03</span>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Critic &amp; Revision Agents</h3>
              <p className="text-gray-400 text-sm max-w-lg">
                Critic agent evaluates completeness, clarity, and actionability with a quality score. If below threshold, the revision agent automatically improves the PRD.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10">
          <div className="flex gap-8 py-8">
            <span className="text-violet-500 font-mono text-sm pt-1">04</span>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Ticket Generator</h3>
              <p className="text-gray-400 text-sm max-w-lg">
                Converts approved PRDs into Jira-ready epics and user stories with Given/When/Then acceptance criteria and story point estimates.
              </p>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10">
          <div className="flex gap-8 py-8">
            <span className="text-violet-500 font-mono text-sm pt-1">05</span>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">PM FAQ Assistant (Agentic RAG)</h3>
              <p className="text-gray-400 text-sm max-w-lg">
                Ask questions about PRDs and product management. Retrieves from a curated PM
                knowledge base (RAG over a vector database) and runs a live web search when
                needed — every answer is grounded and cited.
              </p>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10" />
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="max-w-6xl mx-auto px-6 py-24">
        <p className="text-xs uppercase tracking-[0.2em] text-gray-500 mb-16">How It Works</p>

        <div className="grid md:grid-cols-5 gap-8 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-10 left-[10%] right-[10%] h-px bg-white/10" />

          <div>
            <span className="text-4xl font-mono text-violet-500/20 block mb-4">01</span>
            <h4 className="text-lg font-semibold text-white mb-2">Describe</h4>
            <p className="text-sm text-gray-400">
              Enter your product name, problem statement, and context.
            </p>
          </div>
          <div>
            <span className="text-4xl font-mono text-violet-500/20 block mb-4">02</span>
            <h4 className="text-lg font-semibold text-white mb-2">Clarify</h4>
            <p className="text-sm text-gray-400">
              Answer AI-generated questions to fill context gaps.
            </p>
          </div>
          <div>
            <span className="text-4xl font-mono text-violet-500/20 block mb-4">03</span>
            <h4 className="text-lg font-semibold text-white mb-2">Generate</h4>
            <p className="text-sm text-gray-400">
              Watch agents research, write, evaluate, and revise.
            </p>
          </div>
          <div>
            <span className="text-4xl font-mono text-violet-500/20 block mb-4">04</span>
            <h4 className="text-lg font-semibold text-white mb-2">Review</h4>
            <p className="text-sm text-gray-400">
              See quality scores, issues, and the full PRD.
            </p>
          </div>
          <div>
            <span className="text-4xl font-mono text-violet-500/20 block mb-4">05</span>
            <h4 className="text-lg font-semibold text-white mb-2">Tickets</h4>
            <p className="text-sm text-gray-400">
              Get Jira-ready epics and stories instantly.
            </p>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="border-t border-white/10 py-24">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-8">
            Ready to build better products?
          </h2>
          <Link
            href="/product"
            className="inline-block bg-violet-600 hover:bg-violet-500 text-white font-medium py-3 px-8 rounded-lg transition-colors"
          >
            Get Started
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-6 pb-8">
        <p className="text-center text-sm text-gray-600">Agentic AI PRD Generator — For demonstration purposes only</p>
      </footer>
    </main>
  );
}
