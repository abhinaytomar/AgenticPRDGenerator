"use client"

import { useState, useCallback } from "react";
import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from "@clerk/nextjs";

import { useWorkflow } from "@/lib/useWorkflow";
import StepIndicator from "@/components/workflow/StepIndicator";
import IntakeStep from "@/components/workflow/IntakeStep";
import ClarifyStep from "@/components/workflow/ClarifyStep";
import GenerationStep from "@/components/workflow/GenerationStep";
import ReviewStep from "@/components/workflow/ReviewStep";
import TicketStep from "@/components/workflow/TicketStep";
import HistoryDrawer from "@/components/HistoryDrawer";

function WorkflowApp() {
  const { getToken } = useAuth();
  const getClerkToken = useCallback(() => getToken(), [getToken]);
  const { state, submitIntake, submitAnswers, generateTickets, approveAndSave, goToStep, reset } = useWorkflow(getClerkToken);
  const [historyOpen, setHistoryOpen] = useState(false);

  return (
    <>
      <nav className="flex items-center justify-between px-6 py-4">
        <Link href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
          &larr; Back
        </Link>
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => setHistoryOpen(true)}
            className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            History
          </button>
          <UserButton />
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-2">
          PRD Generator
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
          Multi-agent AI workflow for comprehensive PRD generation
        </p>

        <StepIndicator currentStep={state.step} />

        <div className="mt-8">
          {state.step === "intake" && (
            <IntakeStep
              onSubmit={submitIntake}
              loading={state.loading}
              error={state.error}
            />
          )}

          {state.step === "clarify" && (
            <ClarifyStep
              questions={state.questions}
              onSubmit={submitAnswers}
              onBack={() => goToStep("intake")}
              loading={state.loading}
              error={state.error}
            />
          )}

          {state.step === "generate" && (
            <GenerationStep
              substep={state.generationSubstep}
              error={state.error}
            />
          )}

          {state.step === "review" && state.generateResult && (
            <ReviewStep
              result={state.generateResult}
              onApprove={() => {
                approveAndSave();
              }}
              onGenerateTickets={generateTickets}
              onReject={reset}
              loading={state.loading}
            />
          )}

          {state.step === "tickets" && state.ticketsResult && (
            <TicketStep
              result={state.ticketsResult}
              onStartOver={reset}
            />
          )}
        </div>
      </div>

      <HistoryDrawer open={historyOpen} onClose={() => setHistoryOpen(false)} />
    </>
  );
}

export default function Product() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-[#09090b]">
      <SignedIn>
        <WorkflowApp />
      </SignedIn>

      <SignedOut>
        <nav className="flex items-center justify-between px-6 py-4">
          <Link href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
            &larr; Back
          </Link>
        </nav>

        <div className="container mx-auto px-4 py-32 max-w-lg text-center">
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-4">
            PRD Generator
          </h1>
          <p className="text-gray-400 mb-8">
            Sign in to start generating professional PRDs with our multi-agent AI workflow.
          </p>
          <SignInButton mode="modal">
            <button className="bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200">
              Sign In to Get Started
            </button>
          </SignInButton>
        </div>
      </SignedOut>
    </main>
  );
}
