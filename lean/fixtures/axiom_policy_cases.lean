namespace PolicyFixture

-- Complete proof with no axiom dependencies.
theorem no_axioms : (0 : Nat) = 0 := by
  rfl

-- Intentionally incomplete: our policy must reject it.
theorem admitted : False := by
  sorry

-- A custom assumption: our policy must also reject it.
axiom custom_assumption : False

theorem uses_custom : False :=
  custom_assumption

end PolicyFixture

#print axioms PolicyFixture.no_axioms
#print axioms PolicyFixture.admitted
#print axioms PolicyFixture.uses_custom
