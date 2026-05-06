"""add_status_factura_catalog

Revision ID: 9b2c1d4e5f60
Revises: e018f2708813
Create Date: 2026-05-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9b2c1d4e5f60"
down_revision = "e018f2708813"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "status_factura",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_status_factura_nombre"),
    )
    op.create_index(
        op.f("ix_status_factura_id"), "status_factura", ["id"], unique=False
    )

    op.execute(
        """
        INSERT INTO status_factura (id, nombre, descripcion, activo)
        VALUES
            (1, 'pendiente', 'Factura pendiente de pago', true),
            (2, 'pagada', 'Factura pagada', true),
            (3, 'anulada', 'Factura anulada', true)
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('status_factura', 'id'),
            (SELECT MAX(id) FROM status_factura)
        )
        """
    )

    op.add_column(
        "facturas",
        sa.Column(
            "id_status",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE facturas
        SET id_status = CASE
            WHEN pagada IS TRUE THEN 2
            ELSE 1
        END
        """
    )
    op.execute(
        """
        UPDATE facturas
        SET id_status = 3
        WHERE id IN (
            SELECT DISTINCT factura_id
            FROM anulaciones
        )
        """
    )

    op.alter_column("facturas", "id_status", nullable=False)
    op.create_foreign_key(
        "fk_facturas_id_status_status_factura",
        "facturas",
        "status_factura",
        ["id_status"],
        ["id"],
    )
    op.drop_column("facturas", "pagada")


def downgrade():
    op.add_column(
        "facturas",
        sa.Column("pagada", sa.Boolean(), nullable=True),
    )
    op.execute(
        """
        UPDATE facturas
        SET pagada = CASE
            WHEN id_status = 2 THEN true
            ELSE false
        END
        """
    )

    op.drop_constraint(
        "fk_facturas_id_status_status_factura",
        "facturas",
        type_="foreignkey",
    )
    op.drop_column("facturas", "id_status")
    op.drop_index(op.f("ix_status_factura_id"), table_name="status_factura")
    op.drop_table("status_factura")
