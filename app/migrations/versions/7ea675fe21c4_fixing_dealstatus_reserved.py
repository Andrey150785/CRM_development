"""fixing dealstatus reserved

Revision ID: 7ea675fe21c4
Revises: 847c5bd9598c
Create Date: 2026-06-28 13:40:38.853143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ea675fe21c4'
down_revision: Union[str, Sequence[str], None] = '847c5bd9598c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем новое значение в тип
    op.execute("DELETE FROM deals WHERE status = 'reserved'")


def downgrade():
    op.execute("""
        ALTER TABLE deals
            ALTER COLUMN status TYPE VARCHAR(50)
    """)
    op.execute("DROP TYPE dealstatus")
    op.execute("""
        CREATE TYPE dealstatus AS ENUM (
            'on_sale',
            'reservation',
            'confirmed',
            'signing',
            'payment',
            'completed',
            'canceled'
        )
    """)
    op.execute("UPDATE deals SET status = 'reservation' WHERE status = 'reserved'")
    op.execute("""
        ALTER TABLE deals
            ALTER COLUMN status TYPE dealstatus USING status::dealstatus
    """)
