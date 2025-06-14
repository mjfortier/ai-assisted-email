import { useState, useRef, useEffect } from "react";
import type { Email } from './types';

interface Props {
  email: Email | null;
  refreshEmail: () => void;
}

export default function EmailDetail({ email, refreshEmail }: Props) {
  if (!email) return <p className="text-gray-500">Select an email to view its contents.</p>;

  const [replyDraft, setReplyDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [notes, setNotes] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const animateReply = (text: string, delay = 3) => {
    setReplyDraft("");
    function type(i: number = 0) {
      setReplyDraft(prev => prev + text[i]);
      if (i+1 < text.length) {
        setTimeout(type, delay, i+1);
      }
    }
    type();
  };

  const handleAutoDraft = () => {
    setNotes("");
    setShowNotesModal(true);
  };

  const handleSubmitNotes = async () => {
    setShowNotesModal(false);
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/generate-reply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: email,
          practitioner_notes: notes
        })
      });
      setReplyDraft(""); // Clear previous draft
      const data = await res.json();
      const reply = data.data.reply || "No reply generated.";
      animateReply(reply);
    } catch (err) {
      console.error("Error generating reply:", err);
      setReplyDraft("An error occurred while generating a reply.");
    } finally {
      setLoading(false);
    }
  };

  const handleReplyChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setReplyDraft(e.target.value);

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"; // reset
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // grow
    }
  };

  const handleSend = () => {
    if (!replyDraft.trim()) {
      alert("Reply cannot be empty.");
      return;
    }

    fetch(`http://localhost:8000/emails/${email.id}/reply`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        to: email.from,
        subject: `Re: ${email.subject}`,
        body: replyDraft,
      })})
      .then(data => {
        console.log("Reply sent successfully:", data);
      })
      .catch(err => {
        console.error("Error sending reply:", err);
        alert("Failed to send reply. Please try again.");
      });

    alert("Reply sent!");
    refreshEmail();
    setReplyDraft("");
  };

  // Make sure textarea grows on load with generated text or it looks wonky
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [replyDraft]);

  return (
    <div>
      <h2 className="text-xl font-bold mb-2">{email.subject}</h2>
      <div className="text-sm text-gray-500 mb-4">
        From: {email.from}
        <br />
        Patient: {email.patient_name}
      </div>
      <p className="whitespace-pre-wrap mb-6">{email.body}</p>

      {/* Replies Section */}
      {email.replies && email.replies.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2 text-gray-700">Replies</h3>
          <ul className="space-y-4">
            {email.replies.map((reply, idx) => (
              <li key={reply.id || idx} className="border rounded p-3 bg-gray-50">
                <div className="text-xs text-gray-500 mb-1">
                  To: {reply.to}
                </div>
                <div className="whitespace-pre-wrap">{reply.body}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Buttons for auto-draft and send */}
      <div className="mb-2 flex gap-2">
        <button
          className={`bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 ${loading ? "animate-pulse" : ""}`}
          onClick={handleAutoDraft}
          disabled={loading}
        >
          {loading ? "Generating..." : "Auto-draft reply"}
        </button>
        <button
          className="bg-teal-500 text-white px-4 py-2 rounded hover:bg-teal-600 disabled:opacity-50"
          onClick={handleSend}
          disabled={!replyDraft.trim()}
        >
          Send
        </button>
      </div>

      {/* Reply text area */}
      <textarea
        ref={textareaRef}
        className="w-full p-2 border border-gray-300 rounded resize-none overflow-hidden focus:outline-none focus:ring focus:border-blue-300"
        placeholder="Reply will appear here..."
        value={replyDraft}
        onChange={handleReplyChange}
        rows={1}
      />

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="fixed inset-0 flex items-center justify-center backdrop-blur-sm z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-md mb-128">
            <h2 className="text-lg font-semibold mb-2">Add clinician notes (optional)</h2>
            <textarea
              className="w-full border border-gray-300 rounded p-2 mb-4"
              rows={4}
              placeholder="Type any notes or instructions to guide the AI in generating the reply..."
              value={notes}
              onChange={e => setNotes(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <button
                className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
                onClick={() => setShowNotesModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700"
                onClick={handleSubmitNotes}
                disabled={loading}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
