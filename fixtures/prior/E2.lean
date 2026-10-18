import Mathlib
set_option linter.unusedVariables false

/-! # Exp 2: machine-checked evidence on real (since-fixed) PutnamBench statement bugs.
Each bug is paired with the fixed version as a control where feasible. -/
namespace E2
open Filter Topology

/-! ## R20 = putnam_1980_a4, pre-fix (commit 25bc648^): "not all zero" was written "all zero".
Certificate: the benchmark statement is FALSE (part (b) fails at a = b = c = 0). -/
def R20_U : Prop := ∀ (abcvals : ℤ → ℤ → ℤ → Prop)
    (habcvals : ∀ a b c : ℤ, abcvals a b c ↔ (a = 0 ∧ b = 0 ∧ c = 0) ∧ |a| < 1000000 ∧
      |b| < 1000000 ∧ |c| < 1000000),
    (∃ a b c : ℤ,
      abcvals a b c ∧
      |a + b * Real.sqrt 2 + c * Real.sqrt 3| < 10 ^ (-(11 : ℝ))) ∧
      (∀ a b c : ℤ, abcvals a b c → |a + b * Real.sqrt 2 + c * Real.sqrt 3| > 10 ^ (-(21 : ℝ)))

theorem R20_U_false : ¬ R20_U := by
  intro h
  have := (h (fun a b c => (a = 0 ∧ b = 0 ∧ c = 0) ∧ |a| < 1000000 ∧ |b| < 1000000 ∧
    |c| < 1000000) (fun _ _ _ => Iff.rfl)).2 0 0 0
    ⟨⟨rfl, rfl, rfl⟩, by norm_num, by norm_num, by norm_num⟩
  simp only [Int.cast_zero, zero_mul, add_zero, abs_zero, gt_iff_lt] at this
  linarith [Real.rpow_pos_of_pos (by norm_num : (0 : ℝ) < 10) (-(21 : ℝ))]

/-- Control: the FIXED statement is equivalent to GPT's independent formalization, for every
real-valued expression E (schema over the quantity being bounded). -/
def R20s_F (E : ℤ → ℤ → ℤ → ℝ) : Prop := ∀ (abcvals : ℤ → ℤ → ℤ → Prop)
    (habcvals : ∀ a b c : ℤ, abcvals a b c ↔ ¬(a = 0 ∧ b = 0 ∧ c = 0) ∧ |a| < 1000000 ∧
      |b| < 1000000 ∧ |c| < 1000000),
    (∃ a b c : ℤ, abcvals a b c ∧ E a b c < 10 ^ (-(11 : ℝ))) ∧
      (∀ a b c : ℤ, abcvals a b c → E a b c > 10 ^ (-(21 : ℝ)))
def R20s_G (E : ℤ → ℤ → ℤ → ℝ) : Prop :=
  (∃ a b c : ℤ,
    (a ≠ 0 ∨ b ≠ 0 ∨ c ≠ 0) ∧
    |a| < (1000000 : ℤ) ∧
    |b| < (1000000 : ℤ) ∧
    |c| < (1000000 : ℤ) ∧
    E a b c < (1 : ℝ) / 10 ^ 11) ∧
  (∀ a b c : ℤ,
    (a ≠ 0 ∨ b ≠ 0 ∨ c ≠ 0) →
    |a| < (1000000 : ℤ) →
    |b| < (1000000 : ℤ) →
    |c| < (1000000 : ℤ) →
    (1 : ℝ) / 10 ^ 21 < E a b c)

example : (∀ (abcvals : ℤ → ℤ → ℤ → Prop)
    (habcvals : ∀ a b c : ℤ, abcvals a b c ↔ ¬(a = 0 ∧ b = 0 ∧ c = 0) ∧ |a| < 1000000 ∧
      |b| < 1000000 ∧ |c| < 1000000),
    (∃ a b c : ℤ, abcvals a b c ∧ |a + b * Real.sqrt 2 + c * Real.sqrt 3| < 10 ^ (-(11 : ℝ))) ∧
      (∀ a b c : ℤ, abcvals a b c → |a + b * Real.sqrt 2 + c * Real.sqrt 3| > 10 ^ (-(21 : ℝ))))
    ↔ R20s_F (fun a b c => |a + b * Real.sqrt 2 + c * Real.sqrt 3|) := Iff.rfl
