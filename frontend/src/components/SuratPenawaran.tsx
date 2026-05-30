import { LetterInfo } from "@/lib/api";

interface SuratPenawaranProps {
  letterInfo: LetterInfo;
}

function formatPrice(val: number): string {
  return `Rp ${val.toLocaleString("id-ID")}`;
}

export default function SuratPenawaran({ letterInfo }: SuratPenawaranProps) {
  const { letter_number, date, customer_attention, customer_address, client_name, project_type, grand_total } = letterInfo;

  return (
    <div className="surat-wrapper mb-6">
      <style>{`
        .surat-wrapper {
          font-family: 'Times New Roman', Times, serif;
          font-size: 12pt;
          line-height: 1.6;
        }
        .surat-wrapper .kop {
          text-align: center;
          border-bottom: 3px solid #000;
          padding-bottom: 12px;
          margin-bottom: 20px;
        }
        .surat-wrapper .kop h1 {
          font-size: 20pt;
          font-weight: bold;
          margin: 0;
          letter-spacing: 2px;
        }
        .surat-wrapper .kop .subtitle {
          font-size: 11pt;
          font-style: italic;
          margin-top: 2px;
        }
        .surat-wrapper .kop .alamat {
          font-size: 10pt;
          margin-top: 6px;
        }
        .surat-wrapper .body {
          padding: 0 4px;
        }
        .surat-wrapper .nomor-surat {
          text-align: center;
          margin-bottom: 16px;
        }
        .surat-wrapper .perihal {
          text-align: center;
          font-weight: bold;
          text-decoration: underline;
          margin-bottom: 20px;
        }
        .surat-wrapper .kepada {
          margin-bottom: 12px;
        }
        .surat-wrapper .syarat {
          margin-top: 16px;
          border: 1px solid #000;
          padding: 12px;
        }
        .surat-wrapper .syarat h3 {
          font-size: 12pt;
          font-weight: bold;
          margin: 0 0 8px 0;
        }
        .surat-wrapper .syarat table {
          width: 100%;
          border-collapse: collapse;
        }
        .surat-wrapper .syarat td {
          padding: 2px 8px;
          vertical-align: top;
        }
        .surat-wrapper .ttd {
          margin-top: 32px;
          text-align: right;
        }
        .surat-wrapper .ttd .nama {
          margin-top: 64px;
          font-weight: bold;
          text-decoration: underline;
        }
        @media print {
          .surat-wrapper { font-size: 12pt; }
        }
      `}</style>

      <div className="kop">
        <h1>PT. ADI SUKSES SEJAHTERA</h1>
        <div className="subtitle">CCTV &amp; Security System Specialist</div>
        <div className="alamat">
          Komplek Perkantosa Kenari Permai Blok C No. 14 - Jl. Raya Curug Agung, Cimanggis - Depok<br />
          Telp/WA: 085156044200 | Email: info@adicctv.com | Website: adicctv.com
        </div>
      </div>

      <div className="body">
        <div className="nomor-surat">
          Nomor: {letter_number}
        </div>

        <div style={{ textAlign: "right", marginBottom: "16px" }}>
          {date}
        </div>

        <div className="perihal">
          Perihal: Penawaran Harga Sistem {project_type} untuk {client_name}
        </div>

        <div className="kepada">
          <div>Kepada Yth:</div>
          <div>{customer_attention}</div>
          <div>{customer_address}</div>
          <div style={{ marginTop: "8px" }}>Dengan hormat,</div>
        </div>

        <div style={{ textIndent: "32px", textAlign: "justify", marginBottom: "8px" }}>
          Bersama surat ini, kami PT. Adi Sukses Sejahtera selaku perusahaan yang bergerak di bidang
          penyediaan sistem CCTV dan Security System, dengan ini mengajukan penawaran harga untuk
          pengadaan sistem {project_type} di {customer_address || "lokasi yang telah ditentukan"}.
        </div>

        <div style={{ textIndent: "32px", textAlign: "justify", marginBottom: "8px" }}>
          Adapun rincian penawaran yang kami ajukan adalah sebagai berikut:
        </div>

        <div style={{ marginBottom: "12px" }}>
          <strong>{grand_total > 0 ? `Total Harga: ${formatPrice(grand_total)}` : ""}</strong>
        </div>

        <div className="syarat">
          <h3>Syarat &amp; Ketentuan:</h3>
          <table>
            <tbody>
              <tr><td width="140">Pembayaran</td><td>: Transfer Bank BCA 6080473271 a/n Fitriadi Jamil</td></tr>
              <tr><td>Garansi Produk</td><td>: 1 tahun</td></tr>
              <tr><td>Garansi Instalasi</td><td>: 1 bulan</td></tr>
              <tr><td>Pengiriman</td><td>: 1-2 minggu setelah PO diterima</td></tr>
              <tr><td>Masa Berlaku</td><td>: 14 hari</td></tr>
              <tr><td>Harga</td><td>: Sudah termasuk PPN 11%</td></tr>
              <tr><td>Pengiriman</td><td>: Sudah termasuk ongkos kirim area Jabodetabek</td></tr>
            </tbody>
          </table>
        </div>

        <div className="ttd">
          <div>Hormat kami,</div>
          <div>PT. Adi Sukses Sejahtera</div>
          <div className="nama">Fitriadi Jamil</div>
          <div>Director</div>
        </div>
      </div>
    </div>
  );
}
