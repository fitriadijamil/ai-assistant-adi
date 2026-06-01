"use client";

import { ReactNode } from "react";
import { LetterInfo } from "@/lib/api";
import { useBusinessConfig } from "@/lib/useBusinessConfig";

interface SuratPenawaranProps {
  letterInfo: LetterInfo;
  children?: ReactNode;
}

function formatPrice(val: number): string {
  return `Rp ${val.toLocaleString("id-ID")}`;
}

export default function SuratPenawaran({ letterInfo, children }: SuratPenawaranProps) {
  const { config, loading } = useBusinessConfig();
  const { letter_number, date, customer_address, client_name, project_type, camera_count_indoor, camera_count_outdoor, grand_total } = letterInfo;

  if (loading || !config) {
    return <div className="p-4 text-base-content/60">Loading...</div>;
  }

  const { contact, proposal, bank_account, surat_penawaran: spConfig } = config;
  const terms = proposal.terms || [];

  return (
    <div className="surat-wrapper mb-6">
      <style>{`
        .surat-wrapper {
          font-family: 'Times New Roman', Times, serif;
          font-size: 11pt;
          line-height: 1.5;
        }
        .surat-wrapper .kop {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 2px solid #000;
          padding-bottom: 8px;
          margin-bottom: 12px;
        }
        .surat-wrapper .kop .kop-logo {
          flex-shrink: 0;
        }
        .surat-wrapper .kop .kop-img {
          width: auto;
          height: 110px;
          display: block;
        }
        .surat-wrapper .kop .info {
          font-size: 10pt;
          text-align: right;
        }
        .surat-wrapper .kop .info .info-title {
          font-weight: bold;
          font-size: 12pt;
        }
        .surat-wrapper .kop .info div {
          margin: 1px 0;
        }
        .surat-wrapper .body {
          padding: 0 4px;
        }
        .surat-wrapper .meta-line {
          font-size: 11pt;
          margin: 2px 0;
          text-align: right;
        }
        .surat-wrapper .perihal {
          font-weight: bold;
          text-decoration: underline;
          margin: 8px 0 12px 0;
        }
        .surat-wrapper .kepada {
          margin: 8px 0;
        }
        .surat-wrapper .pembuka {
          margin: 6px 0;
          text-align: justify;
        }
        .surat-wrapper .syarat {
          margin-top: 10px;
          border: 1px solid #000;
          padding: 8px;
        }
        .surat-wrapper .syarat h3 {
          font-size: 11pt;
          font-weight: bold;
          margin: 0 0 4px 0;
        }
        .surat-wrapper .syarat table {
          width: 100%;
          border-collapse: collapse;
        }
        .surat-wrapper .syarat td {
          padding: 1px 6px;
          vertical-align: top;
          font-size: 10pt;
        }
        .surat-wrapper .ttd {
          margin-top: 24px;
          text-align: right;
        }
        .surat-wrapper .ttd .jarak {
          height: 48px;
        }
        .surat-wrapper .ttd .nama {
          font-weight: bold;
          text-decoration: underline;
        }
        @media print {
          .surat-wrapper { font-size: 11pt; }
        }
      `}</style>

      <div className="kop">
        <div className="kop-logo">
          {spConfig.show_logo && (
            <img src="/logo.webp" alt={contact.website} className="kop-img" />
          )}
        </div>
        <div className="info">
          <div className="info-title">{contact.website?.replace("https://", "")}</div>
          <div>Alamat : {contact.address}</div>
          <div>Email : {contact.email}</div>
          <div>Tlp/WA : {contact.phone || contact.whatsapp}</div>
        </div>
      </div>

      <div className="body">
        <div className="meta-line">Nomor Surat: {letter_number}</div>
        <div className="meta-line">{date}</div>

        <div className="perihal">Perihal: Penawaran Harga Sistem {project_type}</div>

        <div className="kepada">
          <div>Kepada Yth,</div>
          <div>Bapak/Ibu : {client_name}</div>
          <div>{customer_address}</div>
        </div>

        <div className="pembuka">
          Bersama surat ini, kami dari {contact.website?.replace("https://", "")} mengajukan penawaran harga untuk pengadaan CCTV di {project_type} sebagai berikut:{camera_count_indoor > 0 || camera_count_outdoor > 0 ? ` (${camera_count_indoor} Indoor + ${camera_count_outdoor} Outdoor)` : ''}
        </div>

        <div style={{ marginBottom: "6px" }}>
          <strong>{grand_total > 0 ? `Total Harga: ${formatPrice(grand_total)}` : ""}</strong>
        </div>

        {children}

        <div className="syarat">
          <h3>Syarat &amp; Ketentuan:</h3>
          <table>
            <tbody>
              {terms.map((term, i) => {
                const [label, ...rest] = term.split(":");
                return (
                  <tr key={i}>
                    <td width="150">{label}</td>
                    <td>: {rest.join(":").trim()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {spConfig.show_bank_account && (
          <div style={{ marginTop: "8px", fontSize: "10pt", fontWeight: "bold", fontStyle: "italic" }}>
            {bank_account.label}
          </div>
        )}

        {spConfig.show_ttd && (
          <div className="ttd">
            <div>Hormat kami,</div>
            <div className="jarak" />
            <div className="nama">{proposal.signatory}</div>
          </div>
        )}
      </div>
    </div>
  );
}
