import Mathlib
abbrev S01_solution : ℚ × ℚ := sorry
/--
Two real numbers $x$ and $y$ are chosen at random in the interval $(0,1)$ with respect to the uniform distribution. What is the probability that the closest integer to $x/y$ is even? Express the answer in the form $r+s\pi$, where $r$ and $s$ are rational numbers.
-/
theorem S01 :
  let (r, s) := S01_solution;
  (MeasureTheory.volume
    {p : Fin 2 → ℝ | 0 < p ∧ p < 1 ∧ Even (round (p 0 / p 1))}
  ).toReal
  = r + s * Real.pi :=
sorry
