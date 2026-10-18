import Mathlib
set_option linter.unusedVariables false

/-! # Exp 4: Lean certificates for NEW defects found in the PutnamBench HEAD audit (a635813). -/
namespace E4
open Filter Topology Set

/-! ## putnam_2023_a6: the statement is provable without any game theory.
We prove the benchmark statement verbatim (hypotheses copied), with the answer `{n | 0 < n}`
(the commented solution) substituted for the `sorry` placeholder. The proof only uses the
bug: a "valid" strategy must return an already-chosen number, so no valid game of length ≥ 2
can conform to it. -/
theorem A6_trivial
    (IsValidGame : List ℕ → Prop)
    (IsValidGame_def : ∀ g, IsValidGame g ↔ g.Nodup ∧ (∀ i ∈ g, i ∈ Finset.Icc 1 g.length))
    (parityOf : List ℕ → ZMod 2)
    (parityOf_def : ∀ g, parityOf g =
      ((Finset.range g.length).filter fun i ↦ g[i]! = i + 1).card)
    (ConformsToStrategy : List ℕ → (List ℕ → ℕ) → Prop)
    (ConformsToStrategy_def : ∀ g s, ConformsToStrategy g s ↔
      ∀ (i) (h : i < g.length), Odd i → g[i] = s (g.take i))
    (IsValidStrategy : (List ℕ → ℕ) → Prop)
    (IsValidStrategy_def : ∀ s, IsValidStrategy s ↔
      ∀ (g : List ℕ), g.length > 0 → s g ∈ g)
    (IsWinningFor : ℕ → (List ℕ → ℕ) → Prop)
    (IsWinningFor_def : ∀ n s, IsWinningFor n s ↔
      IsValidStrategy s ∧ ∃ p, ∀ g, g.length = n → IsValidGame g → ConformsToStrategy g s →
        parityOf g = p) :
    {n : ℕ | 0 < n ∧ ∃ s, IsWinningFor n s} = {n : ℕ | 0 < n} := by
  ext n
  simp only [Set.mem_setOf_eq]
  refine ⟨fun h => h.1, fun hn => ⟨hn, fun g => g.headD 0, (IsWinningFor_def _ _).2 ⟨?_, ?_⟩⟩⟩
  · rw [IsValidStrategy_def]
    intro g hg
    cases g with
    | nil => simp at hg
    | cons a t => simp
  · by_cases h1 : n = 1
    · subst h1
      refine ⟨1, fun g hlen hv _ => ?_⟩
      obtain ⟨-, hmem⟩ := (IsValidGame_def g).1 hv
      match g, hlen, hmem with
      | [a], _, hmem =>
        have ha : a ∈ Finset.Icc 1 1 := hmem a (by simp)
        have : a = 1 := by simpa using ha
        subst this
        rw [parityOf_def]
        decide
    · refine ⟨0, fun g hlen hv hc => ?_⟩
      exfalso
      obtain ⟨hnd, -⟩ := (IsValidGame_def g).1 hv
      have h1lt : 1 < g.length := by omega
      have hstep := ((ConformsToStrategy_def g _).1 hc) 1 h1lt (by decide)
      match g, h1lt, hnd, hstep with
      | a :: b :: t, _, hnd, hstep =>
        simp at hstep
        simp_all

