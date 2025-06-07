// This is rather hacky, but it works for now.
export interface EmailPart {
  id: string;
  from: string;
  patient_name: string;
  subject: string;
}

export interface SentEmail {
    id: string;
    parent: string;
    to: string;
    subject: string;
    body: string;
}

export interface Email extends EmailPart {
  body: string;
  replies: SentEmail[];
}