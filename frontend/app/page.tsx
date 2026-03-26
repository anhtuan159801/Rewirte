import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page">
      <div className="shell">
        <section className="hero">
          <span className="badge">MVP review-first</span>
          <h1>Chinh sua DOCX dua tren bao cao tuong dong.</h1>
          <p>
            He thong phan tich file DOCX va PDF, tao repair units, rewrite theo chuoi provider
            va giu lai buoc review cua nguoi dung truoc khi su dung ket qua.
          </p>
        </section>

        <div className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              <h2>Bat dau job moi</h2>
              <p>Upload 1 file DOCX va 1 file PDF de khoi tao luong xu ly.</p>
            </div>
            <Link href="/upload" className="button">
              Mo trang upload
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
