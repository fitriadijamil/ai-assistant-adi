"use client";

import { ToolCallResult } from "@/lib/api";

function StorageCalculatorCard({ result }: { result: Record<string, unknown> }) {
  return (
    <div className="alert shadow-lg bg-base-200 border border-primary/20">
      <div className="flex-col items-start gap-2 w-full">
        <div className="flex items-center gap-2">
          <span className="text-lg">💾</span>
          <span className="font-semibold">Storage Calculator</span>
        </div>
        <div className="grid grid-cols-2 gap-2 w-full text-sm">
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Daily</div>
            <div className="stat-value text-lg">{String(result.daily_storage_gb ?? "-")} GB</div>
          </div>
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Monthly</div>
            <div className="stat-value text-lg">{String(result.monthly_storage_gb ?? "-")} GB</div>
          </div>
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Recommended HDD</div>
            <div className="stat-value text-lg">{String(result.recommended_hdd_tb ?? "-")} TB</div>
          </div>
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Bitrate Used</div>
            <div className="stat-value text-lg">
              {result.bitrate_used_bps
                ? `${(Number(result.bitrate_used_bps) / 1_000_000).toFixed(1)} Mbps`
                : "-"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BandwidthCalculatorCard({ result }: { result: Record<string, unknown> }) {
  return (
    <div className="alert shadow-lg bg-base-200 border border-secondary/20">
      <div className="flex-col items-start gap-2 w-full">
        <div className="flex items-center gap-2">
          <span className="text-lg">🌐</span>
          <span className="font-semibold">Bandwidth Calculator</span>
        </div>
        <div className="grid grid-cols-2 gap-2 w-full text-sm">
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Total Bandwidth</div>
            <div className="stat-value text-lg">{String(result.total_bandwidth_mbps ?? "-")} Mbps</div>
          </div>
          <div className="stat p-2 min-h-0">
            <div className="stat-title text-xs">Recommendation</div>
            <div className="stat-value text-sm">{String(result.recommendation ?? "-")}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProductLookupCard({ result }: { result: Record<string, unknown> }) {
  const products = result.products as Record<string, unknown>[] | undefined;

  return (
    <div className="alert shadow-lg bg-base-200 border border-accent/20">
      <div className="flex-col items-start gap-2 w-full">
        <div className="flex items-center gap-2">
          <span className="text-lg">📦</span>
          <span className="font-semibold">
            Product Lookup: {String(result.category ?? "")}
          </span>
          <span className="badge badge-sm">{String(result.count ?? "0")} found</span>
        </div>
        {products && products.length > 0 ? (
          <div className="overflow-x-auto w-full">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Brand</th>
                  <th>Model</th>
                  <th>Spec</th>
                  <th>Est. Price</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 6).map((p, i) => (
                  <tr key={i}>
                    <td className="font-medium">{String(p.brand ?? "")}</td>
                    <td>{String(p.nama ?? "")}</td>
                    <td className="text-xs">
                      {p.resolusi ? String(p.resolusi) : p.kapasitas_tb ? `${String(p.kapasitas_tb)} TB` : ""}
                    </td>
                    <td>
                      {p.harga_estimasi
                        ? `Rp ${Number(p.harga_estimasi).toLocaleString("id-ID")}`
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {products.length > 6 && (
              <p className="text-xs text-base-content/50 mt-1">
                +{products.length - 6} more products
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-base-content/50">No products found</p>
        )}
      </div>
    </div>
  );
}

export default function ToolResult({ tool, result }: ToolCallResult) {
  if (tool === "storage_calculator") {
    return <StorageCalculatorCard result={result} />;
  }

  if (tool === "bandwidth_calculator") {
    return <BandwidthCalculatorCard result={result} />;
  }

  if (tool === "product_lookup") {
    return <ProductLookupCard result={result} />;
  }

  return (
    <div className="alert shadow-lg bg-base-200">
      <div className="flex-col items-start gap-1 w-full">
        <span className="font-semibold text-sm">Tool: {tool}</span>
        <pre className="text-xs whitespace-pre-wrap overflow-x-auto max-w-full">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>
    </div>
  );
}
