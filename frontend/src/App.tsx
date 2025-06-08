import { useEffect, useState } from "react";
import type { Email, EmailPart } from './types';
import EmailDetail from "./EmailDetail.tsx";

import InboxIcon from './assets/inbox.svg';
import TrashIcon from './assets/trash.svg';

const mailboxes = ["inbox", "trash"];
const mailboxIcons = {
  inbox: InboxIcon,
  trash: TrashIcon,
};

function App() {
  const [selectedMailbox, setSelectedMailbox] = useState("inbox");
  const [emails, setEmails] = useState<EmailPart[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);

  useEffect(() => {
    if (selectedMailbox === "trash") {
      setEmails([]);
      setSelectedEmail(null);
    } else {
      fetch(`http://localhost:8000/emails`)
        .then(res => res.json())
        .then(data => {
          setEmails(data as EmailPart[]|| []);
          setSelectedEmail(null);
        });
      }
  }, [selectedMailbox]);

  const handleSelectEmail = (email: EmailPart) => {
    setSelectedEmail(null);
    fetch(`http://localhost:8000/emails/${email.id}`)
      .then(res => res.json())
      .then(data => {
        const fullEmail: Email = data as Email;
        setSelectedEmail(fullEmail);
      });
  };

  return (
    <div className="flex h-screen w-screen">

      {/* Left: Mailbox selector */}
      <div className="w-1/6 bg-zinc-100 p-4 border-r border-zinc-400">
        <h2 className="font-bold mb-4 text-zinc-500">Mailboxes</h2>
        {mailboxes.map(box => (
          <button
            key={box}
            className={`mb-2 flex items-center w-full px-3 py-2 rounded hover:bg-zinc-200 transition ${
              selectedMailbox === box ? "bg-zinc-200 font-medium" : ""
            }`}
            onClick={() => setSelectedMailbox(box)}
          >
            <img src={mailboxIcons[box]} alt={`${box} icon`} className="w-5 h-5 mr-3" />
            <span>{box.charAt(0).toUpperCase() + box.slice(1)}</span>
          </button>
        ))}
      </div>

      {/* Middle: Email list */}
      <div className="w-1/4 p-4 border-r border-zinc-400 overflow-y-auto bg-zinc-50">
        <h2 className="font-bold mb-4 text-zinc-500 capitalize">{selectedMailbox}</h2>
        {emails.map(email => (
          <div
            key={email.id}
            className={`p-2 mb-1 rounded cursor-pointer hover:bg-zinc-200 ${
              selectedEmail?.id === email.id ? "bg-zinc-200" : ""
            }`}
            onClick={() => handleSelectEmail(email)}
          >
            <div className="font-semibold text-gray-700">{email.patient_name}</div>
            <div className="text-sm text-gray-700 truncate">{email.subject}</div>
          </div>
        ))}
      </div>

      {/* Right: Email detail */}
      <div className="flex-1 p-6 overflow-y-auto bg-white text-zinc-800">
        <EmailDetail 
          email={selectedEmail}
          refreshEmail={() => selectedEmail && handleSelectEmail(selectedEmail)}
        />
      </div>
    </div>
  );
}

export default App;
