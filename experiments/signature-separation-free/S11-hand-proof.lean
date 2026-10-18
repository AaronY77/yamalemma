by
  refine ⟨1, fun _ => 0, fun N _ => N = 0, ⟨0, Fin.elim0, fun _ _ => 0, rfl, by simp⟩, ?_⟩
  rintro ⟨N, c, a, hN, h⟩
  subst hN
  have h1 := h (fun _ => 1)
  simp at h1
