import Mathlib
set_option linter.unusedVariables false

namespace E1

/-! ## P10: O/S/Ge state it over ℕ; GPT over ℤ with Int.toNat.
Schema: generalize `Nat.Prime` to an arbitrary predicate Q. -/
def P10s_O (Q : ℕ → Prop) : Prop := ∀ n : ℕ, 2 ≤ n → ¬ Q (n ^ 4 + 4)
def P10s_G (Q : ℕ → Prop) : Prop := ∀ n : ℤ, 2 ≤ n → ¬ Q (Int.toNat (n ^ 4 + 4))

example : (∀ n : ℕ, 2 ≤ n → ¬ Nat.Prime (n ^ 4 + 4)) ↔ P10s_O Nat.Prime := Iff.rfl
example : (∀ n : ℤ, 2 ≤ n → ¬ Nat.Prime (Int.toNat (n ^ 4 + 4))) ↔ P10s_G Nat.Prime := Iff.rfl

theorem P10s (Q : ℕ → Prop) : P10s_O Q ↔ P10s_G Q := by
  have key : ∀ m : ℕ, ((m : ℤ) ^ 4 + 4).toNat = m ^ 4 + 4 := by
    intro m
    have e : ((m : ℤ) ^ 4 + 4) = ((m ^ 4 + 4 : ℕ) : ℤ) := by push_cast; ring
    rw [e]
    exact Int.toNat_natCast _
  constructor
  · intro h n hn
    obtain ⟨m, rfl⟩ := Int.eq_ofNat_of_zero_le (by omega : (0 : ℤ) ≤ n)
    rw [key]
    exact h m (by exact_mod_cast hn)
  · intro h m hm
    have := h (m : ℤ) (by exact_mod_cast hm)
    rwa [key] at this

/-! ## P17: O/S inline; GPT wraps `0 < n` into the predicate; Gemini omits positivity.
Schema: generalize "square-full" to an arbitrary predicate R. -/
def P17s_O (R : ℕ → Prop) : Prop := Set.Infinite {n : ℕ | 0 < n ∧ R n ∧ R (n + 1)}
def P17s_G (R : ℕ → Prop) : Prop :=
  Set.Infinite {n : ℕ | (0 < n ∧ R n) ∧ (0 < n + 1 ∧ R (n + 1))}
def P17s_Ge (R : ℕ → Prop) : Prop := Set.Infinite {n : ℕ | R n ∧ R (n + 1)}

def SF (m : ℕ) : Prop := ∀ p : ℕ, p.Prime → p ∣ m → p ^ 2 ∣ m
def P17_squareFull (n : ℕ) : Prop := 0 < n ∧ ∀ p : ℕ, Nat.Prime p → p ∣ n → p ^ 2 ∣ n
def IsSquareFull (m : ℕ) : Prop := ∀ p : ℕ, p.Prime → p ∣ m → p ^ 2 ∣ m

example : Set.Infinite {n : ℕ | 0 < n ∧ (∀ p : ℕ, p.Prime → p ∣ n → p ^ 2 ∣ n) ∧
    (∀ p : ℕ, p.Prime → p ∣ n + 1 → p ^ 2 ∣ n + 1)} ↔ P17s_O SF := Iff.rfl
example : Set.Infinite {n : ℕ | P17_squareFull n ∧ P17_squareFull (n + 1)} ↔ P17s_G SF := Iff.rfl
example : Set.Infinite {n : ℕ | IsSquareFull n ∧ IsSquareFull (n + 1)} ↔ P17s_Ge SF := Iff.rfl

theorem P17s_OG (R : ℕ → Prop) : P17s_O R ↔ P17s_G R := by
  unfold P17s_O P17s_G
  have : {n : ℕ | 0 < n ∧ R n ∧ R (n + 1)} =
      {n : ℕ | (0 < n ∧ R n) ∧ (0 < n + 1 ∧ R (n + 1))} := by
    ext n
    constructor
    · rintro ⟨h0, h1, h2⟩; exact ⟨⟨h0, h1⟩, Nat.succ_pos n, h2⟩
    · rintro ⟨⟨h0, h1⟩, _, h2⟩; exact ⟨h0, h1, h2⟩
  rw [this]

/-- Gemini's dropped positivity is certified harmless for every R. -/
theorem P17s_OGe (R : ℕ → Prop) : P17s_O R ↔ P17s_Ge R := by
  unfold P17s_O P17s_Ge
  constructor
  · intro h; exact h.mono (fun n hn => ⟨hn.2.1, hn.2.2⟩)
  · intro h
    have h' := h.diff (Set.finite_singleton 0)
    exact h'.mono (fun n hn => ⟨Nat.pos_of_ne_zero hn.2, hn.1.1, hn.1.2⟩)

