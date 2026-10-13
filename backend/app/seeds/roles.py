from app.database import SessionLocal
from app.models.role import Role


def seed_roles():

    db = SessionLocal()

    roles = [
        "ADMIN",
        "SECURITY_ANALYST",
        "VIEWER"
    ]

    for role_name in roles:

        print("Checking:", role_name)

        existing_role = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if not existing_role:
            print("Creating:", role_name)

            db.add(
                Role(name=role_name)
            )

    db.commit()

    print("Commit completed")

    db.close()


if __name__ == "__main__":
    seed_roles()