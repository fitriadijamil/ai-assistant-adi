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
          line-height: 1.4;
        }
        .surat-wrapper .kop {
          text-align: left;
          margin-bottom: 10px;
        }
        .surat-wrapper .kop div {
          margin: 1px 0;
        }
        .surat-wrapper .body {
          padding: 0;
        }
        .surat-wrapper .meta-right {
          text-align: right;
          margin: 2px 0;
        }
        .surat-wrapper .perihal {
          font-weight: bold;
          text-decoration: underline;
          margin: 6px 0 12px 0;
        }
        .surat-wrapper .kepada {
          margin: 6px 0;
        }
        .surat-wrapper .pembuka {
          font-weight: bold;
          margin: 6px 0;
          text-align: justify;
        }
        .surat-wrapper .syarat {
          margin-top: 8px;
          border: 1px solid #000;
          padding: 6px;
        }
        .surat-wrapper .syarat h3 {
          font-size: 11pt;
          font-weight: bold;
          margin: 0 0 3px 0;
        }
        .surat-wrapper .syarat table {
          width: 100%;
          border-collapse: collapse;
        }
        .surat-wrapper .syarat td {
          padding: 1px 4px;
          vertical-align: top;
          font-size: 10pt;
        }
        .surat-wrapper .ttd {
          margin-top: 20px;
          text-align: right;
        }
        .surat-wrapper .ttd .jarak1 { height: 6px; }
        .surat-wrapper .ttd .jarak2 { height: 6px; }
        .surat-wrapper .ttd .jarak3 { height: 6px; }
        .surat-wrapper .ttd .nama {
          font-weight: bold;
          text-decoration: underline;
        }
        @media print {
          .surat-wrapper { font-size: 11pt; }
        }
      `}</style>

      <div className="kop">
        <div><strong>adicctv.com</strong></div>
        <div>Alamat : Kp. Bojong RT.005/026 Bakti Jaya Sukmajaya Depok 16418</div>
        <div>Email : fitriadijamil@gmail.com</div>
      </div>

      <div className="body">
        <div className="meta-right">Nomor Surat: {letter_number}</div>
        <div className="meta-right">{date}</div>

        <div className="perihal">Perihal: Penawaran Harga Sistem {project_type} untuk {client_name}</div>

        <div className="kepada">
          <div>Kepada Yth,</div>
          <div>Bapak/Ibu : {client_name}</div>
          <div>{customer_address}</div>
        </div>

        <div className="pembuka">
          Bersama surat ini, kami dari adicctv.com mengajukan penawaran harga untuk pengadaan sistem {project_type} sebagai berikut:
        </div>

        <div style={{ marginBottom: "4px" }}>
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
          <div className="jarak1" />
          <div className="jarak2" />
          <div className="jarak3" />
          <div className="nama">Fitriadi Jamil</div>
        </div>
      </div>
    </div>
  );
}