/-! ## P19: O/S use IsLeast; GPT unfolds minimality; Gemini replaces the divisibility
condition with `(n !).factorization 5 = 100`. -/
def P19s_O (T : ℕ → Prop) (ans : ℕ) : Prop := IsLeast {n : ℕ | 0 < n ∧ T n} ans
def P19s_G (T : ℕ → Prop) (ans : ℕ) : Prop :=
  0 < ans ∧ T ans ∧ ∀ m, 0 < m → m < ans → ¬ T m

theorem P19s_OG (T : ℕ → Prop) (ans : ℕ) : P19s_O T ans ↔ P19s_G T ans := by
  unfold P19s_O P19s_G
  constructor
  · rintro ⟨⟨h0, hT⟩, hl⟩
    refine ⟨h0, hT, fun m hm hlt hTm => ?_⟩
    have := hl ⟨hm, hTm⟩
    omega
  · rintro ⟨h0, hT, hl⟩
    refine ⟨⟨h0, hT⟩, fun m ⟨hm, hTm⟩ => ?_⟩
    by_contra hc
    exact hl m hm (by omega) hTm

def T19 (n : ℕ) : Prop := 10 ^ 100 ∣ Nat.factorial n ∧ ¬ 10 ^ 101 ∣ Nat.factorial n
def P19_Opus (ans : ℕ) : Prop :=
  IsLeast {n : ℕ | 0 < n ∧ 10 ^ 100 ∣ Nat.factorial n ∧ ¬ 10 ^ 101 ∣ Nat.factorial n} ans
def P19_GPT (ans : ℕ) : Prop :=
  0 < ans ∧ (10 : ℕ) ^ 100 ∣ Nat.factorial ans ∧ ¬ ((10 : ℕ) ^ 101 ∣ Nat.factorial ans) ∧
    (∀ m : ℕ, 0 < m → m < ans →
      ¬ ((10 : ℕ) ^ 100 ∣ Nat.factorial m ∧ ¬ ((10 : ℕ) ^ 101 ∣ Nat.factorial m)))

example (ans : ℕ) : P19_Opus ans ↔ P19s_O T19 ans := Iff.rfl

theorem P19_OG (ans : ℕ) : P19_Opus ans ↔ P19_GPT ans := by
  refine (P19s_OG T19 ans).trans ⟨?_, ?_⟩
  · rintro ⟨a, ⟨b, c⟩, d⟩; exact ⟨a, b, c, d⟩
  · rintro ⟨a, b, c, d⟩; exact ⟨a, ⟨b, c⟩, d⟩

/-- Generalize the factorial to an arbitrary f. -/
def P19f_O (f : ℕ → ℕ) (ans : ℕ) : Prop :=
  IsLeast {n : ℕ | 0 < n ∧ 10 ^ 100 ∣ f n ∧ ¬ 10 ^ 101 ∣ f n} ans
def P19f_Ge (f : ℕ → ℕ) (ans : ℕ) : Prop :=
  IsLeast {n : ℕ | 0 < n ∧ (f n).factorization 5 = 100} ans

example (ans : ℕ) : P19_Opus ans ↔ P19f_O Nat.factorial ans := Iff.rfl
example (ans : ℕ) : IsLeast {n : ℕ | 0 < n ∧ Nat.factorization (Nat.factorial n) 5 = 100} ans ↔
    P19f_Ge Nat.factorial ans := Iff.rfl

/-- Schema refutation (f = const 5^100). NOTE: this does NOT show Gemini's P19 is wrong;
for f = factorial the two agree because v₂(n!) ≥ v₅(n!). See P19 concrete check. -/
theorem P19f_OGe_fails : ¬ ∀ (f : ℕ → ℕ) (ans : ℕ), P19f_O f ans ↔ P19f_Ge f ans := by
  intro h
  have hv : ((5 : ℕ) ^ 100).factorization 5 = 100 := by
    rw [Nat.factorization_pow, Finsupp.smul_apply, Nat.prime_five.factorization_self] <;> norm_num
  have hGe : P19f_Ge (fun _ => 5 ^ 100) 1 := ⟨⟨one_pos, hv⟩, fun m ⟨hm, _⟩ => hm⟩
  obtain ⟨⟨_, hd, _⟩, _⟩ := (h _ 1).mpr hGe
  have h2 : 2 ∣ 5 ^ 100 := (dvd_pow (by norm_num : (2 : ℕ) ∣ 10) (by norm_num)).trans hd
  have := Nat.Prime.dvd_of_dvd_pow Nat.prime_two h2
  omega

/-! ## P07: Opus (abstract F + recurrence), Sonnet/GPT (Nat.fib, ncard), Gemini (∃ Finset: lower bound).
Schema: generalize the counted set family to an arbitrary C. -/
def CS (n : ℕ) : Set (List ℕ) := {l | l.sum = n ∧ ∀ x ∈ l, x = 1 ∨ x = 2}
def CO (n : ℕ) : Set (List ℕ) := {l | (∀ x ∈ l, x = 1 ∨ x = 2) ∧ l.sum = n}

