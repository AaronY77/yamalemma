import Mathlib

/-! # Exp 5: Lean refutes the false alarms raised blind by GPT (High).  VERIFIED: 0 errors, 0 warnings
(live.lean-lang.org, Lean v4.35.0-rc4 + Mathlib, Oct 13 2026).

GPT claimed: S12 (putnam_2004_a3) `u (n + i * 2 + j)` with i j : Fin 2 computes `i * 2` in Fin 2,
so both rows coincide, det = 0, and the hypotheses are contradictory. S10 (putnam_2024_a6)
`c (i + j + 1)` with i j : Fin n wraps modulo n. Both claims are false: binop% elaborates the whole
arithmetic tree at the expected type ℕ, inserting ↑i, ↑j at the leaves. -/
open Nat
namespace E5c

-- S12: the index elaborates as ↑i * 2 + ↑j in ℕ (definitional).
theorem index_uses_nat (u : ℕ → ℝ) (n : ℕ) (i j : Fin 2) :
    u (n + i * 2 + j) = u (n + (i : ℕ) * 2 + (j : ℕ)) := rfl

-- S12: the second row is (u (n+2), u (n+3)), not a copy of row 0.
theorem second_row_indices (u : ℕ → ℝ) (n : ℕ) :
    (fun i j : Fin 2 => u (n + i * 2 + j)) 1 0 = u (n + 2) ∧
    (fun i j : Fin 2 => u (n + i * 2 + j)) 1 1 = u (n + 3) := ⟨rfl, rfl⟩

-- S12: the n = 0 hypothesis is satisfiable (u = 1,1,1,2: det = 1·2 − 1·1 = 1 = 0!), so not contradictory.
theorem determinant_at_zero : Matrix.det (fun i j : Fin 2 =>
    (fun k : ℕ => if k = 3 then (2 : ℝ) else 1) (0 + i * 2 + j)) = ((0 : ℕ)! : ℝ) := by
  erw [Matrix.det_fin_two]; norm_num

-- S10: no wraparound. n = 3, entry (2,2) is c 5, not c ((2+2) % 3 + 1) = c 2.
theorem concrete_index_no_wrap (c : ℕ → ℝ) : (Matrix.of fun (i j : Fin 3) => c (i + j + 1)) 2 2 = c 5 := rfl
theorem general_index_uses_nat (c : ℕ → ℝ) (n : ℕ) (i j : Fin n) :
    (Matrix.of fun (i j : Fin n) => c (i + j + 1)) i j = c ((i : ℕ) + (j : ℕ) + 1) := rfl

-- Negative control: genuine Fin arithmetic does wrap, so the tests above would catch a wrap.
theorem genuine_fin_wrap : ((2 : Fin 3) + 2 : Fin 3) = 1 := rfl

end E5c
#print axioms E5c.index_uses_nat
#print axioms E5c.second_row_indices
#print axioms E5c.determinant_at_zero
#print axioms E5c.concrete_index_no_wrap
#print axioms E5c.general_index_uses_nat
#print axioms E5c.genuine_fin_wrap
