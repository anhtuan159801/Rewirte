"use client";

import { useEffect, useMemo, useState } from "react";

import { API_BASE_URL, getUnits, type RepairUnit } from "../../../lib/api";

export default function ReviewPage({ params }: { params: { jobId: string } }) {
  const [jobId] = useState(params.jobId);
  const [units, setUnits] = useState<RepairUnit[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!jobId) {
      return;
    }
    getUnits(jobId).then(setUnits).catch(() => setUnits([]));
  }, [jobId]);

  const filteredUnits = useMemo(() => {
    return units.filter((unit) => {
      const matchesSearch =
        unit.original_text.toLowerCase().includes(search.toLowerCase()) ||
        (unit.rewritten_text ?? "").toLowerCase().includes(search.toLowerCase());
      if (!matchesSearch) {
        return false;
      }
      if (filter === "manual") {
        return unit.status === "MANUAL_REVIEW";
      }
      if (filter === "citation") {
        return Boolean(unit.citation_needed);
      }
      return true;
    });
  }, [filter, search, units]);

  return (
    <main className="page">
      <div className="shell stack">
        <section className="hero">
          <span className="badge">Review</span>
          <h1>So sanh noi dung goc va noi dung sau khi rewrite.</h1>
        </section>

        <section className="card stack">
          <div className="row">
            <input
              className="input"
              placeholder="Tim theo noi dung"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <select className="select" value={filter} onChange={(event) => setFilter(event.target.value)}>
              <option value="all">Tat ca</option>
              <option value="manual">Can review</option>
              <option value="citation">Can citation</option>
            </select>
          </div>
        </section>

        <section className="card stack">
          {filteredUnits.length === 0 ? (
            <p>Khong co doan nao khop voi bo loc hien tai.</p>
          ) : (
            filteredUnits.map((unit) => (
              <article className="unit-card stack" key={unit.id}>
                <div className="row">
                  <span className="badge">{unit.paragraph_ref}</span>
                  <span className="badge">{unit.risk_type}</span>
                  <span className="badge">{unit.provider_used ?? "pending"}</span>
                  <span className="badge">confidence {unit.confidence ?? "-"}</span>
                  {unit.citation_needed ? <span className="badge">Can xem lai trich dan</span> : null}
                </div>
                <div className="grid two-col">
                  <div>
                    <h3>Original</h3>
                    <p>{unit.original_text}</p>
                  </div>
                  <div>
                    <h3>Rewritten</h3>
                    <p>{unit.rewritten_text ?? unit.failure_reason ?? "Chua co ket qua."}</p>
                  </div>
                </div>
                <div>
                  <h3>Summary of changes</h3>
                  <p>{unit.summary_of_changes ?? "Can review thu cong."}</p>
                </div>
              </article>
            ))
          )}
        </section>

        <section className="row">
          <a className="button" href={`${API_BASE_URL}/jobs/${jobId}/download/docx`}>
            Tai revised.docx
          </a>
          <a className="button secondary" href={`${API_BASE_URL}/jobs/${jobId}/download/report`}>
            Tai change_report.json
          </a>
        </section>
      </div>
    </main>
  );
}
