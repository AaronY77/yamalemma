# S11-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The comparison proposition places x after the existential choices. Reviewing the quantifier order should expose the translation difference; proving equivalence would not by itself resolve it, since both propositions may be true.

## Source

Item fingerprint: `2c1b637189f2f1cc788905c43e58144426cfc0e4d4ba93fd83eac108c17d2770`
Source: putnam_2004_a4.lean

## Formal claim

```lean
(open Nat Topology Filter in
∀ (n : ℕ) (npos : n > 0)
  (x : Fin n → ℝ)
  (avals : ℕ → (ℕ → Fin n → ℝ) → Prop)
  (havals : ∀ N a, avals N a ↔ ∀ (i : Fin N) (j : Fin n), (a i j = -1 ∨ a i j = 0 ∨ a i j = 1)), ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ),
    avals N a ∧
    (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n) ↔ (∀ (n : ℕ), n > 0 → ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ), (∀ (i : Fin N) (j : Fin n), a i j = -1 ∨ a i j = 0 ∨ a i j = 1) ∧ ∀ (x : Fin n → ℝ), (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n)
```

## Bridge obligations

- translated: Review whether “identically” requires coefficients and N independent of x. Logical equivalence between the two true theorems would not establish that the original quantifier order faithfully translates that requirement. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: <input>:1:22: expected term
  Evidence ID: `66f2660b4a7bc352088b82de795306cf5b5d6d42c59786c3284558d76b87bffe`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: probe.lean:1:11: error: Tactic `introN` failed: There are no additional binders or `let` bindings in the goal to introduce

⊢ (∀ n > 0,
      (∀ (x : ((Fin n) → ℝ)) (avals : (ℕ → ((ℕ → ((Fin n) → ℝ)) → Prop))),
        ((∀ (N : ℕ) (a : (ℕ → ((Fin n) → ℝ))),
            ((avals N a) ↔
              (∀ (i : (Fin N)) (j : (Fin n)), (((a (↑i) j) = (-1)) ∨ (((a (↑i) j) = 0) ∨ ((a (↑i) j) = 1)))))) →
          (∃ N c a, ((avals N a) ∧ ((∏ i, (x i)) = (∑ i, (↑(c i) * ((∑ j, ((a (↑i) j) * (x j))) ^ n))))))))) ↔
    (∀ n > 0,
      (∃ N c a,
        ((∀ (i : (Fin N)) (j : (Fin n)), (((a (↑i) j) = (-1)) ∨ (((a (↑i) j) = 0) ∨ ((a (↑i) j) = 1)))) ∧
          (∀ (x : ((Fin n) → ℝ)), ((∏ i, (x i)) = (∑ i, (↑(c i) * ((∑ j, ((a (↑i) j) * (x j))) ^ n))))))))

  Evidence ID: `2b2f50a60f818360a0f8c872c01483998a260475b8457d57970d24b47a7997bf`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:15: expected end of input
  Evidence ID: `8f5d8a31398a7181491bcd4eb26c8ae03700f511f583860cf3bb1091dfc89fc5`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:15: expected end of input
  Evidence ID: `07fad4388a67beaf0d85438db4dfe7033691d6f3d5accbf9d59f4c0352a3e11d`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
