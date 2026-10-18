by
  refine ⟨Multiplicative (ZMod 3), inferInstance, inferInstance, Multiplicative.ofAdd 1, Multiplicative.ofAdd 1, _, ⟨?_, ?_, rfl⟩, ?_⟩
  · rw [Set.pair_eq_singleton]
    exact (Subgroup.eq_top_iff' _).2 fun x => Subgroup.mem_closure_singleton.2 ⟨((Multiplicative.toAdd x).val : ℤ), by
      rw [← ofAdd_zsmul, zsmul_one, Int.cast_natCast, ZMod.natCast_zmod_val]; rfl⟩
  · rw [orderOf_ofAdd_eq_addOrderOf, ZMod.addOrderOf_one]
    decide
  · rintro ⟨⟨-, hg, -⟩, -⟩
    exact hg ((Subgroup.eq_top_iff' _).2 fun x => Subgroup.mem_closure_singleton.2 ⟨((Multiplicative.toAdd x).val : ℤ), by
      rw [← ofAdd_zsmul, zsmul_one, Int.cast_natCast, ZMod.natCast_zmod_val]; rfl⟩)
