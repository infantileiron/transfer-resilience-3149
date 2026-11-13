-- Report versions are bound to the accepted review and evidence snapshot they were
-- archived from. SQLAlchemy create_all only creates new tables; existing deployments
-- must run this ALTER before starting the new backend.
ALTER TABLE network_reports
  MODIFY run_id VARCHAR(80) NOT NULL,
  ADD COLUMN review_id VARCHAR(80) NULL,
  ADD COLUMN version INT NOT NULL DEFAULT 1,
  ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'valid',
  ADD COLUMN invalidated_at VARCHAR(64) NOT NULL DEFAULT '',
  ADD COLUMN invalidated_by VARCHAR(160) NOT NULL DEFAULT '',
  ADD COLUMN invalidated_reason TEXT,
  ADD COLUMN invalidated_review_id VARCHAR(80) NOT NULL DEFAULT '',
  ADD COLUMN accepted_note TEXT,
  ADD COLUMN accepted_author VARCHAR(160) NOT NULL DEFAULT '',
  ADD COLUMN result_checksum VARCHAR(80) NOT NULL DEFAULT '',
  ADD COLUMN snapshot JSON,
  DROP INDEX uq_network_reports_run_id;

-- Bind each legacy report to its run's latest accepted review. Reports whose run has
-- no accepted review stay NULL; the service treats them as unbindable (export falls
-- back to the run result, but any new review invalidates them).
UPDATE network_reports r
JOIN network_runs n ON n.id = r.run_id
JOIN resilience_reviews v ON v.id = (
  SELECT v2.id FROM resilience_reviews v2
  WHERE v2.run_id = n.id AND v2.decision = 'accepted'
  ORDER BY v2.created_at DESC, v2.id DESC LIMIT 1
)
SET r.review_id = v.id,
    r.accepted_note = v.note,
    r.accepted_author = v.author,
    r.version = 1,
    r.status = 'valid';

ALTER TABLE network_reports
  ADD CONSTRAINT uq_network_reports_review UNIQUE (review_id),
  ADD CONSTRAINT uq_network_reports_run_version UNIQUE (run_id, version);
