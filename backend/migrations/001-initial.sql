-- Initial schema comes from versioned SQLAlchemy metadata.
-- TransferArc unique(dataset_id,arc_id); endpoints can repeat/reverse without losing edge identity.
-- Scenario stores an immutable arc snapshot. Production requires reviewed ALTER migrations.
SELECT 1;
