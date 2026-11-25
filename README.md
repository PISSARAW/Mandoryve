# Mandoryve
Un utilisateur demande à un agent : « Donne à ces deux prestataires un accès en lecture à ce dossier jusqu’à vendredi. » Chaque appel d’API peut être autorisé individuellement. Pourtant, si l’agent choisit d’ajouter les prestataires à un groupe qui donne aussi accès à d’autres dossiers, il dépasse le mandat.

Le vérificateur Python reçoit un mandat de lecture et deux instantanés de l’application documentaire. Il calcule les droits directs et hérités, puis compare l’état attendu aux effets observés.

## Démarrage

Depuis la racine du dépôt avec Python 3.10 ou ultérieur et Make :

```sh
make demo
make test
```

Commande directe :

```sh
python3 -m mandoryve examples/group.json
```

Les deux prestataires obtiennent le dossier demandé. L’appartenance au groupe `support` donne aussi à `lea` le dossier `interne`. La démo attend cet écart et l’affiche.

Codes de sortie : 0 conforme, 1 écart, 2 observation inexploitable ou entrée invalide.

## Organisation

- `mandoryve.py` contient le moteur et son interface en ligne de commande.
- `examples/` contient les entrées fictives et reproductibles.
- `tests/` couvre le comportement nominal et les cas limites.

## Périmètre du socle

Les instants sont des entiers sur la même échelle. Les droits expirent à la borne indiquée. Les instantanés sont fournis par le scénario et supposés exhaustifs. Ce contrôle hors ligne ne détermine pas l’auteur d’un changement concurrent. Un état structurellement incomplet peut produire `unverifiable`.

## Premier chantier à reprendre

Écrire un adaptateur de relecture indépendante sur une application de démonstration. Introduire une modification concurrente et conserver les identifiants de révision pour distinguer différence d’état et attribution.

## Publier les observations d’accès

Le lot privé `evidence.v1` expose les droits attendus et observés pour chaque écart. Un contrôle conforme ou inexploitable donne une observation de synthèse distincte. Le champ `observed_at` du dossier et l’heure utilisée par Revaskel doivent partager la même origine.

```sh
python3 -m mandoryve examples/group.json --evidence exercice-01 --uncertainty-s 1 > droits.json
```

L’exercice complet se lance avec `make demo-suite` depuis [Horvessane](https://github.com/PISSARAW/Horvessane).
