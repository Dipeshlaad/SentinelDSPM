"""normalize role ids

Revision ID: 2f609fe29f33
Revises: d35d96696bcd
Create Date: 2026-09-21 03:32:41.624446

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2f609fe29f33"
down_revision: Union[str, Sequence[str], None] = "d35d96696bcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Normalize role IDs while preserving all user and
    role-permission relationships.
    """

    connection = op.get_bind()

    # Temporarily remove foreign keys that reference roles.id.
    connection.exec_driver_sql(
        """
        ALTER TABLE users
        DROP CONSTRAINT users_role_id_fkey
        """
    )

    connection.exec_driver_sql(
        """
        ALTER TABLE role_permissions
        DROP CONSTRAINT role_permissions_role_id_fkey
        """
    )

    # Move references to temporary IDs.
    connection.exec_driver_sql(
        """
        UPDATE users
        SET role_id = CASE role_id
            WHEN 2 THEN 102
            WHEN 3 THEN 103
            WHEN 5 THEN 105
            WHEN 6 THEN 106
            ELSE role_id
        END
        """
    )

    connection.exec_driver_sql(
        """
        UPDATE role_permissions
        SET role_id = CASE role_id
            WHEN 2 THEN 102
            WHEN 3 THEN 103
            WHEN 5 THEN 105
            WHEN 6 THEN 106
            ELSE role_id
        END
        """
    )

    # Move roles to temporary IDs.
    connection.exec_driver_sql(
        """
        UPDATE roles
        SET id = CASE id
            WHEN 2 THEN 102
            WHEN 3 THEN 103
            WHEN 5 THEN 105
            WHEN 6 THEN 106
            ELSE id
        END
        """
    )

    # Move roles to final IDs:
    #
    # 105 SYSTEM_ADMIN     -> 1
    # 106 TENANT_ADMIN     -> 2
    # 102 SECURITY_ANALYST -> 3
    # 103 VIEWER           -> 4
    connection.exec_driver_sql(
        """
        UPDATE roles
        SET id = CASE id
            WHEN 102 THEN 3
            WHEN 103 THEN 4
            WHEN 105 THEN 1
            WHEN 106 THEN 2
            ELSE id
        END
        """
    )

    # Update user references to final IDs.
    connection.exec_driver_sql(
        """
        UPDATE users
        SET role_id = CASE role_id
            WHEN 102 THEN 3
            WHEN 103 THEN 4
            WHEN 105 THEN 1
            WHEN 106 THEN 2
            ELSE role_id
        END
        """
    )

    # Update role-permission references to final IDs.
    connection.exec_driver_sql(
        """
        UPDATE role_permissions
        SET role_id = CASE role_id
            WHEN 102 THEN 3
            WHEN 103 THEN 4
            WHEN 105 THEN 1
            WHEN 106 THEN 2
            ELSE role_id
        END
        """
    )

    # Recreate foreign keys.
    connection.exec_driver_sql(
        """
        ALTER TABLE users
        ADD CONSTRAINT users_role_id_fkey
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        """
    )

    connection.exec_driver_sql(
        """
        ALTER TABLE role_permissions
        ADD CONSTRAINT role_permissions_role_id_fkey
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        """
    )


def downgrade() -> None:
    """
    Restore the previous role IDs.
    """

    connection = op.get_bind()

    # Temporarily remove foreign keys.
    connection.exec_driver_sql(
        """
        ALTER TABLE users
        DROP CONSTRAINT users_role_id_fkey
        """
    )

    connection.exec_driver_sql(
        """
        ALTER TABLE role_permissions
        DROP CONSTRAINT role_permissions_role_id_fkey
        """
    )

    # Move references to temporary IDs.
    connection.exec_driver_sql(
        """
        UPDATE users
        SET role_id = CASE role_id
            WHEN 1 THEN 105
            WHEN 2 THEN 106
            WHEN 3 THEN 102
            WHEN 4 THEN 103
            ELSE role_id
        END
        """
    )

    connection.exec_driver_sql(
        """
        UPDATE role_permissions
        SET role_id = CASE role_id
            WHEN 1 THEN 105
            WHEN 2 THEN 106
            WHEN 3 THEN 102
            WHEN 4 THEN 103
            ELSE role_id
        END
        """
    )

    connection.exec_driver_sql(
        """
        UPDATE roles
        SET id = CASE id
            WHEN 1 THEN 105
            WHEN 2 THEN 106
            WHEN 3 THEN 102
            WHEN 4 THEN 103
            ELSE id
        END
        """
    )

    # Restore original IDs.
    connection.exec_driver_sql(
        """
        UPDATE roles
        SET id = CASE id
            WHEN 102 THEN 2
            WHEN 103 THEN 3
            WHEN 105 THEN 5
            WHEN 106 THEN 6
            ELSE id
        END
        """
    )

    connection.exec_driver_sql(
        """
        UPDATE users
        SET role_id = CASE role_id
            WHEN 102 THEN 2
            WHEN 103 THEN 3
            WHEN 105 THEN 5
            WHEN 106 THEN 6
            ELSE role_id
        END
        """
    )

    connection.exec_driver_sql(
        """
        UPDATE role_permissions
        SET role_id = CASE role_id
            WHEN 102 THEN 2
            WHEN 103 THEN 3
            WHEN 105 THEN 5
            WHEN 106 THEN 6
            ELSE role_id
        END
        """
    )

    # Recreate foreign keys.
    connection.exec_driver_sql(
        """
        ALTER TABLE users
        ADD CONSTRAINT users_role_id_fkey
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        """
    )

    connection.exec_driver_sql(
        """
        ALTER TABLE role_permissions
        ADD CONSTRAINT role_permissions_role_id_fkey
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        """
    )