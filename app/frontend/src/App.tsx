import { useEffect, useState } from "react";
import { createJob, getJobStatus, getResult, saveEdits, pickFile } from "./api/client";
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
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timer: number | undefined;
    if (jobId && status !== "completed" && status !== "failed") {
      timer = window.setInterval(async () => {
        try {
          const data = await getJobStatus(jobId);
          setStatus(data.status);
          setProgress(data.progress);
          setLogs(data.logs);
          if (data.status === "completed") {
            const jobResult = await getResult(jobId);
            setResult(jobResult);
          }
        } catch (e) {
          console.error("Error polling status:", e);
        }
      }, 1500);
    }
    return () => {
      if (timer) {
        window.clearInterval(timer);
      }
    };
  }, [jobId, status]);

  const handlePickFile = async () => {
    try {
      setError(null);
      const { path } = await pickFile();
      if (path) {
        setVideoPath(path);
      }
    } catch (error) {
      console.error("Error picking file:", error);
      setError("Error al abrir el explorador de archivos. Asegúrate de que el backend esté corriendo.");
    }
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      const response = await createJob({
        video_path: videoPath,
        language,
        num_speakers: numSpeakers ? Number(numSpeakers) : undefined,
        verify: false,
      });
      setJobId(response.job_id);
      setStatus("queued");
      setResult(null);
    } catch (err) {
      console.error(err);
      setError("Error al iniciar el análisis. Verifica que el backend esté conectado.");
    }
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
    <div className="relative min-h-screen bg-slate-950 overflow-hidden font-sans text-slate-200 selection:bg-purple-500/30">
      {/* Gradient Mesh Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 -left-40 w-[500px] h-[500px] bg-purple-600 rounded-full blur-[128px] opacity-20 animate-blob"></div>
        <div className="absolute top-0 -right-40 w-[400px] h-[400px] bg-pink-600 rounded-full blur-[128px] opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-blue-600 rounded-full blur-[128px] opacity-20 animate-blob animation-delay-4000"></div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]"></div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-12">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400 mb-4 tracking-tight">
            FastCheck Local
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Análisis local de video con speakers, transcript y claims verificables.
          </p>
        </header>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 mb-8 text-red-200 flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 shrink-0">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
            <p>{error}</p>
          </div>
        )}

        <section className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
            <span className="w-1 h-6 bg-purple-500 rounded-full"></span>
            Nuevo análisis
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6">
            <label className="lg:col-span-6 block">
              <span className="block text-sm font-medium text-slate-400 mb-2">Ruta del video</span>
              <div className="flex gap-2">
                <input
                  className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all shadow-inner"
                  value={videoPath}
                  onChange={(event) => setVideoPath(event.target.value)}
                  placeholder="/ruta/al/video.mp4"
                />
                <button
                  onClick={handlePickFile}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-xl transition-colors shrink-0 flex items-center gap-2 border border-slate-700/50"
                  title="Abrir explorador"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                  </svg>
                  <span className="hidden sm:inline">Buscar</span>
                </button>
              </div>
            </label>
            <label className="lg:col-span-3 block">
              <span className="block text-sm font-medium text-slate-400 mb-2">Idioma</span>
              <select
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all shadow-inner appearance-none cursor-pointer"
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
              >
                <option value="auto">Auto</option>
                <option value="es">Español</option>
                <option value="en">English</option>
              </select>
            </label>
            <label className="lg:col-span-3 block">
              <span className="block text-sm font-medium text-slate-400 mb-2">Nº speakers</span>
              <input
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all shadow-inner"
                value={numSpeakers}
                onChange={(event) => setNumSpeakers(event.target.value)}
                placeholder="Auto (2-4)"
              />
            </label>
            <div className="lg:col-span-12 flex justify-end mt-2">
              <button
                onClick={handleSubmit}
                disabled={!videoPath}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold py-3 px-8 rounded-full shadow-lg shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
              >
                Iniciar Análisis
              </button>
            </div>
          </div>
        </section>

        {jobId && (
          <section className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
              Progreso
            </h2>
            <div className="w-full bg-slate-800/50 rounded-full h-3 mb-4 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.round(progress * 100)}%` }}
              />
            </div>
            <div className="flex justify-between items-center text-sm mb-4">
              <p className="text-slate-300">
                Estado: <span className="font-semibold text-white capitalize">{status}</span>
              </p>
              <span className="text-slate-400">{Math.round(progress * 100)}%</span>
            </div>
            <div className="bg-slate-950/50 rounded-xl p-4 max-h-48 overflow-y-auto border border-slate-800/50 font-mono text-xs text-slate-400">
              <ul className="space-y-1">
                {logs.map((log, idx) => (
                  <li key={idx} className="border-l-2 border-slate-700 pl-2">{log}</li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {result && (
          <section className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl animate-in fade-in slide-in-from-bottom-8 duration-700">
            <h2 className="text-2xl font-semibold text-white mb-8 flex items-center gap-2">
              <span className="w-1 h-6 bg-green-500 rounded-full"></span>
              Resultados
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

              {/* Speakers Column */}
              <div className="lg:col-span-1 space-y-6">
                <div className="bg-slate-900/30 rounded-xl p-6 border border-white/5">
                  <h3 className="text-lg font-medium text-white mb-4">Speakers Detectados</h3>
                  <div className="space-y-3">
                    {speakers.map((speaker) => (
                      <div key={speaker} className="group">
                        <div className="flex flex-col gap-1">
                          <span className="text-xs text-slate-500 uppercase tracking-wider font-bold">Original: {speaker}</span>
                          <input
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:ring-1 focus:ring-green-500/50 transition-all"
                            placeholder="Renombrar..."
                            defaultValue={speaker} /* Using defaultValue allows editing, though controlled logic is in onBlur */
                            onBlur={(event) => handleRename(speaker, event.target.value)}
                          />
                        </div>
                      </div>
                    ))}
                    {!speakers.length && <p className="text-slate-500 text-sm italic">No speakers found yet.</p>}
                  </div>
                </div>

                <div className="bg-slate-900/30 rounded-xl p-6 border border-white/5">
                  <h3 className="text-lg font-medium text-white mb-4">Filtrar Transcript</h3>
                  <select
                    className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:ring-1 focus:ring-green-500/50 transition-all appearance-none cursor-pointer"
                    value={selectedSpeaker}
                    onChange={(event) => setSelectedSpeaker(event.target.value)}
                  >
                    <option value="">Mostrar Todo</option>
                    {speakers.map((speaker) => (
                      <option key={speaker} value={speaker}>
                        {speaker}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Transcript Column */}
              <div className="lg:col-span-2">
                <h3 className="text-lg font-medium text-white mb-4">Transcripción</h3>
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                  {result.transcript.segments
                    .filter((segment) => !selectedSpeaker || segment.speaker === selectedSpeaker)
                    .map((segment, idx) => (
                      <div key={`${segment.start}-${idx}`} className="group relative bg-slate-900/40 hover:bg-slate-900/60 border border-white/5 rounded-xl p-5 transition-all">
                        <div className="flex justify-between items-start mb-2">
                          <strong className="text-sm text-purple-400 font-bold tracking-wide">{segment.speaker}</strong>
                          <span className="text-xs text-slate-500 font-mono">
                            {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                          </span>
                        </div>
                        <p className="text-slate-300 leading-relaxed mb-3">{segment.text}</p>

                        <div className="flex justify-end opacity-50 group-hover:opacity-100 transition-opacity">
                          <select
                            className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-400 focus:text-white focus:border-purple-500 outline-none cursor-pointer"
                            onChange={(event) => handleAssign(segment, event.target.value)}
                            value="" // Always reset to prompt
                          >
                            <option value="" disabled>Reasignar a...</option>
                            {speakers.map((speaker) => (
                              <option key={speaker} value={speaker}>
                                {speaker}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

            </div>

            {/* Claims Section */}
            <div className="mt-8 pt-8 border-t border-white/5">
              <h3 className="text-lg font-medium text-white mb-6">Claims Verificables</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.claims.map((claim) => (
                  <div key={claim.id} className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border-l-4 border-l-blue-500 border-y border-r border-y-white/5 border-r-white/5 rounded-r-xl p-5 hover:border-l-blue-400 transition-all">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-blue-400 uppercase">{claim.speaker}</span>
                      <span className="text-xs text-slate-500 font-mono">{claim.start.toFixed(1)}s</span>
                    </div>
                    <p className="text-slate-200 text-sm leading-relaxed">"{claim.text}"</p>
                  </div>
                ))}
                {!result.claims.length && (
                  <div className="col-span-full text-center py-8 text-slate-500 border border-dashed border-slate-800 rounded-xl">
                    No se detectaron claims verificables en este video.
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
