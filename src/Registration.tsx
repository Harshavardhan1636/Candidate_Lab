import { useState, type FormEvent } from "react";
import { api } from "./api";
import { Button, Field, Notice } from "./components";

export function Registration({
  created,
  cancel,
}: {
  created: (email: string) => void;
  cancel: () => void;
}) {
  const [role, setRole] = useState("candidate");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [code, setCode] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [invalid, setInvalid] = useState("");
  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setInvalid("");
    const problem = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
      ? ["register-email", "Enter a valid email address."]
      : password.length < 12 ||
          !/[a-z]/i.test(password) ||
          !/\d/.test(password) ||
          password !== password.trim()
        ? [
            "register-password",
            "Use at least 12 characters with a letter and a number, without leading or trailing spaces.",
          ]
        : password !== confirm
          ? ["register-confirm", "Passwords do not match."]
          : role !== "candidate" && !code.trim()
            ? [
                "register-code",
                "Enter the invitation code supplied by your administrator.",
              ]
            : null;
    if (problem) {
      setInvalid(problem[0]);
      setError(problem[1]);
      document.getElementById(problem[0])?.focus();
      return;
    }
    setBusy(true);
    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim(),
          password,
          confirm_password: confirm,
          role,
          invitation_code: code.trim(),
        }),
      });
      created(email.trim().toLowerCase());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h2>Create your account</h2>
      <p className="muted">
        Candidates can join directly. Recruiters and auditors need an
        administrator invitation.
      </p>
      <form noValidate onSubmit={submit}>
        {error && <Notice error message={error} />}
        <Field id="register-role" label="Account role">
          <select
            id="register-role"
            value={role}
            disabled={busy}
            onChange={(e) => {
              setRole(e.target.value);
              setCode("");
              setError("");
              setInvalid("");
            }}
          >
            <option value="candidate">Candidate</option>
            <option value="recruiter">Recruiter — invitation required</option>
            <option value="auditor">Auditor — invitation required</option>
          </select>
        </Field>
        <Field
          id="register-email"
          label="Email"
          error={invalid === "register-email" ? error : undefined}
        >
          <input
            id="register-email"
            type="email"
            autoComplete="email"
            maxLength={120}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={busy}
          />
        </Field>
        <Field
          id="register-password"
          label="New password"
          help="At least 12 characters, including a letter and a number."
          error={invalid === "register-password" ? error : undefined}
        >
          <input
            id="register-password"
            type={show ? "text" : "password"}
            autoComplete="new-password"
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={busy}
          />
        </Field>
        <Field
          id="register-confirm"
          label="Confirm password"
          error={invalid === "register-confirm" ? error : undefined}
        >
          <input
            id="register-confirm"
            type={show ? "text" : "password"}
            autoComplete="new-password"
            maxLength={128}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            disabled={busy}
          />
        </Field>
        <Button
          variant="ghost"
          type="button"
          aria-pressed={show}
          onClick={() => setShow(!show)}
        >
          {show ? "Hide passwords" : "Show passwords"}
        </Button>
        {role !== "candidate" && (
          <Field
            id="register-code"
            label="Invitation code"
            help="Bound to this email and role. Codes expire and can be used once."
            error={invalid === "register-code" ? error : undefined}
          >
            <input
              id="register-code"
              type="password"
              autoComplete="off"
              maxLength={200}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              disabled={busy}
            />
          </Field>
        )}
        <p className="small muted">
          This is a shared local research workspace. Recruiters can review saved
          candidate profiles. Email ownership verification is not enabled in
          this local version.
        </p>
        <Button type="submit" busy={busy} className="full">
          Create account
        </Button>
        <Button
          type="button"
          variant="ghost"
          className="full"
          disabled={busy}
          onClick={cancel}
        >
          Back to sign in
        </Button>
      </form>
    </>
  );
}
