# FastCheck Local (MVP v0.1)

FastCheck Local es un sistema local-first para analizar videos descargados, identificar 2–4 hablantes, transcribir, extraer claims verificables y contrastarlos con fuentes offline (packs) o snapshots web controlados. Todo corre en CPU y localmente.

## Prerrequisitos

- **Python 3.10+**
- **Node 18+**
- **ffmpeg** (necesario para extraer audio)

## Setup backend

```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup frontend

```bash
cd app/frontend
npm install
```

## Ejecutar local (dos comandos)

En una terminal:

```bash
cd app/backend
uvicorn main:app --reload
```

En otra terminal:

```bash
cd app/frontend
npm run dev
```

La UI queda en `http://localhost:5173` y el backend en `http://localhost:8000`.

## Indexar packs + snapshots

1. Coloca fuentes en `app/packs/{pack_name}/` (PDF/HTML/TXT/MD).
2. Indexa el pack:

```bash
curl -X POST http://localhost:8000/api/packs/index \
  -H "Content-Type: application/json" \
  -d '{"pack_name": "mi_pack"}'
```

3. (Opcional) snapshot web con allowlist en `core/settings.py`:

```bash
curl -X POST http://localhost:8000/api/packs/snapshot \
  -H "Content-Type: application/json" \
  -d '{"pack_name": "mi_pack", "url": "https://example.com"}'
```

## Export

- `GET /api/jobs/{job_id}/export/json`
- `GET /api/jobs/{job_id}/export/csv`
- `GET /api/jobs/{job_id}/export/srt`
- `GET /api/jobs/{job_id}/export/vtt`

## Limitaciones conocidas

- Diarización y ASR requieren dependencias opcionales (`pyannote.audio`, `faster-whisper`), si no están instaladas se usa un fallback básico.
- Overlap de voces y ruido afectan el merge.
- Verificación es básica y depende de los packs cargados.
