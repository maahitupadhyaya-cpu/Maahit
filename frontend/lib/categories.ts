import { CategoryId, CategoryMeta } from "./types";

export const CATEGORIES: CategoryMeta[] = [
  {
    id: "calculus",
    label: "Calculus",
    shortLabel: "Calculus",
    blurb: "Derivatives, integrals & limits",
    placeholder: "e.g. Differentiate x^3 + 2x^2 - 5x + 7",
    icon: "∫",
  },
  {
    id: "differential_equations",
    label: "Differential Equations",
    shortLabel: "Diff. Eq.",
    blurb: "ODEs with or without initial conditions",
    placeholder: "e.g. Solve y'' - 3*y' + 2*y = 0",
    icon: "y′",
  },
  {
    id: "linear_algebra",
    label: "Linear Algebra",
    shortLabel: "Lin. Alg.",
    blurb: "Matrices, eigenvalues, systems",
    placeholder: "e.g. Find the eigenvalues of [[2,1],[1,2]]",
    icon: "⊞",
  },
  {
    id: "optimization",
    label: "Optimization",
    shortLabel: "Optim.",
    blurb: "Extrema, constrained & unconstrained",
    placeholder: "e.g. Minimize f(x,y) = x^2 + y^2 - 4x - 6y + 20",
    icon: "min",
  },
  {
    id: "statistics",
    label: "Statistics",
    shortLabel: "Stats",
    blurb: "Mean, variance, distributions",
    placeholder: "e.g. Find the mean and variance of [2,4,4,4,5,5,7,9]",
    icon: "x̄",
  },
  {
    id: "probability",
    label: "Probability",
    shortLabel: "Prob.",
    blurb: "Binomial & normal distributions",
    placeholder: "e.g. Probability of exactly 3 heads in 10 coin flips with p=0.5",
    icon: "P",
  },
];

export const EXAMPLES: Record<string, string[]> = {
  calculus: [
    "Differentiate x^3 + 2x^2 - 5x + 7",
    "Find the integral of x^2 * sin(x) dx",
    "Integrate 3x^2 + 2x from 0 to 4",
    "Find the limit of (sin(x))/x as x -> 0",
  ],
  differential_equations: [
    "Solve y'' - 3*y' + 2*y = 0",
    "Solve dy/dx = y - x, y(0) = 1",
    "Solve y' + 2*y = sin(x)",
  ],
  linear_algebra: [
    "Find the eigenvalues of [[2,1],[1,2]]",
    "Find the determinant of [[1,2,3],[0,1,4],[5,6,0]]",
    "Find the inverse of [[2,1],[1,1]]",
    "Solve [[2,1],[1,3]] x = [3,5]",
  ],
  optimization: [
    "Minimize f(x,y) = x^2 + y^2 - 4x - 6y + 20",
    "Minimize f(x) = x^2 - 4x + 5",
    "Maximize f(x,y) = x*y subject to x + y = 10",
  ],
  statistics: [
    "Find the mean and variance of [2,4,4,4,5,5,7,9]",
    "Describe the dataset [12, 15, 12, 18, 20, 22, 15, 14]",
  ],
  probability: [
    "Probability of exactly 3 heads in 10 coin flips with p=0.5",
    "Probability of at least 4 successes in 8 trials with p=0.3",
    "Normal distribution with mean 0 and std 1, probability between -1 and 1",
  ],
};

export function isCategoryId(value: string | null | undefined): value is CategoryId {
  return !!value && CATEGORIES.some((c) => c.id === value);
}

export function solveHref(category?: CategoryId): string {
  return category ? `/solve?category=${category}` : "/solve";
}

export function defaultProblem(category: CategoryId): string {
  return EXAMPLES[category]?.[0] ?? "";
}
