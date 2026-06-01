import { ReactNode } from "react";
import { LetterInfo } from "@/lib/api";

interface SuratPenawaranProps {
  letterInfo: LetterInfo;
  children?: ReactNode;
}

function formatPrice(val: number): string {
  return `Rp ${val.toLocaleString("id-ID")}`;
}

export default function SuratPenawaran({ letterInfo, children }: SuratPenawaranProps) {
  const { letter_number, date, customer_address, client_name, project_type, camera_count_indoor, camera_count_outdoor, grand_total } = letterInfo;

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
          <img src="/logo.webp" alt="adicctv.com" className="kop-img" />
        </div>
        <div className="info">
          <div className="info-title">adicctv.com</div>
          <div>Alamat : Kp. Bojong RT.005/026 Bakti Jaya Sukmajaya Depok 16418</div>
          <div>Email : fitriadijamil@gmail.com</div>
          <div>Tlp/WA : 0851 5604 4200</div>
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
          Bersama surat ini, kami dari adicctv.com mengajukan penawaran harga untuk pengadaan CCTV di {project_type} sebagai berikut:{camera_count_indoor > 0 || camera_count_outdoor > 0 ? ` (${camera_count_indoor} Indoor + ${camera_count_outdoor} Outdoor)` : ''}
        </div>

        <div style={{ marginBottom: "6px" }}>
          <strong>{grand_total > 0 ? `Total Harga: ${formatPrice(grand_total)}` : ""}</strong>
        </div>

        {children}

        <div className="syarat">
          <h3>Syarat &amp; Ketentuan:</h3>
          <table>
            <tbody>
              <tr><td width="150">Pembayaran</td><td>: DP 70%, setelah pekerjaan selesai 30%</td></tr>
              <tr><td>Mulai Pekerjaan</td><td>: Maksimal 5 hari setelah DP diterima</td></tr>
              <tr><td>Garansi Produk</td><td>: 1 tahun</td></tr>
              <tr><td>Garansi Instalasi</td><td>: 1 bulan</td></tr>
              <tr><td>Masa Berlaku</td><td>: 5 hari</td></tr>
              <tr><td>Harga</td><td>: Sudah termasuk PPN 11%</td></tr>
              <tr><td>Ongkos Kirim</td><td>: Sudah termasuk area Jabodetabek</td></tr>
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: "8px", fontSize: "10pt", fontWeight: "bold", fontStyle: "italic" }}>
          Pembayaran via transfer Bank BCA 6080473271 a.n. Fitriadi Jamil
        </div>

        <div className="ttd">
          <div>Hormat kami,</div>
          <div className="jarak" />
          <div className="nama">Fitriadi Jamil</div>
        </div>
      </div>
    </div>
  );
}