example : ((∃ a b c : ℤ,
    (a ≠ 0 ∨ b ≠ 0 ∨ c ≠ 0) ∧ |a| < (1000000 : ℤ) ∧ |b| < (1000000 : ℤ) ∧ |c| < (1000000 : ℤ) ∧
    |(a : ℝ) + (b : ℝ) * Real.sqrt 2 + (c : ℝ) * Real.sqrt 3| < (1 : ℝ) / 10 ^ 11) ∧
  (∀ a b c : ℤ, (a ≠ 0 ∨ b ≠ 0 ∨ c ≠ 0) → |a| < (1000000 : ℤ) → |b| < (1000000 : ℤ) →
    |c| < (1000000 : ℤ) →
    (1 : ℝ) / 10 ^ 21 < |(a : ℝ) + (b : ℝ) * Real.sqrt 2 + (c : ℝ) * Real.sqrt 3|))
    ↔ R20s_G (fun a b c => |(a : ℝ) + (b : ℝ) * Real.sqrt 2 + (c : ℝ) * Real.sqrt 3|) := Iff.rfl

theorem rp (n : ℕ) : (10 : ℝ) ^ (-(n : ℝ)) = 1 / 10 ^ n := by
  rw [Real.rpow_neg (by norm_num), Real.rpow_natCast, one_div]

theorem R20s_FG (E : ℤ → ℤ → ℤ → ℝ) : R20s_F E ↔ R20s_G E := by
  have k11 : (10 : ℝ) ^ (-(11 : ℝ)) = 1 / 10 ^ 11 := by have := rp 11; push_cast at this; exact this
  have k21 : (10 : ℝ) ^ (-(21 : ℝ)) = 1 / 10 ^ 21 := by have := rp 21; push_cast at this; exact this
  unfold R20s_F R20s_G
  constructor
  · intro h
    obtain ⟨⟨a, b, c, hv, hE⟩, h2⟩ := h (fun a b c => ¬(a = 0 ∧ b = 0 ∧ c = 0) ∧ |a| < 1000000 ∧
      |b| < 1000000 ∧ |c| < 1000000) (fun _ _ _ => Iff.rfl)
    refine ⟨⟨a, b, c, by omega, hv.2.1, hv.2.2.1, hv.2.2.2, by rw [← k11]; exact hE⟩,
      fun a b c hn ha hb hc => ?_⟩
    have := h2 a b c ⟨by omega, ha, hb, hc⟩
    rw [k21] at this
    exact this
  · rintro ⟨⟨a, b, c, hn, ha, hb, hc, hE⟩, h2⟩ abcvals habc
    refine ⟨⟨a, b, c, (habc a b c).2 ⟨by omega, ha, hb, hc⟩, by rw [k11]; exact hE⟩,
      fun a b c hv => ?_⟩
    obtain ⟨h0, ha, hb, hc⟩ := (habc a b c).1 hv
    rw [k21]
    exact h2 a b c (by omega) ha hb hc

/-! ## R19 = putnam_1977_a2, pre-fix: the solution predicate was declared equal to
"nonzero → equations", so every tuple containing a zero counts as a solution.
Answer-parametric certificate: NO answer satisfies both the benchmark spec and GPT's spec. -/
def R19_U (sol : ℝ → ℝ → ℝ → ℝ → Prop) : Prop :=
  ∀ a b c d : ℝ, sol a b c d ↔
    a ≠ 0 → b ≠ 0 → c ≠ 0 → d ≠ 0 → (a + b + c = d ∧ 1 / a + 1 / b + 1 / c = 1 / d)
def R19_F (sol : ℝ → ℝ → ℝ → ℝ → Prop) : Prop :=
  ∀ a b c d : ℝ, a ≠ 0 → b ≠ 0 → c ≠ 0 → d ≠ 0 →
    (sol a b c d ↔ (a + b + c = d ∧ 1 / a + 1 / b + 1 / c = 1 / d))
def R19_G (ans : Set (ℝ × ℝ × ℝ × ℝ)) : Prop :=
  {v : ℝ × ℝ × ℝ × ℝ |
    ∃ a b c d : ℝ,
    v = (a, b, c, d) ∧
    a ≠ 0 ∧ b ≠ 0 ∧ c ≠ 0 ∧ d ≠ 0 ∧
    a + b + c = d ∧
    (1 : ℝ) / a + 1 / b + 1 / c = 1 / d}
  = ans
def toSet (sol : ℝ → ℝ → ℝ → ℝ → Prop) : Set (ℝ × ℝ × ℝ × ℝ) :=
  {v | sol v.1 v.2.1 v.2.2.1 v.2.2.2}

theorem R19_U_G_incompatible (sol : ℝ → ℝ → ℝ → ℝ → Prop) (hU : R19_U sol) :
    ¬ R19_G (toSet sol) := by
  intro hG
  have h1 : sol 0 1 1 2 := (hU 0 1 1 2).2 (fun h => absurd rfl h)
  have h2 : ((0 : ℝ), (1 : ℝ), (1 : ℝ), (2 : ℝ)) ∈ toSet sol := h1
  rw [← hG] at h2
  obtain ⟨a, b, c, d, hv, ha, _⟩ := h2
  simp only [Prod.mk.injEq] at hv
  exact ha hv.1.symm

