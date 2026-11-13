import {
  useEffect,
  useRef,
  cloneElement,
  isValidElement,
  type ReactNode,
  type ButtonHTMLAttributes,
} from "react";
import {
  ArrowLeft,
  ArrowRight,
  LoaderCircle,
  Search,
  X,
  AlertCircle,
} from "lucide-react";

export function Button({
  children,
  busy,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  busy?: boolean;
  variant?: "primary" | "secondary" | "ghost";
}) {
  return (
    <button
      {...props}
      className={`button ${variant} ${props.className || ""}`}
      disabled={props.disabled || busy}
      aria-busy={busy || undefined}
    >
      {busy && <LoaderCircle size={16} className="spin" aria-hidden="true" />}
      {children}
    </button>
  );
}
export function Field({
  label,
  id,
  help,
  children,
  error,
}: {
  label: string;
  id: string;
  help?: string;
  children: ReactNode;
  error?: string;
}) {
  const control =
    isValidElement<Record<string, unknown>>(children) &&
    ["input", "textarea", "select"].includes(String(children.type))
      ? cloneElement(children, {
          "aria-invalid": error ? true : undefined,
          "aria-describedby":
            [help && `${id}-help`, error && `${id}-error`]
              .filter(Boolean)
              .join(" ") || undefined,
        })
      : children;
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {help && (
        <p className="help" id={`${id}-help`}>
          {help}
        </p>
      )}
      {control}
      {error && (
        <p className="field-error" id={`${id}-error`}>
          {error}
        </p>
      )}
    </div>
  );
}
export function Panel({
  title,
  action,
  children,
  className = "",
}: {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      {title && (
        <div className="panel-head">
          <h2>{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
export function Notice({
  message,
  error = false,
  onClose,
}: {
  message: string;
  error?: boolean;
  onClose?: () => void;
}) {
  return (
    <div
      className={`notice ${error ? "error" : ""}`}
      role={error ? "alert" : "status"}
    >
      <AlertCircle size={17} aria-hidden="true" />
      <span>{message}</span>
      {onClose && (
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Dismiss message"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <LoaderCircle className="spin" size={22} /> Loading workspace…
    </div>
  );
}
export function Empty({
  title,
  children,
}: {
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      {children}
    </div>
  );
}
export function Pager({
  page,
  total,
  onPage,
}: {
  page: number;
  total: number;
  onPage: (page: number) => void;
}) {
  const pages = Math.max(1, Math.ceil(total / 10));
  return (
    <div className="pager">
      <span>
        {total ? (page - 1) * 10 + 1 : 0}–{Math.min(page * 10, total)} of{" "}
        {total}
      </span>
      <div>
        <Button
          variant="ghost"
          onClick={() => onPage(page - 1)}
          disabled={page <= 1}
        >
          <ArrowLeft size={15} />
          Previous
        </Button>
        <span>
          {page} / {pages}
        </span>
        <Button
          variant="ghost"
          onClick={() => onPage(page + 1)}
          disabled={page >= pages}
        >
          Next
          <ArrowRight size={15} />
        </Button>
      </div>
    </div>
  );
}
export function SearchField({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  const input = useRef<HTMLInputElement>(null);
  return (
    <div className="search">
      <Search size={17} aria-hidden="true" />
      <input
        ref={input}
        aria-label={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
      {value && (
        <button
          className="icon-button"
          aria-label="Clear search"
          onClick={() => {
            onChange("");
            input.current?.focus();
          }}
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
export function Dialog({
  title,
  children,
  close,
}: {
  title: string;
  children: ReactNode;
  close: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const el = ref.current!;
    const active = document.activeElement as HTMLElement;
    el.showModal();
    return () => {
      el.close();
      active?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      aria-labelledby="dialog-title"
      onCancel={(e) => {
        e.preventDefault();
        close();
      }}
    >
      <div className="dialog-title">
        <h2 id="dialog-title">{title}</h2>
        <button
          aria-label="Close dialog"
          className="icon-button"
          onClick={close}
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