/-! ## putnam_1982_b5: precedence drops the convergence claim.
`B82` is the benchmark's conclusion with `S` and `g` abstracted (same text, so same parse). -/
def B82 (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ) : Prop :=
  ∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
    (∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T
/-- The intended reading ("prove S_x converges, and that g is continuous"). -/
def I82 (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ) : Prop :=
  (∀ x ∈ T, ∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
    ((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T)

/-- How Lean actually parses the benchmark conclusion. -/
theorem B82_parse (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ) :
    B82 T S g ↔ ∀ x ∈ T, ((∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
      (∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x)))) → ContinuousOn g T := Iff.rfl

/-- Intended ⇒ benchmark, but not conversely: with a divergent S the benchmark form is
vacuously true while the intended statement is false. -/
theorem I82_imp_B82 (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ) : I82 T S g → B82 T S g :=
  fun ⟨_, h⟩ _ _ hx => h hx.2

theorem B82_weaker : ∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), B82 T S g ∧ ¬ I82 T S g := by
  have hdiv : ¬ ∃ L : ℝ, Tendsto (fun n : ℕ => (n : ℝ)) atTop (𝓝 L) := by
    rintro ⟨L, hL⟩
    exact not_tendsto_atTop_of_tendsto_nhds hL tendsto_natCast_atTop_atTop
  refine ⟨univ, fun _ n => n, fun x => if x < 0 then 0 else 1, ?_, ?_⟩
  · rintro x - ⟨h, -⟩
    exact absurd h hdiv
  · rintro ⟨h, -⟩
    exact hdiv (h 0 trivial)

/-! ## putnam_2021_b4: the docstring states a false problem (Lean statement is fine).
Docstring: R_m = (∏_{k=1}^{F_{m-1}} k^k) mod F_m is a Fibonacci number. False at m = 7. -/
theorem docstring_2021_b4_false :
    ¬ ∀ m : ℕ, m > 2 → ∃ p, (∏ k ∈ Finset.Icc 1 (Nat.fib (m - 1)), k ^ k) % Nat.fib m = Nat.fib p := by
  intro h
  obtain ⟨p, hp⟩ := h 7 (by norm_num)
  have h6 : Nat.fib 6 = 8 := by decide
  have h7 : Nat.fib 7 = 13 := by decide
  have hprod : (∏ k ∈ Finset.Icc 1 8, k ^ k) % 13 = 12 := by decide
  rw [show (7 : ℕ) - 1 = 6 from rfl, h6, h7, hprod] at hp
  rcases Nat.lt_or_ge p 7 with hlt | hge
  · interval_cases p <;> revert hp <;> decide
  · have := Nat.fib_mono hge
    rw [h7] at this
    omega

/-- And the Lean statement's version (bound F_m − 1) holds at m = 7: 8 = F_6. -/
example : (∏ k ∈ Finset.Icc 1 (Nat.fib 7 - 1), k ^ k) % Nat.fib 7 = Nat.fib 6 := by decide

/-! ## putnam_2004_a4: quantifier scope. Schema: replace ∏ x i by an arbitrary F.
`B04` = benchmark shape (x fixed first), `I04` = intended ("identically"). n = 1, F x = |x 0|. -/
def B04 (F : (Fin 1 → ℝ) → ℝ) : Prop := ∀ x : Fin 1 → ℝ,
  ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin 1 → ℝ),
    (∀ (i : Fin N) (j : Fin 1), a i j = -1 ∨ a i j = 0 ∨ a i j = 1) ∧
    F x = ∑ i : Fin N, c i * (∑ j : Fin 1, a i j * x j) ^ 1
def I04 (F : (Fin 1 → ℝ) → ℝ) : Prop :=
  ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin 1 → ℝ),
    (∀ (i : Fin N) (j : Fin 1), a i j = -1 ∨ a i j = 0 ∨ a i j = 1) ∧
    ∀ x : Fin 1 → ℝ, F x = ∑ i : Fin N, c i * (∑ j : Fin 1, a i j * x j) ^ 1

theorem scope_2004_a4 : B04 (fun x => |x 0|) ∧ ¬ I04 (fun x => |x 0|) := by
  constructor
  · intro x
    by_cases hx : 0 ≤ x 0
    · refine ⟨1, fun _ => 1, fun _ _ => 1, fun _ _ => Or.inr (Or.inr rfl), ?_⟩
      simp [abs_of_nonneg hx]
    · refine ⟨1, fun _ => -1, fun _ _ => 1, fun _ _ => Or.inr (Or.inr rfl), ?_⟩
      simp [abs_of_neg (not_le.mp hx)]
  · rintro ⟨N, c, a, -, hall⟩
    have key : ∀ x : Fin 1 → ℝ, (∑ i : Fin N, (c i : ℝ) * (∑ j : Fin 1, a i j * x j) ^ 1) =
        (∑ i : Fin N, (c i : ℝ) * a i 0) * x 0 := by
      intro x
      rw [Finset.sum_mul]
      apply Finset.sum_congr rfl
      intro i _
      simp only [Fin.sum_univ_one, pow_one]
      ring
    have h1 := hall (fun _ => 1)
    have h2 := hall (fun _ => -1)
    rw [key] at h1 h2
    norm_num at h1 h2
    linarith

end E4
