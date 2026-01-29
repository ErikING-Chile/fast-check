import { useEffect, useState } from "react";
import { createJob, getJobStatus, getResult, saveEdits } from "./api/client";
import type { JobResult, Segment } from "./types/models";
import "./app.css";

export default function App() {
  const [videoPath, setVideoPath] = useState("");
  const [language, setLanguage] = useState("auto");
  const [numSpeakers, setNumSpeakers] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [result, setResult] = useState<JobResult | null>(null);
  const [selectedSpeaker, setSelectedSpeaker] = useState<string>("");

  useEffect(() => {
    let timer: number | undefined;
    if (jobId && status !== "completed" && status !== "failed") {
      timer = window.setInterval(async () => {
        const data = await getJobStatus(jobId);
        setStatus(data.status);
        setProgress(data.progress);
        setLogs(data.logs);
        if (data.status === "completed") {
          const jobResult = await getResult(jobId);
          setResult(jobResult);
        }
      }, 1500);
    }
    return () => {
      if (timer) {
        window.clearInterval(timer);
      }
    };
  }, [jobId, status]);

  const handleSubmit = async () => {
    const response = await createJob({
      video_path: videoPath,
      language,
      num_speakers: numSpeakers ? Number(numSpeakers) : undefined,
      verify: false,
    });
    setJobId(response.job_id);
    setStatus("queued");
    setResult(null);
  };

  const speakers = result
    ? Array.from(new Set(result.transcript.segments.map((segment) => segment.speaker)))
    : [];

  const handleRename = async (speaker: string, newName: string) => {
    if (!jobId) return;
    await saveEdits(jobId, [{ action: "rename", old: speaker, new: newName }]);
    const updated = await getResult(jobId);
    setResult(updated);
  };

  const handleAssign = async (segment: Segment, speaker: string) => {
    if (!jobId) return;
    await saveEdits(jobId, [
      { action: "assign", start: segment.start, end: segment.end, speaker },
    ]);
    const updated = await getResult(jobId);
    setResult(updated);
  };

  return (
    <div className="app">
      <header>
        <h1>FastCheck Local</h1>
        <p>
          Análisis local de video con speakers, transcript y claims verificables.
        </p>
      </header>

      <section className="card">
        <h2>Nuevo análisis</h2>
        <div className="form-grid">
          <label>
            Ruta del video
            <input
              value={videoPath}
              onChange={(event) => setVideoPath(event.target.value)}
              placeholder="/ruta/al/video.mp4"
            />
          </label>
          <label>
            Idioma
            <select value={language} onChange={(event) => setLanguage(event.target.value)}>
              <option value="auto">Auto</option>
              <option value="es">Español</option>
              <option value="en">English</option>
            </select>
          </label>
          <label>
            Nº speakers (2-4)
            <input
              value={numSpeakers}
              onChange={(event) => setNumSpeakers(event.target.value)}
              placeholder="auto"
            />
          </label>
          <button onClick={handleSubmit} disabled={!videoPath}>
            Iniciar
          </button>
        </div>
      </section>

      {jobId && (
        <section className="card">
          <h2>Progreso</h2>
          <div className="progress">
            <div className="bar" style={{ width: `${Math.round(progress * 100)}%` }} />
          </div>
          <p>Estado: {status}</p>
          <ul>
            {logs.map((log, idx) => (
              <li key={idx}>{log}</li>
            ))}
          </ul>
        </section>
      )}

      {result && (
        <section className="card">
          <h2>Resultados</h2>
          <div className="grid">
            <div>
              <h3>Speakers</h3>
              {speakers.map((speaker) => (
                <div key={speaker} className="speaker-row">
                  <span>{speaker}</span>
                  <input
                    placeholder="Renombrar"
                    onBlur={(event) => handleRename(speaker, event.target.value)}
                  />
                </div>
              ))}
            </div>
            <div>
              <h3>Transcript</h3>
              <select
                value={selectedSpeaker}
                onChange={(event) => setSelectedSpeaker(event.target.value)}
              >
                <option value="">Todos</option>
                {speakers.map((speaker) => (
                  <option key={speaker} value={speaker}>
                    {speaker}
                  </option>
                ))}
              </select>
              <div className="transcript">
                {result.transcript.segments
                  .filter((segment) => !selectedSpeaker || segment.speaker === selectedSpeaker)
                  .map((segment, idx) => (
                    <div key={`${segment.start}-${idx}`} className="segment">
                      <div className="segment-meta">
                        <strong>{segment.speaker}</strong>
                        <span>
                          {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                        </span>
                      </div>
                      <p>{segment.text}</p>
                      <select
                        onChange={(event) => handleAssign(segment, event.target.value)}
                        defaultValue=""
                      >
                        <option value="">Asignar speaker</option>
                        {speakers.map((speaker) => (
                          <option key={speaker} value={speaker}>
                            {speaker}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
              </div>
            </div>
            <div>
              <h3>Claims</h3>
              <div className="claims">
                {result.claims.map((claim) => (
                  <div key={claim.id} className="claim-card">
                    <span>
                      {claim.start.toFixed(1)}s · {claim.speaker}
                    </span>
                    <p>{claim.text}</p>
                  </div>
                ))}
                {!result.claims.length && <p>No se detectaron claims.</p>}
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
