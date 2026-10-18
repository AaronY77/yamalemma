import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from yamalemma.selection import check_selection, fix_history, select_heldout, write_selection


ROOT = Path(__file__).resolve().parents[1]


def run(root, *arguments):
    subprocess.run(['git', '-C', str(root), *arguments], check=True, capture_output=True)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name) / 'bench'
        self.source = self.repo / 'lean4' / 'src'
        self.source.mkdir(parents=True)
        (self.repo / 'lean4' / 'lean-toolchain').write_text('leanprover/lean4:v4.33.1\n')
        for index in range(8):
            (self.source / f'putnam_200{index}_a1.lean').write_text(f'theorem putnam_200{index}_a1 : True := trivial\n')
        run(self.repo, 'init', '-q')
        run(self.repo, '-c', 'user.email=fixture@example.com', '-c', 'user.name=fixture', 'add', '.')
        run(self.repo, '-c', 'user.email=fixture@example.com', '-c', 'user.name=fixture', 'commit', '-qm', 'synthetic benchmark')

    def test_selection_is_deterministic_and_excludes_development(self):
        first = select_heldout(self.source, ['putnam_2000_a1', 'putnam_1999_b1'], 3, 'seed-1')
        second = select_heldout(self.source, ['putnam_2000_a1', 'putnam_1999_b1'], 3, 'seed-1')
        self.assertEqual(first['selected'], second['selected'])
        self.assertNotIn('putnam_2000_a1', first['selected'])
        self.assertEqual(first['development_excluded'], ['putnam_2000_a1'])
        self.assertEqual(first['unknown_development_names'], ['putnam_1999_b1'])
        self.assertEqual(first['pool_size'], 7)
        self.assertEqual(first['toolchain'], 'leanprover/lean4:v4.33.1')
        self.assertEqual(set(first['groups']), set(first['selected']))
        with self.assertRaises(ValueError):
            select_heldout(self.source, [], 9, 'seed-1')
        with self.assertRaises(ValueError):
            select_heldout(self.source, [], 2, '')

    def test_dirty_or_moved_checkout_is_rejected(self):
        selection = select_heldout(self.source, [], 2, 'seed-1')
        path = Path(self.repo.parent) / 'selection.json'
        write_selection(selection, path)
        with self.assertRaises(FileExistsError):
            write_selection(selection, path)
        self.assertEqual(check_selection(selection, self.source), set(selection['selected']))
        target = self.source / f'{selection["selected"][0]}.lean'
        target.write_text('theorem changed : False := sorry\n')
        with self.assertRaisesRegex(ValueError, 'local changes'):
            select_heldout(self.source, [], 2, 'seed-1')
        with self.assertRaises(ValueError):
            check_selection(selection, self.source)

    def test_fix_history_lists_statement_changes_only(self):
        email, name = '-c', 'user.email=fixture@example.com'
        (self.source / 'putnam_2003_a1.lean').write_text('theorem putnam_2003_a1 : 1 = 1 := rfl\n')
        run(self.repo, email, name, '-c', 'user.name=fixture', 'commit', '-qam', 'Fix 2003 A1 statement')
        (self.repo / 'lean4' / 'lean-toolchain').write_text('leanprover/lean4:v4.34.0\n')
        (self.source / 'putnam_2004_a1.lean').write_text('theorem putnam_2004_a1 : 2 = 2 := rfl\n')
        run(self.repo, email, name, '-c', 'user.name=fixture', 'commit', '-qam', 'Update Lean toolchain and Mathlib')
        rows = fix_history(self.source)
        subjects = [row['subject'] for row in rows]
        self.assertIn('Fix 2003 A1 statement', subjects)
        self.assertNotIn('Update Lean toolchain and Mathlib', subjects)
        self.assertEqual(rows[0]['problems'], ['putnam_2003_a1'])

    def test_putnambench_environment_uses_the_same_worker(self):
        self.assertEqual((ROOT / 'lean' / 'Yamalemma' / 'Worker.lean').read_bytes(),
                         (ROOT / 'lean-putnambench' / 'Yamalemma' / 'Worker.lean').read_bytes())
        development = json.loads((ROOT / 'fixtures' / 'development_problems.json').read_text())
        self.assertTrue(all(row['name'].startswith('putnam_') and row['reason'] for row in development['problems']))



class AnswerSubstitutionTests(unittest.TestCase):
    def test_commented_answer_replaces_only_definition_placeholders(self):
        from yamalemma.ingest import substitute_answers
        source = ('abbrev putnam_x_solution : ℤ × ℤ := sorry\n-- (11, 8)\n'
                  'theorem putnam_x : putnam_x_solution = (11, 8) := sorry\n')
        text, records = substitute_answers(source)
        self.assertIn(':= ((11, 8))\n-- (11, 8)', text)
        self.assertTrue(text.endswith(':= sorry\n'))
        self.assertEqual(records[0]['definition'], 'putnam_x_solution')
        self.assertEqual(records[0]['line'], 1)
        self.assertEqual(substitute_answers('abbrev a : ℕ := sorry\n--\n'), ('abbrev a : ℕ := sorry\n--\n', []))
        self.assertEqual(substitute_answers('abbrev a : ℕ := sorry\ntheorem t : True := trivial\n')[1], [])


if __name__ == '__main__':
    unittest.main()
