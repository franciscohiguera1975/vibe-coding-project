export interface CitationRef {
  sourceDocument: string;
  articleLabel: string;
}

export interface ChecklistItemResult {
  item: string;
  label: string;
  cumple: boolean | null;
  explicacion: string;
  citas: CitationRef[];
}

export interface RagEvaluationResultItem {
  id: string;
  question: string;
  expectedCitation: CitationRef;
  baselineAnswer: string;
  ragAnswer: string;
  ragCitationMatch: boolean;
  baselineCitationMatch: boolean;
}

export interface RagEvaluationSummary {
  total: number;
  ragCitationMatches: number;
  baselineCitationMatches: number;
}

export interface RagEvaluationRun {
  id: string;
  results: RagEvaluationResultItem[];
  summary: RagEvaluationSummary;
}
