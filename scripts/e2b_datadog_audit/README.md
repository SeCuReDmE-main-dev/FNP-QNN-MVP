# E2B Datadog Sandbox Auditor

Ce module fournit un agent local pour auditer automatiquement une sandbox E2B et
émettre un log Datadog structuré, avec priorité au SDK officiel Datadog (fallback HTTP si nécessaire).

## Structure

- `audit_e2b.py` : script principal (audit + emission Datadog)
- `requirements.txt` : dépendances optionnelles pour ce module
- `README.md` : ce document

## Installation

```bash
cd "C:\\Users\\jeans\\Desktop\\Case study\\modele\\simulateur de bacterie\\FNP-QNN-MVP-version-desise-simulator-\\scripts\\e2b_datadog_audit"
python -m pip install -r requirements.txt
```

## Variables d’environnement

Les variables suivantes peuvent être définies avant lancement :

- `E2B_API_KEY` : token API E2B (requis)
- `DATADOG_API_KEY` : token API Datadog pour l’ingestion de logs
- `DATADOG_SITE` : site Datadog (défaut `datadoghq.com`)
- `DD_ENV` : tag d’environnement Datadog (défaut `local`)
- `E2B_TEMPLATE_ID` : template E2B (défaut `python`)

Les variables sensibles (clés, tokens, secrets) présentes dans la sortie d’environnement
sont masquées dans le payload Datadog. Vous pouvez désactiver la redaction locale
avec `--skip-sensitive-redaction` si vous auditez uniquement en environnement
strictement fermé.

## Utilisation basique

```bash
cd "C:\\Users\\jeans\\Desktop\\Case study\\modele\\simulateur de bacterie\\FNP-QNN-MVP-version-desise-simulator-\\scripts\\e2b_datadog_audit"
python audit_e2b.py
```

Options utiles :

- `--template-id` : template E2B à utiliser
- `--e2b-timeout` : timeout par commande sandbox (s)
- `--timeout` : timeout global audit (s)
- `--service` : nom Datadog service (défaut `e2b-vm-auditor`)
- `--dd-env` : tag d’environnement Datadog
- `--datadog-site` : site datadog (ex. `datadoghq.com`, `us3.datadoghq.com`)
- `--no-datadog` : exécute uniquement local, n’envoie pas de log
- `--skip-sensitive-redaction` : ne pas masquer les valeurs d’environnement

### Exemple complet

```bash
set E2B_API_KEY=xxx
set DATADOG_API_KEY=xxx
python audit_e2b.py --template-id py --e2b-timeout 120 --service e2b-vm-auditor --dd-env ci
```

La sortie standard contient un JSON résumé :
- status global (`pass` / `fail`)
- le résultat de chaque commande
- l’`sandbox_id` (si disponible dans le SDK E2B utilisé)

Quand Datadog est disponible, le script tente d’abord l’envoi via `datadog-api-client`
et bascule sur l’API HTTP d’ingestion en secours si la librairie Python n’est pas importable.

## Intégration Datadog Workflow / Cron

Intégrer ce script dans un workflow Datadog (ou toute orchestration CI) avec une
exécution périodique ; le script retourne :
- `0` si audit OK et log Datadog accepté (le cas échéant)
- `1` si échec d’au moins une vérification
- `2` si configuration invalide (clé manquante)

### Requête de monitor (exemple)

Créer un monitor "log" avec la requête :

```text
status:error service:e2b-vm-auditor
```

ou filtrer par environnement:

```text
status:error service:e2b-vm-auditor @audit.tags.env:ci
```

## Limites connues

- Le SDK E2B n’a pas une API stabilisée public/privée unique selon versions.
  Le script essaie plusieurs signatures (`create`, `run_code`, `run`) et retombe en
  erreur claire si l’interface installée n’est pas compatible.
- Le script attend `dpkg`, `ss` ou `netstat` selon disponibilité de l’image sandbox.
- Les résultats sont structurés pour audit local ; les valeurs de secrets sont redacted.

## Sécurité

- Le script évite toute persistance de données.
- La sandbox est supprimée via le mécanisme de sortie `with` et/ou `close`.
- Les secrets (`E2B_API_KEY`, `DATADOG_API_KEY`) ne sont jamais sérialisés dans les logs.
