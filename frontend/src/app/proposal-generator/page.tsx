"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { generateProposal, ProposalResponse } from "@/lib/api";

const PROJECT_TYPES = [
  "Office CCTV Installation",
  "Warehouse Surveillance",
  "Retail Store Security",
  "Parking Area Monitoring",
  "Residential Security",
  "School/University Campus",
  "Factory/Industrial Area",
  "Other",
];

const RESOLUTIONS = ["2MP", "3MP", "4MP", "5MP", "8MP"];

export default function ProposalGeneratorPage() {
  const [clientName, setClientName] = useState("");
  const [projectType, setProjectType] = useState("");
  const [location, setLocation] = useState("");
  const [cameraCount, setCameraCount] = useState(4);
  const [resolution, setResolution] = useState("4MP");
  const [recordingDays, setRecordingDays] = useState(30);
  const [requirementsText, setRequirementsText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ProposalResponse | null>(null);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!clientName.trim() || !projectType.trim()) {
      setError("Nama klien dan tipe proyek wajib diisi.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await generateProposal({
        client_name: clientName,
        project_type: projectType,
        location,
        camera_count: cameraCount,
        resolution,
        recording_days: recordingDays,
        requirements_text: requirementsText,
        selected_products: [],
      });
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Gagal menghasilkan proposal."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Proposal Generator</h1>
        <p className="text-base-content/60">
          Generate professional CCTV project proposals
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Client & Project Data</h2>

            <label className="form-control w-full">
              <span className="label-text">Client Name *</span>
              <input
                type="text"
                className="input input-bordered w-full"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="PT. Contoh Security"
              />
            </label>

            <label className="form-control w-full">
              <span className="label-text">Project Type *</span>
              <select
                className="select select-bordered w-full"
                value={projectType}
                onChange={(e) => setProjectType(e.target.value)}
              >
                <option value="">Select project type...</option>
                {PROJECT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>

            <label className="form-control w-full">
              <span className="label-text">Location</span>
              <input
                type="text"
                className="input input-bordered w-full"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Jakarta, Indonesia"
              />
            </label>

            <div className="grid grid-cols-2 gap-4">
              <label className="form-control w-full">
                <span className="label-text">Camera Count</span>
                <input
                  type="number"
                  className="input input-bordered w-full"
                  min={1}
                  max={256}
                  value={cameraCount}
                  onChange={(e) => setCameraCount(Number(e.target.value))}
                />
              </label>

              <label className="form-control w-full">
                <span className="label-text">Resolution</span>
                <select
                  className="select select-bordered w-full"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                >
                  {RESOLUTIONS.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="form-control w-full">
              <span className="label-text">Recording Days</span>
              <input
                type="number"
                className="input input-bordered w-full"
                min={1}
                max={365}
                value={recordingDays}
                onChange={(e) => setRecordingDays(Number(e.target.value))}
              />
            </label>

            <label className="form-control w-full">
              <span className="label-text">Additional Requirements</span>
              <textarea
                className="textarea textarea-bordered w-full h-24"
                value={requirementsText}
                onChange={(e) => setRequirementsText(e.target.value)}
                placeholder="e.g. Night vision required, IP66 rated, remote access via mobile app"
              />
            </label>

            {error && (
              <div className="alert alert-error">
                <span>{error}</span>
              </div>
            )}

            <button
              className="btn btn-primary w-full mt-2"
              onClick={handleGenerate}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="loading loading-spinner" />
                  Generating...
                </>
              ) : (
                "Generate Proposal"
              )}
            </button>
          </div>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Proposal Preview</h2>

            {result ? (
              <div className="overflow-y-auto max-h-[70vh]">
                {result.storage_summary && (
                  <div className="grid grid-cols-2 gap-2 mb-4 p-3 bg-base-200 rounded-box">
                    <div className="stat p-1 min-h-0">
                      <div className="stat-title text-xs">Storage/Day</div>
                      <div className="stat-value text-lg">
                        {String(result.storage_summary.daily_storage_gb)} GB
                      </div>
                    </div>
                    <div className="stat p-1 min-h-0">
                      <div className="stat-title text-xs">Recommended HDD</div>
                      <div className="stat-value text-lg">
                        {String(result.storage_summary.recommended_hdd_tb)} TB
                      </div>
                    </div>
                  </div>
                )}

                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      table: ({ children }) => (
                        <div className="overflow-x-auto">
                          <table className="table table-sm table-zebra">
                            {children}
                          </table>
                        </div>
                      ),
                    }}
                  >
                    {result.proposal_markdown}
                  </ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-base-content/40">
                <div className="text-center">
                  <p className="text-4xl mb-2">📄</p>
                  <p>Fill the form and generate a proposal</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