def P07s_O (C : ℕ → Set (List ℕ)) : Prop :=
  ∀ F : ℕ → ℕ, F 1 = 1 → F 2 = 1 → (∀ k : ℕ, 1 ≤ k → F (k + 2) = F (k + 1) + F k) →
    ∀ n : ℕ, 0 < n → (C n).ncard = F (n + 1)
def P07s_S (C : ℕ → Set (List ℕ)) : Prop := ∀ n : ℕ, 0 < n → (C n).ncard = Nat.fib (n + 1)
def P07s_Ge (C : ℕ → Set (List ℕ)) : Prop :=
  ∀ n : ℕ, 0 < n → ∃ s : Finset (List ℕ), (∀ l ∈ s, l ∈ C n) ∧ s.card = Nat.fib (n + 1)

example : (∀ (F : ℕ → ℕ) (hF1 : F 1 = 1) (hF2 : F 2 = 1)
    (hrec : ∀ k : ℕ, 1 ≤ k → F (k + 2) = F (k + 1) + F k) (n : ℕ) (hn : 0 < n),
    {l : List ℕ | (∀ x ∈ l, x = 1 ∨ x = 2) ∧ l.sum = n}.ncard = F (n + 1)) ↔ P07s_O CO := Iff.rfl
example : (∀ n : ℕ, 0 < n → {l : List ℕ | l.sum = n ∧ ∀ x ∈ l, x = 1 ∨ x = 2}.ncard =
    Nat.fib (n + 1)) ↔ P07s_S CS := Iff.rfl
example : (∀ n : ℕ, 0 < n → ({l : List ℕ | (∀ x ∈ l, x = 1 ∨ x = 2) ∧ l.sum = n} :
    Set (List ℕ)).ncard = Nat.fib (n + 1)) ↔ P07s_S CO := Iff.rfl
example : (∀ n : ℕ, 0 < n → ∃ s : Finset (List ℕ),
    (∀ l ∈ s, l.sum = n ∧ ∀ x ∈ l, x = 1 ∨ x = 2) ∧ s.card = Nat.fib (n + 1)) ↔
    P07s_Ge CS := Iff.rfl

theorem CO_eq : CO = CS := by
  funext n; ext l; exact and_comm

theorem fib_unique (F : ℕ → ℕ) (h1 : F 1 = 1) (h2 : F 2 = 1)
    (hr : ∀ k, 1 ≤ k → F (k + 2) = F (k + 1) + F k) : ∀ n, 1 ≤ n → F n = Nat.fib n := by
  have key : ∀ n, F (n + 1) = Nat.fib (n + 1) ∧ F (n + 2) = Nat.fib (n + 2) := by
    intro n
    induction n with
    | zero => exact ⟨by simpa using h1, by simpa using h2⟩
    | succ k ih =>
      obtain ⟨a, b⟩ := ih
      have r := hr (k + 1) (by omega)
      have fb := Nat.fib_add_two (n := k + 1)
      have b' : F (k + 1 + 1) = Nat.fib (k + 1 + 1) := b
      exact ⟨b, by omega⟩
  intro n hn
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  exact (key m).1

theorem P07s_OS (C : ℕ → Set (List ℕ)) : P07s_O C ↔ P07s_S C := by
  constructor
  · intro h n hn
    exact h Nat.fib Nat.fib_one Nat.fib_two
      (fun k _ => by rw [Nat.fib_add_two, add_comm]) n hn
  · intro h F h1 h2 hr n hn
    rw [h n hn, fib_unique F h1 h2 hr (n + 1) (by omega)]

/-- Opus ≡ Sonnet ≡ GPT for P07. -/
theorem P07_OS : P07s_O CO ↔ P07s_S CS := by rw [CO_eq]; exact P07s_OS CS

/-- Gemini's P07 is not schema-equivalent: with C n = univ (infinite), ncard = 0 ≠ fib 2,
but a Finset of size fib (n+1) inside univ always exists. -/
theorem P07s_SGe_fails : ¬ ∀ C : ℕ → Set (List ℕ), P07s_S C ↔ P07s_Ge C := by
  intro h
  have hGe : P07s_Ge (fun _ => Set.univ) := by
    intro n hn
    refine ⟨(Finset.range (Nat.fib (n + 1))).image (fun i => List.replicate i 0),
      fun l _ => Set.mem_univ l, ?_⟩
    rw [Finset.card_image_of_injective _
      (fun a b hab => by simpa using congrArg List.length hab), Finset.card_range]
  have := (h _).mpr hGe 1 one_pos
  simp at this

end E1
