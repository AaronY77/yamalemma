import Mathlib
set_option linter.unusedVariables false

namespace E1c
open Filter Topology

/-! ## P05: Opus/Sonnet (Icc 1 6 ×ˢ Icc 1 6, ratio over its card), GPT (Fin 6 × Fin 6, +2, /36),
Gemini (Finset.product, /36). Schema: generalize Nat.Prime to any decidable Q. -/
def P05s_O (Q : ℕ → Prop) [DecidablePred Q] : Prop :=
  ((((Finset.Icc 1 6 ×ˢ Finset.Icc 1 6).filter (fun p : ℕ × ℕ => Q (p.1 + p.2))).card : ℚ) /
    ((Finset.Icc 1 6 ×ˢ Finset.Icc 1 6).card : ℚ)) = 5 / 12
def P05s_G (Q : ℕ → Prop) [DecidablePred Q] : Prop :=
  ((Finset.univ.filter (fun p : Fin 6 × Fin 6 => Q (p.1.val + p.2.val + 2))).card : ℚ) / 36 =
    (5 : ℚ) / 12
def P05s_Ge (Q : ℕ → Prop) [DecidablePred Q] : Prop :=
  ((Finset.filter (fun p : ℕ × ℕ => Q (p.1 + p.2))
    (Finset.product (Finset.Icc 1 6) (Finset.Icc 1 6))).card : ℚ) / 36 = 5 / 12

example : ((((Finset.Icc 1 6 ×ˢ Finset.Icc 1 6).filter
        (fun p : ℕ × ℕ => (p.1 + p.2).Prime)).card : ℚ) /
      ((Finset.Icc 1 6 ×ˢ Finset.Icc 1 6).card : ℚ)) = 5 / 12 ↔ P05s_O Nat.Prime := Iff.rfl
example : ((Finset.univ.filter
      (fun p : Fin 6 × Fin 6 =>
        Nat.Prime (p.1.val + p.2.val + 2))).card : ℚ) / 36 =
      (5 : ℚ) / 12 ↔ P05s_G Nat.Prime := Iff.rfl
example : ((Finset.filter (fun p : ℕ × ℕ => (p.1 + p.2).Prime)
      (Finset.product (Finset.Icc 1 6) (Finset.Icc 1 6))).card : ℚ) / 36 = 5 / 12 ↔
    P05s_Ge Nat.Prime := Iff.rfl

def e5 : Fin 6 × Fin 6 ↪ ℕ × ℕ :=
  ⟨fun p => (p.1.val + 1, p.2.val + 1), by
    intro a b h
    simp only [Prod.mk.injEq] at h
    exact Prod.ext (Fin.ext (by omega)) (Fin.ext (by omega))⟩

theorem e5_univ : (Finset.univ : Finset (Fin 6 × Fin 6)).map e5 =
    Finset.Icc 1 6 ×ˢ Finset.Icc 1 6 := by decide

theorem P05_card (Q : ℕ → Prop) [DecidablePred Q] :
    ((Finset.Icc 1 6 ×ˢ Finset.Icc 1 6).filter (fun p : ℕ × ℕ => Q (p.1 + p.2))).card =
    (Finset.univ.filter (fun p : Fin 6 × Fin 6 => Q (p.1.val + p.2.val + 2))).card := by
  rw [← e5_univ, Finset.filter_map, Finset.card_map]
  all_goals congr 1
  all_goals (apply Finset.filter_congr; intro p _
             show Q (p.1.val + 1 + (p.2.val + 1)) ↔ Q (p.1.val + p.2.val + 2)
             rw [show p.1.val + 1 + (p.2.val + 1) = p.1.val + p.2.val + 2 by omega])

theorem P05s_OG (Q : ℕ → Prop) [DecidablePred Q] : P05s_O Q ↔ P05s_G Q := by
  unfold P05s_O P05s_G
  rw [P05_card, show (Finset.Icc 1 6 ×ˢ Finset.Icc 1 6 : Finset (ℕ × ℕ)).card = 36 by decide]
  norm_num

theorem P05s_OGe (Q : ℕ → Prop) [DecidablePred Q] : P05s_O Q ↔ P05s_Ge Q := by
  unfold P05s_O P05s_Ge
  rw [show (Finset.Icc 1 6 ×ˢ Finset.Icc 1 6 : Finset (ℕ × ℕ)).card = 36 by decide]
  rfl

/-! ## P20 (Fekete). Opus: ⨅ n (_ : 1 ≤ n); Sonnet: ⨅ n : ℕ+; GPT: shifted sequence + sInf of a
set, with the division ascribed to EReal; Gemini: sInf with `∃ n ≥ 1`, EReal ascription. -/
noncomputable def u20 (a : ℕ → ℝ) (n : ℕ) : EReal := ((a n / (n : ℝ) : ℝ) : EReal)

def P20_O : Prop := ∀ (a : ℕ → ℝ), (∀ m n : ℕ, 1 ≤ m → 1 ≤ n → a (m + n) ≤ a m + a n) →
    Filter.Tendsto (fun n : ℕ => ((a n / (n : ℝ) : ℝ) : EReal)) Filter.atTop
      (nhds (⨅ (n : ℕ) (_ : 1 ≤ n), ((a n / (n : ℝ) : ℝ) : EReal)))
def P20_S : Prop := ∀ (a : ℕ → ℝ), (∀ m n : ℕ, 0 < m → 0 < n → a (m + n) ≤ a m + a n) →
    Tendsto (fun n : ℕ => ((a n / (n : ℝ) : ℝ) : EReal)) atTop
      (𝓝 (⨅ n : ℕ+, ((a (n : ℕ) / ((n : ℕ) : ℝ) : ℝ) : EReal)))
