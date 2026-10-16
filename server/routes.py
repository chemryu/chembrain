from itertools import islice, product


def find_routes(target: str, molecules: list[dict], reactions: list[dict], max_steps: int, limit: int, include_drafts: bool) -> list[dict]:
    by_id = {m["id"]: m for m in molecules}
    producers: dict[str, list[dict]] = {}
    for reaction in reactions:
        if reaction["status"] != "reviewed" and not include_drafts:
            continue
        for mid in reaction["products"]:
            producers.setdefault(mid, []).append(reaction)

    expansions = 0

    def expand(mid: str, budget: int, seen: frozenset[str]):
        nonlocal expansions
        if mid in seen:
            return []
        leaf = {"molecule_id": mid, "reaction_id": None, "children": [], "steps": 0}
        options = [leaf]
        expansions += 1
        if budget == 0 or expansions > 3000:
            return options
        for reaction in producers.get(mid, []):
            if any(r in seen or r == mid for r in reaction["reactants"]):
                continue
            branches = [expand(r, budget - 1, seen | {mid}) for r in reaction["reactants"]]
            if any(not branch for branch in branches):
                continue
            for combination in islice(product(*branches), 300):
                steps = 1 + sum(c["steps"] for c in combination)
                if steps <= budget:
                    options.append({"molecule_id": mid, "reaction_id": reaction["id"], "children": list(combination), "steps": steps})
                if len(options) >= 80:
                    return options
        return options

    candidates = [node for node in expand(target, max_steps, frozenset()) if node["reaction_id"]]
    reaction_map = {r["id"]: r for r in reactions}
    for route in candidates:
        leaves: set[str] = set()
        reaction_ids: list[str] = []

        def visit(node):
            if node["reaction_id"] is None:
                leaves.add(node["molecule_id"])
            else:
                reaction_ids.append(node["reaction_id"])
                for child in node["children"]:
                    visit(child)

        visit(route)
        route["starting_materials"] = sorted(leaves)
        route["unknown_availability"] = sorted(m for m in leaves if by_id[m]["availability"] == "unknown")
        route["reaction_ids"] = reaction_ids
        route["is_demo"] = any(reaction_map[r].get("is_demo", False) for r in reaction_ids) or any(by_id[m].get("is_demo", False) for m in leaves)
        route["contains_drafts"] = any(reaction_map[r]["status"] != "reviewed" for r in reaction_ids)
    candidates.sort(key=lambda r: (len(r["unknown_availability"]), r["steps"]))
    return candidates[:limit]
