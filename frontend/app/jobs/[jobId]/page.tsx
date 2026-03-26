"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { API_BASE_URL, getJob, type Job } from "../../../lib/api";

export default function JobDetailPage({ params }: { params: { jobId: string } }) {
  const [jobId] = useState<string>(params.jobId);
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    let cancelled = false;
    const load = async () => {
      try {
        const nextJob = await getJob(jobId);
        if (!cancelled) {
          setJob(nextJob);
          setError(null);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Khong the tai job");
        }
      }
    };

    load();
    const timer = window.setInterval(load, 3000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [jobId]);

  return (
    <main className="page">
      <div className="shell stack">
        <section className="hero">
          <span className="badge">Job detail</span>
          <h1>Theo doi luong rewrite theo tung giai doan.</h1>
        </section>

        {error ? <p className="status-error">{error}</p> : null}

        {job ? (
          <>
            <section className="card stack">
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>
                  <h2>Job #{job.job_id.slice(0, 8)}</h2>
                  <p>Trang thai hien tai: {job.status}</p>
                </div>
                <span className="badge">{job.progress}%</span>
              </div>
              <div className="progress" aria-label={`Tien trinh ${job.progress}%`}>
                <span style={{ width: `${job.progress}%` }} />
              </div>
              <div className="grid two-col">
                <div className="card">
                  <strong>{job.total_units}</strong>
                  <p>Tong so repair units</p>
                </div>
                <div className="card">
                  <strong>{job.rewritten_units}</strong>
                  <p>Da rewrite</p>
                </div>
                <div className="card">
                  <strong>{job.manual_review_units}</strong>
                  <p>Can manual review</p>
                </div>
                <div className="card">
                  <strong>{job.provider_fail_count}</strong>
                  <p>Provider fail count</p>
                </div>
              </div>
            </section>

            <section className="card stack">
              <h2>Activity log</h2>
              <ol className="timeline">
                {job.timeline.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ol>
            </section>

            <section className="row">
              <Link className="button" href={`/review/${job.job_id}`}>
                Xem ket qua
              </Link>
              {job.output_docx_path ? (
                <a className="button secondary" href={`${API_BASE_URL}/jobs/${job.job_id}/download/docx`}>
                  Tai revised.docx
                </a>
              ) : null}
              {job.change_report_path ? (
                <a className="button secondary" href={`${API_BASE_URL}/jobs/${job.job_id}/download/report`}>
                  Tai change_report.json
                </a>
              ) : null}
            </section>
          </>
        ) : (
          <section className="card">
            <p>Dang tai thong tin job...</p>
          </section>
        )}
      </div>
    </main>
  );
}