def P20_G : Prop := ∀ (a : ℕ → ℝ), (∀ m n : ℕ, 0 < m → 0 < n → a (m + n) ≤ a m + a n) →
    Filter.Tendsto
      (fun n : ℕ =>
        ((a (n + 1) / ((n + 1 : ℕ) : ℝ)) : EReal))
      Filter.atTop
      (nhds
        (sInf
          {x : EReal |
            ∃ n : ℕ,
              0 < n ∧
              x = ((a n / (n : ℝ)) : EReal)}))
def P20_Ge : Prop := ∀ (a : ℕ → ℝ), (∀ m n, 0 < m → 0 < n → a (m + n) ≤ a m + a n) →
    Tendsto (fun n : ℕ => ((a n / (n : ℝ)) : EReal)) atTop
      (𝓝 (sInf {x : EReal | ∃ n ≥ 1, x = (a n / (n : ℝ) : EReal)}))

theorem inf_eq_sInf (u : ℕ → EReal) :
    (⨅ (n : ℕ) (_ : 1 ≤ n), u n) = sInf {x : EReal | ∃ n : ℕ, 0 < n ∧ x = u n} := by
  apply le_antisymm
  · apply le_sInf; rintro x ⟨n, hn, rfl⟩; exact iInf₂_le n hn
  · apply le_iInf₂; intro n hn; exact sInf_le ⟨n, hn, rfl⟩

theorem inf_pnat (u : ℕ → EReal) :
    (⨅ n : ℕ+, u (n : ℕ)) = ⨅ (n : ℕ) (_ : 1 ≤ n), u n := by
  apply le_antisymm
  · apply le_iInf₂; intro n hn; exact iInf_le_of_le ⟨n, hn⟩ le_rfl
  · apply le_iInf; intro n; exact iInf₂_le (n : ℕ) n.pos

/-- Whatever the EReal ascription elaborated to, it equals the ℝ-division coerced. -/
theorem hterm (a : ℕ → ℝ) (n : ℕ) : ((a n / (n : ℝ)) : EReal) = u20 a n := by
  simp [u20, EReal.coe_div]

theorem P20_OG : P20_O ↔ P20_G := by
  unfold P20_O P20_G
  apply forall_congr'; intro a
  apply imp_congr Iff.rfl
  have e1 : (fun n : ℕ => ((a (n + 1) / ((n + 1 : ℕ) : ℝ)) : EReal)) =
      fun n => u20 a (n + 1) := funext fun n => hterm a (n + 1)
  have e2 : {x : EReal | ∃ n : ℕ, 0 < n ∧ x = ((a n / (n : ℝ)) : EReal)} =
      {x : EReal | ∃ n : ℕ, 0 < n ∧ x = u20 a n} :=
    Set.ext fun x => ⟨fun ⟨n, hn, hx⟩ => ⟨n, hn, hx.trans (hterm a n)⟩,
      fun ⟨n, hn, hx⟩ => ⟨n, hn, hx.trans (hterm a n).symm⟩⟩
  rw [e1, e2, ← inf_eq_sInf (u20 a)]
  exact (Filter.tendsto_add_atTop_iff_nat (f := u20 a) 1).symm

theorem P20_OS : P20_O ↔ P20_S := by
  unfold P20_O P20_S
  apply forall_congr'; intro a
  apply imp_congr Iff.rfl
  have : (⨅ n : ℕ+, ((a (n : ℕ) / ((n : ℕ) : ℝ) : ℝ) : EReal)) =
      ⨅ (n : ℕ) (_ : 1 ≤ n), ((a n / (n : ℝ) : ℝ) : EReal) :=
    inf_pnat (fun n => ((a n / (n : ℝ) : ℝ) : EReal))
  rw [this]

theorem P20_OGe : P20_O ↔ P20_Ge := by
  unfold P20_O P20_Ge
  apply forall_congr'; intro a
  apply imp_congr Iff.rfl
  have e1 : (fun n : ℕ => ((a n / (n : ℝ)) : EReal)) = u20 a := funext (hterm a)
  have e2 : {x : EReal | ∃ n ≥ 1, x = (a n / (n : ℝ) : EReal)} =
      {x : EReal | ∃ n : ℕ, 0 < n ∧ x = u20 a n} :=
    Set.ext fun x => ⟨fun ⟨n, hn, hx⟩ => ⟨n, hn, hx.trans (hterm a n)⟩,
      fun ⟨n, hn, hx⟩ => ⟨n, hn, hx.trans (hterm a n).symm⟩⟩
  rw [e1, e2, ← inf_eq_sInf (u20 a)]
  rfl

end E1c

/-! ## Type-checks of the statements adjudicated "ill-typed" in Q1 (each is expected to error). -/
namespace TC

theorem P13_GPT (p : ℕ)
    (hp : Nat.Prime p)
    (hp3 : 3 < p) :
    (∑ r ∈ (Finset.Icc 1 (p - 1)).filter
      (fun r : ℕ =>
        ∃ x : ℕ, x ^ 2 % p = r), r) % p = 0 := by
  sorry

theorem P04_Gemini (E : Type*) [NormedAddTorsor ℝ E] [InnerProductSpace ℝ E] (A B C P : E)
    (h_inside : P ∈ (convexHull ℝ ({A, B, C} : Set E))) :
    dist P A + dist P B + dist P C < dist A B + dist B C + dist C A := by sorry

end TC
