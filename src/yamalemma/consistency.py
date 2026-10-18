from yamalemma.prompts import declared_edit_kind


EDIT_RANK = {'regrouping': 0, 'reordering': 0, 'binder_move': 0, None: 1, 'rewrite': 2}


def separation_kind(item, candidate):
    return declared_edit_kind(item, candidate)


def agrees(first, second):
    return first['type'] == second['type'] or first['location'] == second['location']


def cluster_samples(item, samples):
    members = [(sample, index, candidate) for sample, claims in enumerate(samples) for index, candidate in enumerate(claims)]
    parent = list(range(len(members)))

    def root(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for left in range(len(members)):
        for right in range(left + 1, len(members)):
            if members[left][0] != members[right][0] and agrees(members[left][2], members[right][2]):
                parent[root(left)] = root(right)
    groups = {}
    for node in range(len(members)):
        groups.setdefault(root(node), []).append(node)
    majority = len(samples) // 2 + 1
    clusters = []
    for nodes in sorted(groups.values()):
        rows = [members[node] for node in nodes]
        support = len({sample for sample, _, _ in rows})
        ranked = sorted(rows, key=lambda row: (EDIT_RANK[separation_kind(item, row[2])], row[0], row[1]))
        sample, index, chosen = ranked[0]
        clusters.append({'support': support, 'kept': support >= majority, 'representative': [sample, index],
                         'representative_edit_kind': separation_kind(item, chosen),
                         'members': [{'sample': row[0], 'index': row[1], 'type': row[2]['type'], 'location': row[2]['location'],
                                      'probe_kind': row[2]['probe_kind'], 'edit_kind': separation_kind(item, row[2])} for row in rows],
                         'candidate': chosen})
    clusters.sort(key=lambda cluster: (-cluster['support'], EDIT_RANK[cluster['representative_edit_kind']], cluster['representative']))
    return clusters


def consistency_summary(item, samples, statuses):
    clusters = cluster_samples(item, samples)
    flagged = sum(bool(claims) for claims in samples)
    completed = sum(status == 'completed' for status in statuses)
    summary = {'samples': len(samples), 'completed_samples': completed, 'samples_with_claims': flagged,
               'item_agreement': flagged in (0, len(samples)) and completed == len(samples),
               'clusters': [{key: value for key, value in cluster.items() if key != 'candidate'} for cluster in clusters],
               'kept_clusters': sum(cluster['kept'] for cluster in clusters),
               'cluster_agreement_rate': sum(cluster['kept'] for cluster in clusters) / len(clusters) if clusters else None,
               'rule': 'a cluster joins claims from different samples with the same type or location; it is kept when a majority of samples contribute; '
                       'its representative prefers regrouping or reordering separations, then other probes, then rewrites'}
    return [cluster['candidate'] for cluster in clusters if cluster['kept']], summary