/-- Control: GPT's spec implies the fixed spec (they differ only off the nonzero domain). -/
theorem R19_G_to_F (sol : ℝ → ℝ → ℝ → ℝ → Prop) (hG : R19_G (toSet sol)) : R19_F sol := by
  intro a b c d ha hb hc hd
  have hmem : sol a b c d ↔ (a, b, c, d) ∈ toSet sol := Iff.rfl
  rw [hmem, ← hG]
  constructor
  · rintro ⟨a', b', c', d', hv, -, -, -, -, h1, h2⟩
    simp only [Prod.mk.injEq] at hv
    obtain ⟨rfl, rfl, rfl, rfl⟩ := hv
    exact ⟨h1, h2⟩
  · rintro ⟨h1, h2⟩
    exact ⟨a, b, c, d, rfl, ha, hb, hc, hd, h1, h2⟩

/-- And the fixed spec is compatible with GPT's: some answer satisfies both. -/
theorem R19_F_G_compatible : ∃ sol, R19_F sol ∧ R19_G (toSet sol) :=
  ⟨fun a b c d => a ≠ 0 ∧ b ≠ 0 ∧ c ≠ 0 ∧ d ≠ 0 ∧ a + b + c = d ∧ 1 / a + 1 / b + 1 / c = 1 / d,
    fun a b c d ha hb hc hd => ⟨fun h => h.2.2.2.2, fun h => ⟨ha, hb, hc, hd, h⟩⟩,
    by
      ext ⟨a, b, c, d⟩
      simp only [toSet, Set.mem_setOf_eq, Prod.mk.injEq]
      constructor
      · rintro ⟨a', b', c', d', ⟨rfl, rfl, rfl, rfl⟩, h⟩; exact h
      · intro h; exact ⟨a, b, c, d, ⟨rfl, rfl, rfl, rfl⟩, h⟩⟩

/-! ## R14 = putnam_2023_b4, pre-fix: a missing pair of parentheses put every condition
(including `f (t₀ + T) = 2023`) under `∀ k : Fin n`, which is vacuous for n = 0.
Data-independence certificate: for ANY initial value v0 and ANY target, the benchmark
forces the answer to be 0. (The true answer is 29.) -/
def R14_U (v0 target ans : ℝ) : Prop :=
  ∀ (tne : ℕ → (ℕ → ℝ) → Set ℝ)
    (htne : ∀ n ts, tne n ts = {t | t > ts 0 ∧ ∀ i : Fin n, t ≠ ts (i.1 + 1)}),
    IsLeast
    {(T : ℝ) | 0 ≤ T ∧ ∃ (n : ℕ) (ts : ℕ → ℝ) (f : ℝ → ℝ),
      ∀ k : Fin n, ts (k.1 + 1) ≥ ts k.1 + 1 ∧
      ContinuousOn f (Set.Ici (ts 0)) ∧
      ContDiffOn ℝ 1 f (tne n ts) ∧
      DifferentiableOn ℝ (derivWithin f (tne n ts)) (tne n ts) ∧
      f (ts 0) = v0 ∧
      (∀ k : Fin (n + 1),
        Tendsto (derivWithin f (tne n ts)) (𝓝[>] (ts k.1)) (𝓝 0)) ∧
      (∀ k : Fin n,
        ∀ t ∈ Set.Ioo (ts k.1) (ts (k.1 + 1)),
          iteratedDerivWithin 2 f (tne n ts) t = k.1 + 1) ∧
      (∀ t > ts n,
        iteratedDerivWithin 2 f (tne n ts) t = n + 1) ∧
      f (ts 0 + T) = target}
    ans

theorem R14_U_degenerate (v0 target ans : ℝ) : R14_U v0 target ans ↔ ans = 0 := by
  constructor
  · intro h
    obtain ⟨hmem, hlb⟩ := h (fun n ts => {t | t > ts 0 ∧ ∀ i : Fin n, t ≠ ts (i.1 + 1)})
      (fun _ _ => rfl)
    have h0 : (0 : ℝ) ≤ ans := hmem.1
    have : ans ≤ 0 := hlb ⟨le_rfl, 0, fun _ => 0, fun _ => 0, fun k => k.elim0⟩
    linarith
  · rintro rfl tne htne
    exact ⟨⟨le_rfl, 0, fun _ => 0, fun _ => 0, fun k => k.elim0⟩, fun T hT => hT.1⟩

