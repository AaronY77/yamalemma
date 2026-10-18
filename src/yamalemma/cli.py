import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from yamalemma.adjudicate import adjudicate
from yamalemma.axiom_policy import assess_axioms
from yamalemma.axiom_report import parse_axiom_report
from yamalemma.domain import load_json, make_probe, save_json
from yamalemma.harness import check_probe, environment_record
from yamalemma.ingest import ingest_putnam
from yamalemma.precheck import precheck
from yamalemma.report import write_report
from yamalemma.runner import run_lean
from yamalemma.worker import LeanWorker, WorkerError
from yamalemma.config import load_config
from yamalemma.fixes import issue_draft


def emit(value):
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(description='Yamalemma: controlled formal evidence and benchmark review')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'check', 'ingest', 'precheck', 'demo', 'replay', 'doctor', 'audit', 'freeze', 'evaluate', 'score', 'draft', 'review-audit', 'model-info', 'local-model', 'budget-status', 'budget-init', 'budget-limit', 'intake-export', 'intake-collect', 'select-heldout', 'fix-history', 'fix-pairs', 'lint', 'lint-audit', 'mutate', 'score-mutants'):
        child = commands.add_parser(name)
        child.add_argument('--lean-project', type=Path, default=Path('lean'))
        child.add_argument('--timeout', type=float, default=60)
        if name == 'run':
            child.add_argument('fixture', type=Path)
            child.add_argument('--theorem')
        elif name == 'check':
            child.add_argument('--item', type=Path, required=True)
            child.add_argument('--claim', type=Path, required=True)
            child.add_argument('--proof', type=Path, required=True)
            child.add_argument('--polarity', choices=['confirm', 'refute'], default='confirm')
            child.add_argument('--output', type=Path, default=Path('.yamalemma/check'))
        elif name == 'ingest':
            child.add_argument('source', type=Path)
            child.add_argument('--informal', type=Path)
            child.add_argument('--benchmark-commit')
            child.add_argument('--selection', type=Path)
            child.add_argument('--benchmark-answers', action='store_true')
            child.add_argument('--output', type=Path, default=Path('.yamalemma/items.json'))
        elif name == 'lint':
            child.add_argument('items', type=Path)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'lint-audit':
            child.add_argument('items', type=Path)
            child.add_argument('--config', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
            child.add_argument('--item-id')
            child.add_argument('--elaborate-only', action='store_true')
            child.add_argument('--offline', action='store_true')
        elif name == 'precheck':
            child.add_argument('items', type=Path)
            child.add_argument('--output', type=Path, default=Path('.yamalemma/prechecks.json'))
        elif name == 'demo':
            child.add_argument('--output', type=Path, default=Path('.yamalemma/demo'))
        elif name == 'replay':
            child.add_argument('report', type=Path)
        elif name in ('audit', 'evaluate'):
            child.add_argument('items', type=Path)
            child.add_argument('--config', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
            child.add_argument('--offline', action='store_true')
            if name == 'audit':
                child.add_argument('--item-id')
            else:
                child.add_argument('--protocol', type=Path, required=True)
                child.add_argument('--name', required=True)
        elif name == 'freeze':
            child.add_argument('dataset', type=Path)
            child.add_argument('--config', action='append', required=True)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'score':
            child.add_argument('protocol', type=Path)
            child.add_argument('summary', type=Path)
            child.add_argument('--name', required=True)
            child.add_argument('--config', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
            child.add_argument('--judgments', type=Path)
        elif name in ('draft', 'review-audit'):
            child.add_argument('report', type=Path)
            child.add_argument('--output', type=Path, required=True)
            if name == 'review-audit':
                child.add_argument('--reviews', type=Path, required=True)
        elif name in ('budget-init', 'budget-limit'):
            child.add_argument('--max-calls', type=int, default=3, required=name == 'budget-limit')
            child.add_argument('--max-cost-usd', type=float, default=0.25, required=name == 'budget-limit')
        elif name == 'local-model':
            child.add_argument('action', choices=('start', 'stop', 'status'))
        elif name == 'intake-export':
            child.add_argument('items', type=Path)
            child.add_argument('--split', choices=('development', 'heldout'), required=True)
            child.add_argument('--batch', required=True)
            child.add_argument('--groups', type=Path)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'select-heldout':
            child.add_argument('source', type=Path)
            child.add_argument('--development', type=Path, required=True)
            child.add_argument('--size', type=int, required=True)
            child.add_argument('--seed', required=True)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'fix-history':
            child.add_argument('source', type=Path)
            child.add_argument('--since')
        elif name == 'fix-pairs':
            child.add_argument('source', type=Path)
            child.add_argument('--since')
            child.add_argument('--exclude-selection', type=Path, action='append', default=[])
            child.add_argument('--informal', type=Path)
            child.add_argument('--benchmark-answers', action='store_true')
            child.add_argument('--output', type=Path, required=True)
        elif name == 'mutate':
            child.add_argument('source', type=Path)
            child.add_argument('--selection', type=Path, required=True)
            child.add_argument('--development', type=Path, required=True)
            child.add_argument('--exclude-selection', type=Path, action='append', default=[])
            child.add_argument('--skip-key', type=Path, action='append', default=[])
            child.add_argument('--seed', required=True)
            child.add_argument('--originals', type=int, required=True)
            child.add_argument('--informal', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'score-mutants':
            child.add_argument('key', type=Path)
            child.add_argument('--arm', action='append', default=[])
            child.add_argument('--lint', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
        elif name == 'intake-collect':
            child.add_argument('manifest', type=Path)
            child.add_argument('--responses', type=Path, required=True)
            child.add_argument('--output', type=Path, required=True)
    arguments = sys.argv[1:]
    if arguments and arguments[0] not in commands.choices and not arguments[0].startswith('-'):
        arguments = ['run'] + arguments
    args = parser.parse_args(arguments)
    try:
        if args.command == 'budget-limit':
            from yamalemma.budget import change_budget_limits
            emit(change_budget_limits(args.max_calls, args.max_cost_usd))
            return
        if args.command in ('budget-init', 'budget-status'):
            from yamalemma.budget import initialize_budget, budget_status
            emit(initialize_budget(args.max_calls, args.max_cost_usd) if args.command == 'budget-init' else budget_status())
            return
        if args.command == 'local-model':
            from yamalemma.local_model import local_model
            emit(local_model(args.action))
            return
        if args.command == 'model-info':
            import urllib.request
            emit(json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=10)))
            return
        if args.command == 'select-heldout':
            from yamalemma.selection import select_heldout, write_selection
            development = [row['name'] for row in load_json(args.development)['problems']]
            selection = select_heldout(args.source, development, args.size, args.seed)
            write_selection(selection, args.output)
            emit({'output': args.output, 'benchmark_commit': selection['benchmark_commit'], 'selected': len(selection['selected']),
                  'development_excluded': len(selection['development_excluded']), 'unknown_development_names': selection['unknown_development_names']})
            return
        if args.command == 'fix-history':
            from yamalemma.selection import fix_history
            emit(fix_history(args.source, args.since))
            return
        if args.command == 'score-mutants':
            from yamalemma.mutants import score_mutants
            arms = {}
            for value in args.arm:
                name, path = value.split('=', 1)
                arms[name] = [load_json(row['report']) for row in load_json(Path(path) / 'summary.json')]
            result = score_mutants(load_json(args.key), arms, load_json(args.lint))
            save_json(args.output, result)
            emit(result)
            return
        if args.command == 'intake-export':
            from yamalemma.intake import export_packets
            groups = load_json(args.groups) if args.groups else None
            manifest = export_packets(load_json(args.items), args.output, args.split, args.batch, groups)
            emit({'output': args.output, 'packets': len(manifest['packets']), 'excluded': manifest['excluded']})
            return
        if args.command == 'intake-collect':
            from yamalemma.intake import collect_labels, write_dataset
            rows, summary = collect_labels(load_json(args.manifest), args.manifest.parent, load_json(args.responses))
            write_dataset(rows, args.output)
            emit(dict(summary, output=args.output))
            return
        if args.command == 'draft':
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(issue_draft(load_json(args.report)))
            emit({'draft': args.output})
            return
        if args.command == 'freeze':
            from yamalemma.evaluation import freeze_protocol
            configs = {}
            for value in args.config:
                name, path = value.split('=', 1)
                if name in configs:
                    raise ValueError('duplicate evaluation configuration name')
                configs[name] = load_config(path)
            emit(freeze_protocol(load_json(args.dataset), configs, args.output))
            return
        if args.command == 'score':
            from yamalemma.evaluation import score
            reports = [load_json(row['report']) for row in load_json(args.summary)]
            result = score(load_json(args.protocol), reports, args.name, load_config(args.config),
                           load_json(args.judgments) if args.judgments else None)
            save_json(args.output, result)
            emit(result)
            return
        config = load_config(args.config) if args.command in ('audit', 'evaluate', 'lint-audit') else None
        if args.command == 'run':
            result = run_lean(args.lean_project, args.fixture, args.timeout)
            output = asdict(result)
            code = {'success': 0, 'failure': 1, 'timeout': 124, 'launch_error': 127}[result.status]
            if args.theorem:
                axioms = parse_axiom_report(result.stdout, args.theorem) if result.status == 'success' else None
                decision = assess_axioms(axioms)
                output['axiom_policy'] = asdict(decision)
                output['evidence_scope'] = 'trusted fixture diagnostic only'
                if decision.status != 'allowed' and code == 0:
                    code = 2
            emit(output)
            raise SystemExit(code)
        with LeanWorker(args.lean_project, timeout=args.timeout) as worker:
            if args.command == 'audit':
                from yamalemma.pipeline import run_audit
                items = load_json(args.items)
                if args.item_id:
                    items = [item for item in items if item['id'] == args.item_id]
                    if not items:
                        raise ValueError('requested item ID was not found')
                emit(run_audit(worker, items, config, args.output, offline=args.offline))
            elif args.command == 'evaluate':
                from yamalemma.evaluation import evaluate
                emit(evaluate(worker, load_json(args.items), load_json(args.protocol), config, args.name, args.output, offline=args.offline))
            elif args.command == 'review-audit':
                from yamalemma.pipeline import review_audit
                result = review_audit(worker, load_json(args.report), load_json(args.reviews))
                save_json(args.output, result)
                emit({'output': args.output, 'claims': len(result['claims'])})
            elif args.command == 'doctor':
                emit(worker.request({'expected': 'True', 'proof': 'by trivial'}))
            elif args.command == 'ingest':
                informal = {}
                if args.informal:
                    informal = {entry['problem_name']: entry['informal_statement'] for entry in load_json(args.informal)}
                names, commit = None, args.benchmark_commit
                if args.selection:
                    from yamalemma.selection import check_selection
                    selection = load_json(args.selection)
                    names = check_selection(selection, args.source)
                    if commit is not None and commit != selection['benchmark_commit']:
                        raise ValueError('benchmark commit differs from the selection record')
                    commit = selection['benchmark_commit']
                items = ingest_putnam(worker, args.source, informal_records=informal, benchmark_commit=commit, names=names,
                                      answers=args.benchmark_answers)
                save_json(args.output, items)
                emit({'items': len(items), 'output': args.output})
            elif args.command == 'lint':
                from yamalemma.lints import lint_item
                results = [lint_item(worker, item) for item in load_json(args.items) if 'fingerprint' in item]
                save_json(args.output, results)
                flagged = [{'item': row['item_id'], 'strength': finding['strength'],
                            'edit': (finding.get('suggested_edit') or {}).get('kind')}
                           for row in results for finding in row['findings']]
                emit({'items': len(results), 'statuses': sorted({row['status'] for row in results}),
                      'flagged': flagged, 'output': args.output})
            elif args.command == 'fix-pairs':
                from yamalemma.selection import fix_pairs, ingest_fix_pairs
                excluded = {name for path in args.exclude_selection for name in load_json(path)['selected']}
                manifest = fix_pairs(args.source, args.output, args.since, excluded)
                informal = {entry['problem_name']: entry['informal_statement'] for entry in load_json(args.informal)} if args.informal else {}
                items, rows = ingest_fix_pairs(worker, manifest, args.output, informal, args.benchmark_answers)
                save_json(args.output / 'items.json', items)
                save_json(args.output / 'status.json', rows)
                count = lambda role, status: sum(row.get(role, {}).get('status') == status for row in rows)
                emit({'pairs': len(rows), 'skipped': len(manifest['skipped']), 'fix_like': sum(row['fix_like'] for row in rows),
                      'elaborates': {role: count(role, 'elaborates') for role in ('pre_fix', 'post_fix')},
                      'both_elaborate_statement_changed': sum(row['statement_changed'] is True and all(row.get(role, {}).get('status') == 'elaborates' for role in ('pre_fix', 'post_fix')) for row in rows),
                      'output': args.output})
            elif args.command == 'mutate':
                from yamalemma.lints import lint_item
                from yamalemma.mutants import blinded_outputs, generate
                from yamalemma.selection import check_selection
                selection = load_json(args.selection)
                names = check_selection(selection, args.source)
                excluded = {row['name'] for row in load_json(args.development)['problems']}
                excluded |= {name for path in args.exclude_selection for name in load_json(path)['selected']}
                skip = {row['group'] for path in args.skip_key for row in load_json(path)}
                args.output.mkdir(parents=True, exist_ok=False)
                informal = {entry['problem_name']: entry['informal_statement'] for entry in load_json(args.informal)}
                rows, rejected, quota = generate(worker, args.source, sorted(names - excluded), args.seed, args.originals, informal,
                                                 selection['benchmark_commit'], skip=skip)
                items, key, dataset = blinded_outputs(rows, args.seed, selection['benchmark_commit'], selection['file_sha256'])
                lint = [lint_item(worker, item) for item in items]
                for name, value in (('items.json', items), ('key.json', key), ('dataset.json', dataset), ('rejected.json', rejected), ('lint.json', lint)):
                    save_json(args.output / name, value)
                buckets = {}
                for row in key:
                    if row['role'] == 'mutant':
                        buckets.setdefault(row['operator'], {}).setdefault(row['equivalence']['bucket'], 0)
                        buckets[row['operator']][row['equivalence']['bucket']] += 1
                lint_by = {record['item_fingerprint']: bool(record.get('findings')) for record in lint}
                summary = {'seed': args.seed, 'benchmark_commit': selection['benchmark_commit'], 'pool': len(names - excluded),
                           'originals': len(rows), 'mutants': len(rows), 'operators': quota, 'equivalence_by_operator': buckets,
                           'rejected_attempts': len(rejected),
                           'lint_flagged': {'originals': sum(lint_by[row['item_fingerprint']] for row in key if row['role'] == 'original'),
                                            'mutants': {operator: sum(lint_by[row['item_fingerprint']] for row in key if row['operator'] == operator) for operator in quota}},
                           'lint_statuses': sorted({record['status'] for record in lint})}
                save_json(args.output / 'summary.json', summary)
                emit(summary)
            elif args.command == 'lint-audit':
                from yamalemma.lints import run_lint_audit
                from yamalemma.models import ModelClient
                items = [item for item in load_json(args.items) if 'fingerprint' in item]
                if args.item_id:
                    items = [item for item in items if item['id'] == args.item_id]
                    if not items:
                        raise ValueError('requested item ID was not found')
                client = None if args.elaborate_only else ModelClient(config, args.output / 'models', offline=args.offline)
                emit(run_lint_audit(worker, items, config, args.output, client))
            elif args.command == 'precheck':
                results = [precheck(worker, item) for item in load_json(args.items)]
                save_json(args.output, results)
                emit({'items': len(results), 'output': args.output})
            elif args.command == 'demo':
                from yamalemma.demo import run_demo
                emit(run_demo(worker, args.lean_project.resolve().parent, args.output))
            elif args.command == 'check':
                item, claim = load_json(args.item), load_json(args.claim)
                probe = make_probe(claim, args.polarity, args.proof.read_text())
                evidence = [check_probe(worker, item, claim, probe)]
                verdict = adjudicate(claim, evidence)
                write_report(args.output, item, claim, evidence, verdict)
                emit(verdict)
                if verdict['evidence_verdict'] in ('UNRESOLVED', 'INTERNAL-ERROR'):
                    raise SystemExit(2)
            elif args.command == 'replay':
                report = load_json(args.report)
                current = environment_record(worker.project)
                if any(entry['environment']['fingerprint'] != current['fingerprint'] for entry in report['evidence']):
                    raise ValueError('replay environment differs from the recorded environment')
                evidence = [check_probe(worker, report['item'], report['claim'], entry['probe']) for entry in report['evidence']]
                verdict = adjudicate(report['claim'], evidence)
                emit(verdict)
                if verdict['evidence_verdict'] != report['adjudication']['evidence_verdict']:
                    raise ValueError('replayed verdict differs from the original report')
    except (ValueError, OSError, WorkerError, RuntimeError) as error:
        parser.exit(2, f'error: {error}\n')
