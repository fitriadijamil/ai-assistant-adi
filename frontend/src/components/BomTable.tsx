"use client";

interface BomItem {
  no: number;
  deskripsi: string;
  tipe: string;
  qty: number;
  satuan: string;
  harga: number;
  total: number;
}

interface BomData {
  kategori_a: BomItem[];
  kategori_b: BomItem[];
  total_a: number;
  total_b: number;
  grand_total: number;
}

function fmt(n: number): string {
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

export default function BomTable({ data }: { data: BomData }) {
  const items = [
    ...data.kategori_a.map((i) => ({ ...i, cat: "A" as const })),
    ...data.kategori_b.map((i) => ({ ...i, cat: "B" as const })),
  ];

  return (
    <div className="overflow-x-auto my-4">
      <table
        className="bom-table"
        style={{
          width: "100%",
          borderCollapse: "collapse",
          fontSize: "10pt",
          fontFamily: "Arial, sans-serif",
        }}
      >
        <thead>
          <tr style={{ background: "#dbeafe", fontWeight: "bold", textAlign: "center" }}>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "5%" }}>No</th>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "28%" }}>Deskripsi</th>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "15%" }}>Type</th>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "22%" }} colSpan={2}>Qty</th>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "15%" }}>Harga</th>
            <th style={{ border: "1px solid #000", padding: "6px 4px", width: "15%" }}>Total</th>
          </tr>
          <tr style={{ background: "#dbeafe", fontWeight: "bold", textAlign: "center" }}>
            <th style={{ border: "1px solid #000", padding: "4px" }}></th>
            <th style={{ border: "1px solid #000", padding: "4px" }}></th>
            <th style={{ border: "1px solid #000", padding: "4px" }}></th>
            <th style={{ border: "1px solid #000", padding: "4px", width: "11%" }}>Angka</th>
            <th style={{ border: "1px solid #000", padding: "4px", width: "11%" }}>Satuan</th>
            <th style={{ border: "1px solid #000", padding: "4px" }}></th>
            <th style={{ border: "1px solid #000", padding: "4px" }}></th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ fontWeight: "bold" }}>
            <td colSpan={7} style={{ border: "1px solid #000", padding: "6px 8px" }}>
              A. CCTV System
            </td>
          </tr>
          {data.kategori_a.map((item) => (
            <tr key={`a-${item.no}`}>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "center" }}>{item.no}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.deskripsi}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.tipe}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "center" }}>{item.qty}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.satuan}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right" }}>{fmt(item.harga)}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right" }}>{fmt(item.total)}</td>
            </tr>
          ))}
          <tr>
            <td colSpan={5} style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              Subtotal A
            </td>
            <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              {fmt(data.total_a)}
            </td>
            <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              {fmt(data.total_a)}
            </td>
          </tr>

          <tr style={{ fontWeight: "bold" }}>
            <td colSpan={7} style={{ border: "1px solid #000", padding: "6px 8px" }}>
              B. Material & Jasa Instalasi
            </td>
          </tr>
          {data.kategori_b.map((item) => (
            <tr key={`b-${item.no}`}>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "center" }}>{item.no}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.deskripsi}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.tipe}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "center" }}>{item.qty}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "left" }}>{item.satuan}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right" }}>{fmt(item.harga)}</td>
              <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right" }}>{fmt(item.total)}</td>
            </tr>
          ))}
          <tr>
            <td colSpan={5} style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              Subtotal B
            </td>
            <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              {fmt(data.total_b)}
            </td>
            <td style={{ border: "1px solid #000", padding: "5px 4px", textAlign: "right", fontWeight: "bold" }}>
              {fmt(data.total_b)}
            </td>
          </tr>

          <tr style={{ fontWeight: "bold" }}>
            <td colSpan={5} style={{ border: "1px solid #000", padding: "6px 4px", textAlign: "right" }}>
              Total
            </td>
            <td style={{ border: "1px solid #000", padding: "6px 4px", textAlign: "right" }}>
              {fmt(data.grand_total)}
            </td>
            <td style={{ border: "1px solid #000", padding: "6px 4px", textAlign: "right" }}>
              {fmt(data.grand_total)}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
