"""Local administrator tool. Never expose invitation creation as a public endpoint."""
import argparse
from sqlalchemy.orm import Session
from .app import Base, engine, create_invitation

def main():
    parser = argparse.ArgumentParser(description="Create a single-use, email-bound role invitation.")
    parser.add_argument('--email', required=True)
    parser.add_argument('--role', choices=['recruiter', 'auditor'], required=True)
    parser.add_argument('--hours', type=int, default=24)
    args = parser.parse_args()
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            token = create_invitation(session, args.email, args.role, args.hours)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Invitation for {args.email}, role {args.role}, valid {args.hours} hours (one use):")
    print(token)
    print('Share privately with the intended user. Only its hash is stored.')

if __name__ == '__main__':
    main()
