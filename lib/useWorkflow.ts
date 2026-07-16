/** useReducer-based state machine for the 5-step workflow. */

import { useReducer, useCallback } from "react";
import type {
  WorkflowState,
  WorkflowStep,
  IntakeData,
  ClarifyingQuestion,
  QuestionAnswer,
  GenerateResponse,
  TicketsResponse,
  GenerationSubstep,
} from "./types";
import { callIntake, callGenerate, callTickets, ApiError } from "./api";
import { addToHistory, generateId } from "./history";

const initialState: WorkflowState = {
  step: "intake",
  intake: null,
  questions: [],
  answers: [],
  generateResult: null,
  ticketsResult: null,
  generationSubstep: "researching",
  loading: false,
  error: null,
};

type Action =
  | { type: "SET_STEP"; step: WorkflowStep }
  | { type: "SET_LOADING"; loading: boolean }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "SET_INTAKE"; intake: IntakeData }
  | { type: "SET_QUESTIONS"; questions: ClarifyingQuestion[] }
  | { type: "SET_ANSWERS"; answers: QuestionAnswer[] }
  | { type: "SET_GENERATION_SUBSTEP"; substep: GenerationSubstep }
  | { type: "SET_GENERATE_RESULT"; result: GenerateResponse }
  | { type: "SET_TICKETS_RESULT"; result: TicketsResponse }
  | { type: "RESET" };

function reducer(state: WorkflowState, action: Action): WorkflowState {
  switch (action.type) {
    case "SET_STEP":
      return { ...state, step: action.step, error: null };
    case "SET_LOADING":
      return { ...state, loading: action.loading };
    case "SET_ERROR":
      return { ...state, error: action.error, loading: false };
    case "SET_INTAKE":
      return { ...state, intake: action.intake };
    case "SET_QUESTIONS":
      return { ...state, questions: action.questions };
    case "SET_ANSWERS":
      return { ...state, answers: action.answers };
    case "SET_GENERATION_SUBSTEP":
      return { ...state, generationSubstep: action.substep };
    case "SET_GENERATE_RESULT":
      return { ...state, generateResult: action.result };
    case "SET_TICKETS_RESULT":
      return { ...state, ticketsResult: action.result };
    case "RESET":
      return { ...initialState };
    default:
      return state;
  }
}

/** A function that returns a JWT token string, e.g. from Clerk's useAuth().getToken() */
type GetTokenFn = () => Promise<string | null>;

export function useWorkflow(getToken: GetTokenFn) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const submitIntake = useCallback(async (intake: IntakeData) => {
    dispatch({ type: "SET_INTAKE", intake });
    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: null });

    try {
      const token = await getToken();
      const result = await callIntake(intake, token);
      dispatch({ type: "SET_QUESTIONS", questions: result.questions });
      dispatch({ type: "SET_STEP", step: "clarify" });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to generate questions. Please try again.";
      dispatch({ type: "SET_ERROR", error: message });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  }, [getToken]);

  const submitAnswers = useCallback(
    async (answers: QuestionAnswer[]) => {
      if (!state.intake) return;

      dispatch({ type: "SET_ANSWERS", answers });
      dispatch({ type: "SET_LOADING", loading: true });
      dispatch({ type: "SET_ERROR", error: null });
      dispatch({ type: "SET_STEP", step: "generate" });
      dispatch({ type: "SET_GENERATION_SUBSTEP", substep: "researching" });

      // Simulate substep progression while the single request runs
      const substepTimers = [
        setTimeout(() => dispatch({ type: "SET_GENERATION_SUBSTEP", substep: "writing" }), 3000),
        setTimeout(() => dispatch({ type: "SET_GENERATION_SUBSTEP", substep: "evaluating" }), 8000),
        setTimeout(() => dispatch({ type: "SET_GENERATION_SUBSTEP", substep: "revising" }), 13000),
      ];

      try {
        const token = await getToken();
        const result = await callGenerate({ intake: state.intake, answers }, token);
        substepTimers.forEach(clearTimeout);
        dispatch({ type: "SET_GENERATION_SUBSTEP", substep: "done" });
        dispatch({ type: "SET_GENERATE_RESULT", result });
        dispatch({ type: "SET_STEP", step: "review" });
      } catch (err) {
        substepTimers.forEach(clearTimeout);
        const message = err instanceof ApiError ? err.message : "Failed to generate PRD. Please try again.";
        dispatch({ type: "SET_ERROR", error: message });
        dispatch({ type: "SET_STEP", step: "clarify" });
      } finally {
        dispatch({ type: "SET_LOADING", loading: false });
      }
    },
    [state.intake, getToken],
  );

  const generateTickets = useCallback(async () => {
    if (!state.generateResult) return;

    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: null });

    try {
      const token = await getToken();
      const result = await callTickets(state.generateResult.prd, token);
      dispatch({ type: "SET_TICKETS_RESULT", result });
      dispatch({ type: "SET_STEP", step: "tickets" });

      // Save to history
      if (state.intake) {
        addToHistory({
          id: generateId(),
          intake: state.intake,
          answers: state.answers,
          prd: state.generateResult.prd,
          prd_markdown: state.generateResult.prd_markdown,
          evaluation: state.generateResult.evaluation,
          tickets: result,
          timestamp: Date.now(),
        });
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to generate tickets. Please try again.";
      dispatch({ type: "SET_ERROR", error: message });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  }, [state.generateResult, state.intake, state.answers, getToken]);

  const approveAndSave = useCallback(() => {
    if (!state.generateResult || !state.intake) return;

    addToHistory({
      id: generateId(),
      intake: state.intake,
      answers: state.answers,
      prd: state.generateResult.prd,
      prd_markdown: state.generateResult.prd_markdown,
      evaluation: state.generateResult.evaluation,
      tickets: null,
      timestamp: Date.now(),
    });
  }, [state.generateResult, state.intake, state.answers]);

  const goToStep = useCallback((step: WorkflowStep) => {
    dispatch({ type: "SET_STEP", step });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: "RESET" });
  }, []);

  return {
    state,
    submitIntake,
    submitAnswers,
    generateTickets,
    approveAndSave,
    goToStep,
    reset,
  };
}