/-! ## R01 = putnam_1977_b6, pre-fix: `[Finite H]` missing, and h = Nat.card H = 0 for
infinite H. Certificate: the benchmark statement is FALSE (at universe 0), witnessed by the
infinite exponent-3 group G = Multiplicative (ℕ → ZMod 3), H = ⊤, a = 1. -/
def R01_U : Prop := ∀ {G : Type} [Group G] (H : Subgroup G) (h : ℕ) (h_def : h = Nat.card H)
    (a : G) (ha : ∀ x : H, (x * a) ^ 3 = 1) (P : Set G)
    (hP : P = {g : G | ∃ xs : List H, (xs.length ≥ 1) ∧
      g = (List.map (fun h : H => h * a) xs).prod}),
    (Finite P) ∧ (P.ncard ≤ 3 * h ^ 2)

theorem R01_U_false : ¬ R01_U := by
  intro h
  let G := Multiplicative (ℕ → ZMod 3)
  have h3 : ∀ y : ZMod 3, 3 • y = 0 := by decide
  have hx : ∀ x : G, x ^ 3 = 1 := by
    intro x
    apply Multiplicative.toAdd.injective
    funext i
    simp only [toAdd_pow, toAdd_one, Pi.smul_apply, Pi.zero_apply]
    exact h3 _
  haveI : Fact (1 < 3) := ⟨by norm_num⟩
  haveI : Infinite G := inferInstanceAs (Infinite (ℕ → ZMod 3))
  obtain ⟨hfin, -⟩ := h (G := G) ⊤ _ rfl 1 (fun x => by rw [mul_one]; exact hx _) Set.univ (by
    ext g
    simp only [Set.mem_univ, true_iff, Set.mem_setOf_eq]
    exact ⟨[⟨g, Subgroup.mem_top g⟩], by simp, by simp⟩)
  haveI := hfin
  haveI : Finite G := Finite.of_equiv _ (Equiv.Set.univ G)
  exact not_finite G

/-! ## R15 = putnam_2003_a5 (our issue #363 / PR #364). Relational schema over abstract sets.
U = benchmark conclusion; F = our fix; G = GPT's independent formalization (A ≃ B). -/
def R15s_U {X Y : Type} (A : Set X) (B : Set Y) : Prop :=
  ∃ f : X → Y, ∀ y ∈ B, ∃! x, x ∈ A ∧ f x = y
def R15s_F {X Y : Type} (A : Set X) (B : Set Y) : Prop :=
  ∃ f : X → Y, (∀ x ∈ A, f x ∈ B) ∧ ∀ y ∈ B, ∃! x, x ∈ A ∧ f x = y
def R15s_G {X Y : Type} (A : Set X) (B : Set Y) : Prop := Nonempty (A ≃ B)

theorem R15_UG_fails : ¬ ∀ (A B : Set ℕ), R15s_U A B ↔ R15s_G A B := by
  intro h
  have hU : R15s_U ({0, 1} : Set ℕ) ({0} : Set ℕ) := by
    refine ⟨fun x => if x = 0 then 0 else 5, fun y hy => ?_⟩
    rw [Set.mem_singleton_iff] at hy
    subst hy
    refine ⟨0, ⟨by simp, by simp⟩, fun x ⟨hx, hfx⟩ => ?_⟩
    by_contra hne
    simp [hne] at hfx
  obtain ⟨e⟩ := (h _ _).1 hU
  have : e ⟨0, by simp⟩ = e ⟨1, by simp⟩ := Subsingleton.elim _ _
  have := congrArg Subtype.val (e.injective this)
  simp at this

theorem R15_FG {X Y : Type} [Nonempty Y] (A : Set X) (B : Set Y) :
    R15s_F A B ↔ R15s_G A B := by
  classical
  constructor
  · rintro ⟨f, hmap, huniq⟩
    refine ⟨Equiv.ofBijective (fun a : A => (⟨f a, hmap a a.2⟩ : B)) ⟨?_, ?_⟩⟩
    · intro a1 a2 h12
      have h12' : f a1 = f a2 := congrArg Subtype.val h12
      obtain ⟨x, -, hx⟩ := huniq (f a1) (hmap a1 a1.2)
      exact Subtype.ext ((hx a1 ⟨a1.2, rfl⟩).trans (hx a2 ⟨a2.2, h12'.symm⟩).symm)
    · intro b
      obtain ⟨x, ⟨hxA, hfx⟩, -⟩ := huniq b b.2
      exact ⟨⟨x, hxA⟩, Subtype.ext hfx⟩
  · rintro ⟨e⟩
    refine ⟨fun x => if hx : x ∈ A then (e ⟨x, hx⟩ : Y) else Classical.arbitrary Y,
      fun x hx => by simp [hx], fun y hy => ⟨(e.symm ⟨y, hy⟩ : X), ⟨(e.symm ⟨y, hy⟩).2, ?_⟩, ?_⟩⟩
    · simp
    · rintro x ⟨hxA, hfx⟩
      simp only [hxA, dite_true] at hfx
      have : e ⟨x, hxA⟩ = ⟨y, hy⟩ := Subtype.ext hfx
      rw [← this, Equiv.symm_apply_apply]

end E2
