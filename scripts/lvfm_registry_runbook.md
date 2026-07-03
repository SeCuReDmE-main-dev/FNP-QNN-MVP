# LVFM Registry Window-Key Runbook

Objectif: valider le mécanisme `window key + registry snapshot + score T-I-dF` sans passer par le UI.

## 1) Installer le launcher au démarrage (local)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\setup-lvfm-registry-boot.ps1" `
  -RepoRoot "C:\Users\jeans\Desktop\Case study\modele\fnp-qnn\FNP-QNN-MVP-version-disease-simulator-" `
  -CreateStartupLink `
  -WriteRunKey `
  -PublishRegistry `
  -RegistryThreshold -0.1
```

Effets :
- copie `scripts\lvfm_bootstrap_window.cmd` dans Startup (si `-CreateStartupLink`)
- écrit `HKCU:\Software\SeCuReDmE\LVFM\Launcher`
- écrit `HKCU:\Software\Microsoft\Windows\CurrentVersion\Run\SeCuReDmE-LVFM-Bootstrap` si `-WriteRunKey`

## 2) Exécuter un bootstrap one-shot (API locale)

```powershell
python .\scripts\lvfm_windows_bootstrap.py --api-base http://127.0.0.1:8000 --publish-registry --registry-threshold -0.1 --run-once
```

Lignes attendues :
- `[SeCuReDmE LVFM] trace=T=...|I=...|dF=...|F=...`
- `gate_id` non vide
- `register_keys=...`

## 3) Lire le snapshot du registre (humain)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\read-lvfm-registry-window.ps1"
```

Valeurs critiques :
- `TiDfRaw`, `LockScore`, `TraceLine`
- `BitTableJsonLen`, `RegistryPayloadJsonLen`

## 4) Lire le snapshot en JSON (automatisation)

```powershell
$raw = powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\read-lvfm-registry-window.ps1" -AsJson
$state = $raw | ConvertFrom-Json
$state.gate.gate_id
```

## 5) Audit coût par bit (friction / "coût idée")

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\lvfm_bit_cost_audit.ps1"
```

Sortie :
- `total_cost`
- coût trié par nœud (`node_id`, `cost`, `tiDf`, `metadata`)
- statut Run-key (`run_key_present`)

## 6) Vérification continue

Après chaque boot ou changement :
- relancer le bootstrap
- relire `read-lvfm-registry-window.ps1 -AsJson`
- relancer `lvfm_bit_cost_audit.ps1 -AsJson` pour tracking historique
