"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createJob } from "../../lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [sourceDocx, setSourceDocx] = useState<File | null>(null);
  const [reportPdf, setReportPdf] = useState<File | null>(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    if (!sourceDocx || !reportPdf || !acknowledged) {
      setError("Can chon du 2 file va xac nhan se review lai ket qua.");
      return;
    }

    setSubmitting(true);
    setError(null);
    const formData = new FormData();
    formData.append("source_docx", sourceDocx);
    formData.append("report_pdf", reportPdf);

    try {
      const job = await createJob(formData);
      router.push(`/jobs/${job.job_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Upload that bai");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page">
      <div className="shell stack">
        <section className="hero">
          <span className="badge">Upload</span>
          <h1>Nap tai lieu can doi chieu.</h1>
          <p>
            Tai file nguon DOCX va file PDF bao cao. He thong se phan tich, canh bao doan can
            review va tao file DOCX moi de ban kiem tra.
          </p>
        </section>

        <section className="grid two-col">
          <div className="card stack">
            <label htmlFor="source-docx">Tai tai lieu DOCX</label>
            <input
              id="source-docx"
              className="file-input"
              type="file"
              accept=".docx"
              onChange={(event) => setSourceDocx(event.target.files?.[0] ?? null)}
            />
            <small>{sourceDocx ? sourceDocx.name : "Chua chon file DOCX."}</small>
          </div>

          <div className="card stack">
            <label htmlFor="report-pdf">Tai bao cao PDF</label>
            <input
              id="report-pdf"
              className="file-input"
              type="file"
              accept=".pdf"
              onChange={(event) => setReportPdf(event.target.files?.[0] ?? null)}
            />
            <small>{reportPdf ? reportPdf.name : "Chua chon file PDF."}</small>
          </div>
        </section>

        <section className="card stack">
          <label className="row">
            <input
              type="checkbox"
              checked={acknowledged}
              onChange={(event) => setAcknowledged(event.target.checked)}
            />
            <span>Toi hieu rang can review lai ket qua truoc khi su dung.</span>
          </label>
          <div className="row">
            <button className="button" disabled={submitting} onClick={handleSubmit}>
              {submitting ? "Dang tai len..." : "Bat dau xu ly"}
            </button>
          </div>
          {error ? <p className="status-error">{error}</p> : null}
        </section>
      </div>
    </main>
  );
}
