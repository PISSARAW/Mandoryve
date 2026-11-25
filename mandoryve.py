"""Comparer les droits effectifs observés avec un mandat borné dans le temps."""
import argparse
import json
from pathlib import Path


def text_id(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("identifiant invalide")
    return value


def tick(value):
    if type(value) is not int:
        raise ValueError("échéance entière requise")
    return value


def effective(snapshot, now):
    users, groups = snapshot["users"], snapshot["groups"]
    if not isinstance(users, dict) or not isinstance(groups, dict) or not isinstance(snapshot["direct"], list):
        raise ValueError("collections d’observation invalides")
    rights = {}

    def add(user, grant):
        permission = grant["permission"]
        if permission not in ("read", "write"):
            raise ValueError("permission inconnue")
        # Dans ce modèle, write inclut read. Le droit effectif expire au dernier octroi.
        for mode in (("read", "write") if permission == "write" else ("read",)):
            key = (text_id(user), text_id(grant["folder"]), mode)
            expiry = tick(grant["until"])
            if expiry > now:
                rights[key] = max(expiry, rights.get(key, expiry))

    for user, memberships in users.items():
        text_id(user)
        if not isinstance(memberships, list):
            raise ValueError("adhésions invalides")
        for group in memberships:
            if not isinstance(groups[group], list):
                raise ValueError("octrois du groupe invalides")
            for grant in groups[group]:
                add(user, grant)
    for grant in snapshot["direct"]:
        if grant["user"] not in users:
            raise ValueError("utilisateur absent")
        add(grant["user"], grant)
    return rights


def verify(case):
    now = tick(case["observed_at"])
    mandate = case["mandate"]
    expiry = tick(mandate["until"])
    people = mandate["users"]
    if not isinstance(people, list) or not people or expiry <= now:
        raise ValueError("mandat vide ou expiré")
    target = {(text_id(user), text_id(mandate["folder"]), "read") for user in people}
    try:
        before = effective(case["before"], now)
        after = effective(case["after"], now)
        if any(user not in case[stage]["users"] for stage in ("before", "after") for user in people):
            raise ValueError("sujet du mandat absent de l’observation")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        return {"status": "unverifiable", "reason": f"observation incomplète ou invalide ({exc})"}
    # Ajouter un mandat ne doit ni raccourcir un droit antérieur ni en créer ailleurs.
    expected = before.copy()
    for key in target:
        expected[key] = max(expiry, before.get(key, expiry))
    differences = []
    for key in sorted(expected.keys() | after.keys()):
        if expected.get(key) != after.get(key):
            differences.append({"user": key[0], "folder": key[1], "permission": key[2],
                                "expected_until": expected.get(key), "observed_until": after.get(key)})
    return {"status": "deviation" if differences else "conformant", "differences": differences}


def evidence(case, report, case_id, uncertainty):
    text_id(case_id)
    if uncertainty < 0:
        raise ValueError("incertitude négative")
    rows = []
    for difference in report.get("differences", []):
        rows.append({"kind": "access", "subject": {k: difference[k] for k in ("user", "folder", "permission")},
                     "facts": {"expected": difference["expected_until"], "observed": difference["observed_until"]}})
    if not rows:
        # Une vérification complète sans écart et une observation indisponible ont des sens distincts.
        kind = "verified" if report["status"] == "conformant" else "unavailable"
        rows.append({"kind": kind, "facts": {}})
    for i, row in enumerate(rows, 1):
        row.update(id=f"mandoryve-{i}", time_s=case["observed_at"], uncertainty_s=uncertainty)
    return {"schema": "evidence.v1", "source": "mandoryve", "case_id": case_id, "events": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--evidence", metavar="CASE_ID", help="exporter les observations evidence.v1")
    parser.add_argument("--uncertainty-s", type=int, default=0)
    args = parser.parse_args()
    try:
        case = json.loads(args.case.read_text())
        report = verify(case)
        if args.evidence is not None:
            print(json.dumps(evidence(case, report, args.evidence, args.uncertainty_s), ensure_ascii=False))
            raise SystemExit(0)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Mandat invalide ({exc})\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit({"conformant": 0, "deviation": 1, "unverifiable": 2}[report["status"]])
