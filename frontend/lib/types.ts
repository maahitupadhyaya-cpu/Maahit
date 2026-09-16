export type CategoryId =
  | "calculus"
  | "differential_equations"
  | "linear_algebra"
  | "optimization"
  | "statistics"
  | "probability";

export interface CategoryMeta {
  id: CategoryId;
  label: string;
  shortLabel: string;
  blurb: string;
  placeholder: string;
  icon: string;
}

export interface Step {
  title: string;
  description: string;
  latex: string | null;
}

export interface PlotSpec {
  data: any[];
  layout: Record<string, any>;
  caption?: string | null;
}

export interface SolveResponse {
  category: string;
  subtype: string;
  input_echo: string;
  summary: string;
  steps: Step[];
  latex: string;
  plot: PlotSpec | null;
  warnings: string[];
}

export interface ApiError {
  detail: string;
}
