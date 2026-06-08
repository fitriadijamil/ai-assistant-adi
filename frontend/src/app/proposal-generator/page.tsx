"use client";

import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { generateProposal, ProposalResponse } from "@/lib/api";
import BomTable from "@/components/BomTable";
import SuratPenawaran from "@/components/SuratPenawaran";
import { useBusinessConfig } from "@/lib/useBusinessConfig";

export default function ProposalGeneratorPage() {
  const { config, loading: configLoading } = useBusinessConfig();
  const previewRef = useRef<HTMLDivElement>(null);
  const [clientName, setClientName] = useState("");
  const [projectType, setProjectType] = useState("");
  const [location, setLocation] = useState("");
  const [cameraCountIndoor, setCameraCountIndoor] = useState(2);
  const [cameraCountOutdoor, setCameraCountOutdoor] = useState(2);
  const [resolution, setResolution] = useState("4MP");
  const [systemType, setSystemType] = useState("ip");
  const [recordingType, setRecordingType] = useState("full");
  const [brand, setBrand] = useState("");
  const [kabelUtpQty, setKabelUtpQty] = useState(0);
  const [kabelPowerQty, setKabelPowerQty] = useState(0);
  const [kabelCoaxialQty, setKabelCoaxialQty] = useState(0);
  const [usePipa, setUsePipa] = useState(true);
  const [sdCardSize, setSdCardSize] = useState("");
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
      const totalCameras = cameraCountIndoor + cameraCountOutdoor;
      if (totalCameras < 1) {
        setError("Minimal 1 kamera (indoor atau outdoor).");
        setIsLoading(false);
        return;
      }
      const selPt = projectTypes.find((pt) => pt.id === projectType);
      const projectTypeLabel = selPt?.label || projectType;
      const data = await generateProposal({
        client_name: clientName,
        project_type: projectTypeLabel,
        location,
        camera_count_indoor: cameraCountIndoor,
        camera_count_outdoor: cameraCountOutdoor,
        resolution,
        system_type: systemType,
        recording_type: recordingType,
        recording_days: 30,
        selected_products: [],
        brand: brand,
        kabel_utp_qty: kabelUtpQty || 0,
        kabel_power_qty: kabelPowerQty || 0,
        kabel_coaxial_qty: kabelCoaxialQty || 0,
        use_pipa: usePipa,
        customer_attention: clientName,
        customer_address: location,
        sd_card_size: sdCardSize,
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

  const handleDownloadPDF = () => {
    window.print();
  };

  const projectTypes = config?.project_types || [];
  const resolutions = config?.resolutions || ["2MP", "3MP", "4MP", "5MP", "8MP"];
  const brands = config?.brands || [];
  const systemTypes = config?.system_types || [];
  const sdCardOptions = config?.sd_card_options || [];
  const selSystem = systemTypes.find((st) => st.id === systemType);
  const currentResolutions = selSystem?.resolutions || resolutions;

  const businessName = config?.business?.name || "adicctv.com";
  const businessTagline = config?.business?.tagline || "Service & Instalasi Bergaransi";

  return (
    <>
    <style>{`
      .proposal-markdown table { border-collapse: collapse; width: 100%; margin: 12px 0; }
      .proposal-markdown th { background: #e5e7eb; font-weight: 600; }
      .proposal-markdown th, .proposal-markdown td { border: 1px solid #d1d5db; padding: 6px 10px; text-align: left; }
      .proposal-markdown tr:nth-child(even) td { background: #f9fafb; }
      .bom-table { border-collapse: collapse; width: 100%; }

      @media print {
        html, body { font-size: 12pt; color: #000; background: #fff !important; width: 100%; }
        .drawer-side, .navbar, .btn, .card form, .card-title .btn, header .btn { display: none !important; }
        .drawer { display: block !important; }
        .drawer-content { display: block !important; margin: 0 !important; padding: 0 !important; }
        .drawer-content > .flex-col > main { padding: 0 !important; margin: 0 !important; }
        .grid { display: block !important; }
        .lg\\:grid-cols-2 > div:first-child { display: none !important; }
        .lg\\:grid-cols-2 > div:last-child { display: block !important; max-width: 100% !important; }
        .card { box-shadow: none !important; border: none !important; }
        .card-body { padding: 0 !important; }
        .max-h-\\[70vh\\] { max-height: none !important; overflow: visible !important; }
        .proposal-markdown h1 { font-size: 18pt; margin-top: 24px; margin-bottom: 8px; }
        .proposal-markdown h2 { font-size: 14pt; margin-top: 20px; margin-bottom: 6px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
        .proposal-markdown h3 { font-size: 12pt; margin-top: 14px; }
        .proposal-markdown p, .proposal-markdown li { margin: 4px 0; line-height: 1.6; }
        .proposal-markdown table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 8px 0; }
        .proposal-markdown th, .proposal-markdown td { border: 1px solid #333; padding: 5px 8px; text-align: left; }
        .proposal-markdown th { background: #e0e0e0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-weight: bold; }
        .proposal-markdown tr:nth-child(even) td { background: #f5f5f5 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .print-stat, .card .card-title, .print-header { display: none !important; }
        .overflow-x-auto { overflow: visible !important; }
        .bom-table td, .bom-table th { background: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .bom-table thead tr:first-child th { background: #dbeafe !important; }
        @page { margin: 15mm 20mm; }
      }
    `}</style>
    <div className="max-w-5xl mx-auto p-4 md:p-8">
      <header className="mb-8 print-header">
        <div className="text-3xl font-bold tracking-tight">{businessName}</div>
        <p className="text-base-content/60 text-sm">
          {businessTagline}
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Client & Project Data</h2>

            {configLoading && (
              <div className="text-sm text-base-content/60">Loading configuration...</div>
            )}

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
                {projectTypes.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label}
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
                <span className="label-text">System Type</span>
                <select
                  className="select select-bordered w-full"
                  value={systemType}
                  onChange={(e) => {
                    const newType = e.target.value;
                    setSystemType(newType);
                    setSdCardSize("");
                    const newSys = systemTypes.find((st) => st.id === newType);
                    const newRes = newSys?.resolutions || resolutions;
                    if (newRes.length > 0 && !newRes.includes(resolution)) {
                      setResolution(newRes[0]);
                    }
                  }}
                >
                  {systemTypes.map((st) => (
                    <option key={st.id} value={st.id}>
                      {st.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-control w-full">
                <span className="label-text">Resolution</span>
                <select
                  className="select select-bordered w-full"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                >
                  {currentResolutions.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <label className="form-control w-full">
                <span className="label-text">Camera Indoor Qty</span>
                <input
                  type="number"
                  className="input input-bordered w-full"
                  min={0}
                  max={256}
                  value={cameraCountIndoor}
                  onChange={(e) => setCameraCountIndoor(Math.max(0, Number(e.target.value)))}
                />
              </label>
              <label className="form-control w-full">
                <span className="label-text">Camera Outdoor Qty</span>
                <input
                  type="number"
                  className="input input-bordered w-full"
                  min={0}
                  max={256}
                  value={cameraCountOutdoor}
                  onChange={(e) => setCameraCountOutdoor(Math.max(0, Number(e.target.value)))}
                />
              </label>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {selSystem && !selSystem.has_sd_card && (
                <label className="form-control w-full">
                  <span className="label-text">Recording Type</span>
                  <select
                    className="select select-bordered w-full"
                    value={recordingType}
                    onChange={(e) => setRecordingType(e.target.value)}
                  >
                    <option value="full">Full (24 Jam)</option>
                    <option value="motion">Motion (12 Jam)</option>
                  </select>
                </label>
              )}

              <label className="form-control w-full">
                <span className="label-text">Brand</span>
                <select
                  className="select select-bordered w-full"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                >
                  <option value="">Semua Brand</option>
                  {brands.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="flex items-center gap-2 cursor-pointer mt-2">
              <input
                type="checkbox"
                className="checkbox checkbox-primary checkbox-sm"
                checked={usePipa}
                onChange={(e) => setUsePipa(e.target.checked)}
              />
              <span className="label-text">Conduit</span>
            </label>

            {selSystem && selSystem.has_sd_card && sdCardOptions.length > 0 && (
              <label className="form-control w-full">
                <span className="label-text">SD Card</span>
                <select
                  className="select select-bordered w-full"
                  value={sdCardSize}
                  onChange={(e) => setSdCardSize(e.target.value)}
                >
                  {sdCardOptions.map((opt) => (
                    <option key={opt.size_gb} value={opt.size_gb > 0 ? `${opt.size_gb}GB` : ""}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </label>
            )}

            {error && (
              <div className="alert alert-error">
                <span>{error}</span>
              </div>
            )}

            <div className="grid grid-cols-3 gap-4">
              {selSystem && selSystem.has_utp_cable && (
                <label className="form-control w-full">
                  <span className="label-text">Kabel UTP (M)</span>
                  <input
                    type="number"
                    className="input input-bordered w-full"
                    min={0}
                    value={kabelUtpQty}
                    onChange={(e) => setKabelUtpQty(Math.max(0, Number(e.target.value)))}
                    placeholder="0 = auto"
                  />
                </label>
              )}
              {selSystem && selSystem.has_power_cable && (
                <label className="form-control w-full">
                  <span className="label-text">Kabel Power (M)</span>
                  <input
                    type="number"
                    className="input input-bordered w-full"
                    min={0}
                    value={kabelPowerQty}
                    onChange={(e) => setKabelPowerQty(Math.max(0, Number(e.target.value)))}
                    placeholder="0"
                  />
                </label>
              )}
              {selSystem && selSystem.has_coaxial_cable && (
                <label className="form-control w-full">
                  <span className="label-text">Kabel Coaxial (M)</span>
                  <input
                    type="number"
                    className="input input-bordered w-full"
                    min={0}
                    value={kabelCoaxialQty}
                    onChange={(e) => setKabelCoaxialQty(Math.max(0, Number(e.target.value)))}
                    placeholder="0"
                  />
                </label>
              )}
            </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <button
              className="btn btn-primary w-full mb-4"
              onClick={handleGenerate}
              disabled={isLoading || configLoading}
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

            <div className="flex items-center justify-between">
              <h2 className="card-title">Proposal Preview</h2>
              {result && (
                <button className="btn btn-outline btn-sm" onClick={handleDownloadPDF}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  Download PDF
                </button>
              )}
            </div>

            {result ? (
              <div ref={previewRef} className="overflow-y-auto max-h-[35vh] proposal-content">
                {result.letter_info ? (
                  <SuratPenawaran letterInfo={result.letter_info}>
                    {result.storage_summary && (
                      <div className="flex gap-2 items-center mb-2 p-1 bg-base-200 rounded-box text-xs">
                        <span>Storage/Day: <strong>{String(result.storage_summary.daily_storage_gb)} GB</strong></span>
                        <span className="text-base-content/30">|</span>
                        <span>Recording: <strong>30 Hari</strong></span>
                        <span className="text-base-content/30">|</span>
                        <span>HDD: <strong>{String(result.storage_summary.recommended_hdd_tb)} TB</strong></span>
                      </div>
                    )}
                    {(() => {
                      const parts = result.proposal_markdown.split("<!--BOM-->");
                      return (
                        <>
                          {parts.map((part, i) => (
                            <div key={i}>
                              <div className="prose prose-sm max-w-none proposal-markdown">
                                <ReactMarkdown
                                  components={{
                                    table: ({ children }) => (
                                      <div className="overflow-x-auto">
                                        <table className="table table-sm proposal-table">
                                          {children}
                                        </table>
                                      </div>
                                    ),
                                  }}
                                >
                                  {part}
                                </ReactMarkdown>
                              </div>
                              {i < parts.length - 1 && result.bom_data && (
                                <BomTable data={result.bom_data} />
                              )}
                            </div>
                          ))}
                        </>
                      );
                    })()}
                  </SuratPenawaran>
                ) : (
                  <>
                    {result.storage_summary && (
                      <div className="flex gap-2 items-center mb-2 p-1 bg-base-200 rounded-box text-xs">
                        <span>Storage/Day: <strong>{String(result.storage_summary.daily_storage_gb)} GB</strong></span>
                        <span className="text-base-content/30">|</span>
                        <span>Recording: <strong>30 Hari</strong></span>
                        <span className="text-base-content/30">|</span>
                        <span>HDD: <strong>{String(result.storage_summary.recommended_hdd_tb)} TB</strong></span>
                      </div>
                    )}
                    {(() => {
                      const parts = result.proposal_markdown.split("<!--BOM-->");
                      return (
                        <>
                          {parts.map((part, i) => (
                            <div key={i}>
                              <div className="prose prose-sm max-w-none proposal-markdown">
                                <ReactMarkdown
                                  components={{
                                    table: ({ children }) => (
                                      <div className="overflow-x-auto">
                                        <table className="table table-sm proposal-table">
                                          {children}
                                        </table>
                                      </div>
                                    ),
                                  }}
                                >
                                  {part}
                                </ReactMarkdown>
                              </div>
                              {i < parts.length - 1 && result.bom_data && (
                                <BomTable data={result.bom_data} />
                              )}
                            </div>
                          ))}
                        </>
                      );
                    })()}
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-base-content/40">
                <div className="text-center">
                  <p className="text-3xl mb-1">📄</p>
                  <p className="text-sm">Fill the form and generate a proposal</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
