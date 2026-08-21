"use client";

import { useState } from "react";

const API = "http://localhost:8000";

type ReviewPayload = {
  ticket_id: string;
  draft: string;
  faithfulness_score: number | null;
};

export default function Home() {
  const [ticketId, setTicketId] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [review, setReview] = useState<ReviewPayload | null>(null);
  const [statusMsg, setStatusMsg] = useState("");
  const [editedText, setEditedText] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitTicket() {
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch(`${API}/tickets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ticket_id: ticketId,
          customer_email: email,
          subject,
          body,
        }),
      });
      const data = await res.json();

      if (res.status === 409) {
        setStatusMsg(`Error: ${data.detail}`);
      } else if (data.status === "pending_approval") {
        setReview(data.review);
      } else {
        setStatusMsg(`Auto-escalated to human queue. Status: ${data.status}`);
      }
    } finally {
      setLoading(false);
    }
  }

  async function decide(decision: string) {
    const params = new URLSearchParams({ decision });
    if (editedText) params.append("edited_text", editedText);

    const res = await fetch(
      `${API}/tickets/${review?.ticket_id}/decision?${params}`,
      {
        method: "POST",
      },
    );
    const data = await res.json();
    setStatusMsg(
      `Decision "${decision}" recorded. Final approval status: ${data.approval}`,
    );
    setReview(null);
    setEditedText("");
  }

  return (
    <main className="max-w-2xl mx-auto p-8 space-y-8">
      <h1 className="text-2xl font-bold">Support Ops Copilot</h1>

      <section className="border rounder-lg p-4 space-y-2">
        <h2 className="font-semibold">Submit a ticket</h2>
        <input
          className="w-full border rounded p-2"
          placeholder="ticket id"
          value={ticketId}
          onChange={(e) => setTicketId(e.target.value)}
        />
        <input
          className="w-full border rounded p-2"
          placeholder="customer email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full border rounded p-2"
          placeholder="subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
        <textarea
          className="w-full border rounded p-2"
          rows={3}
          placeholder="body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <button
          className="bg-black text-white rounded py-2 px-4 disabled:opacity-50"
          onClick={submitTicket}
          disabled={loading || !ticketId || !email}
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </section>

      {review && (
        <section className="border rounder-lg p-4 space-y-2 bg-gray-50">
          <h2 className="font-semibold">
            Pending approval - {review.ticket_id}
          </h2>
          <p className="text-sm">
            Faithfulness score:{" "}
            <span
              className={
                review.faithfulness_score! < 0.7
                  ? "text-red-600 font-bold"
                  : "text-green-700 font-bold"
              }
            >
              {review.faithfulness_score?.toFixed(2)}
            </span>
          </p>
          <pre className="whitespace-pre-wrap bg-white p-3 rounded border text-sm">
            {review.draft}
          </pre>
          <textarea
            className="w-full border rounded p-2"
            rows={3}
            placeholder="Edit reply before sending (optional)"
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
          />
          <div className="flex gap-2">
            <button
              className="bg-green-600 text-white rounded py-1 px-3"
              onClick={() => decide("approved")}
            >
              Approve
            </button>
            <button
              className="bg-blue-600 text-white rounded py-1 px-3"
              onClick={() => decide("edited")}
            >
              Send edited
            </button>
            <button
              className="bg-red-600 text-white rounded py-1 px-3"
              onClick={() => decide("rejected")}
            >
              Reject
            </button>
          </div>
        </section>
      )}

      {statusMsg && <p className="text-sm text-gray-700">{statusMsg}</p>}
    </main>
  );
}
