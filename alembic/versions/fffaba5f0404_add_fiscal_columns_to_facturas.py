"""add_fiscal_columns_to_facturas

Revision ID: fffaba5f0404
Revises: ca2541a71011
Create Date: 2026-05-08 14:52:40.758120

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fffaba5f0404'
down_revision = 'ca2541a71011'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("facturas", sa.Column("ncf", sa.String(11), nullable=True))
    op.add_column("facturas", sa.Column("tipo_ncf", sa.String(5), nullable=True))
    op.add_column("facturas", sa.Column("rnc_emisor", sa.String(9), nullable=True))
    op.add_column("facturas", sa.Column("razon_social_emisor", sa.String(200), nullable=True))
    op.add_column("facturas", sa.Column("rnc_cliente", sa.String(9), nullable=True))
    op.add_column("facturas", sa.Column("nombre_cliente_fiscal", sa.String(200), nullable=True))
    op.add_column("facturas", sa.Column("fecha_vencimiento_ncf", sa.Date(), nullable=True))
    op.add_column("facturas", sa.Column("estado_fiscal", sa.String(20), nullable=True))


def downgrade():
    op.drop_column("facturas", "estado_fiscal")
    op.drop_column("facturas", "fecha_vencimiento_ncf")
    op.drop_column("facturas", "nombre_cliente_fiscal")
    op.drop_column("facturas", "rnc_cliente")
    op.drop_column("facturas", "razon_social_emisor")
    op.drop_column("facturas", "rnc_emisor")
    op.drop_column("facturas", "tipo_ncf")
    op.drop_column("facturas", "ncf")
