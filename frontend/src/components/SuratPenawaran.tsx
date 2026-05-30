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
          font-size: 11pt;
          line-height: 1.5;
        }
        .surat-wrapper .kop {
          text-align: center;
          border-bottom: 2px solid #000;
          padding-bottom: 8px;
          margin-bottom: 12px;
        }
        .surat-wrapper .kop .nama-perusahaan {
          font-size: 14pt;
          font-weight: bold;
          margin: 0;
          letter-spacing: 1px;
        }
        .surat-wrapper .kop .subtitle {
          font-size: 10pt;
          font-style: italic;
        }
        .surat-wrapper .kop .info {
          font-size: 10pt;
          margin-top: 4px;
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
        }
        .surat-wrapper .perihal {
          font-weight: bold;
          text-decoration: underline;
          margin: 8px 0;
        }
        .surat-wrapper .kepada {
          margin: 8px 0;
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
        <div className="nama-perusahaan">PT. ADI SUKSES SEJAHTERA</div>
        <div className="subtitle">CCTV &amp; Security System Specialist</div>
        <div className="info">
          <div>adicctv.com</div>
          <div>Kp. Bojong RT.005/026 No. 50, Bakti Jaya Sukmajaya 16418</div>
          <div>No. Tlp/WA: 085156044200</div>
          <div>Email: info@adicctv.com</div>
        </div>
      </div>

      <div className="body">
        <div className="meta-line">No Penawaran: {letter_number}</div>
        <div className="meta-line">Tanggal: {date}</div>
        <div className="perihal">Perihal: Penawaran Harga Sistem {project_type} untuk {client_name}</div>

        <div className="kepada">
          <div>Kepada Yth:</div>
          <div>{customer_attention}</div>
          <div>{customer_address}</div>
          <div style={{ marginTop: "4px" }}>Dengan hormat,</div>
        </div>

        <div style={{ marginBottom: "6px" }}>
          <strong>{grand_total > 0 ? `Total Harga: ${formatPrice(grand_total)}` : ""}</strong>
        </div>

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

        <div className="ttd">
          <div>Hormat kami,</div>
          <div className="jarak" />
          <div className="nama">Fitriadi Jamil</div>
        </div>
      </div>
    </div>
  );
}
