START TRANSACTION;

DROP TABLE IF EXISTS Path;
DROP TABLE IF EXISTS File;
DROP TABLE IF EXISTS basefiles;
DROP TABLE IF EXISTS Job;

CREATE TABLE Path
(
    PathId            SERIAL      NOT NULL,
    Path              TEXT        NOT NULL,
    PRIMARY KEY (PathId)
);

ALTER TABLE Path ALTER COLUMN Path SET STATISTICS 1000;
CREATE UNIQUE INDEX path_name_idx ON Path (Path);

CREATE TABLE File (
   FileId           BIGSERIAL   NOT NULL,
   FileIndex        INTEGER     NOT NULL  DEFAULT 0,
   JobId            INTEGER     NOT NULL,
   PathId           INTEGER     NOT NULL,
   DeltaSeq         SMALLINT    NOT NULL  DEFAULT 0,
   MarkId           INTEGER     NOT NULL  DEFAULT 0,
   Fhinfo           NUMERIC(20) NOT NULL  DEFAULT 0,
   Fhnode           NUMERIC(20) NOT NULL  DEFAULT 0,
   LStat            TEXT        NOT NULL,
   Md5              TEXT        NOT NULL DEFAULT '0',
   Name             TEXT        NOT NULL,
   PRIMARY KEY (FileId)
);

CREATE TABLE basefiles
(
    BaseId            BIGSERIAL   NOT NULL,
    JobId             INTEGER     NOT NULL,
    FileId            BIGINT      NOT NULL,
    FileIndex         INTEGER,
    BaseJobId         INTEGER,
    PRIMARY KEY (BaseId)
);

CREATE INDEX file_jpfid_idx ON File (JobId, PathId, Name);
-- This index is important for bvfs performance, especially
-- for .bvfs_lsdirs which is used by bareos-webui.
-- As it's a partial index, it will only contain data from
-- from accurate jobs with delete directories, so that the
-- impact on backups will be low. Nevertheless, it will
-- improve the performance, even when not using accurate.
CREATE INDEX file_pjidpart_idx ON File(PathId,JobId) WHERE FileIndex = 0 AND Name = '';
CREATE INDEX basefiles_jobid_idx ON BaseFiles (JobId);

CREATE TABLE Job
(
    JobId             SERIAL      NOT NULL,
    Job               TEXT        NOT NULL,
    Name              TEXT        NOT NULL,
    Type              CHAR(1)     NOT NULL,
    Level             CHAR(1)     NOT NULL,
    ClientId          INTEGER     DEFAULT 0,
    JobStatus         CHAR(1)     NOT NULL,
    SchedTime         TIMESTAMP   WITHOUT TIME ZONE,
    StartTime         TIMESTAMP   WITHOUT TIME ZONE,
    EndTime           TIMESTAMP   WITHOUT TIME ZONE,
    RealEndTime       TIMESTAMP   WITHOUT TIME ZONE,
    JobTDate          BIGINT      DEFAULT 0,
    VolSessionId      INTEGER     DEFAULT 0,
    volSessionTime    INTEGER     DEFAULT 0,
    JobFiles          INTEGER     DEFAULT 0,
    JobBytes          BIGINT      DEFAULT 0,
    ReadBytes         BIGINT      DEFAULT 0,
    JobErrors         INTEGER     DEFAULT 0,
    JobMissingFiles   INTEGER     DEFAULT 0,
    PoolId            INTEGER     DEFAULT 0,
    FilesetId         INTEGER     DEFAULT 0,
    PriorJobid        INTEGER     DEFAULT 0,
    PurgedFiles       SMALLINT    DEFAULT 0,
    HasBase           SMALLINT    DEFAULT 0,
    HasCache          SMALLINT    DEFAULT 0,
    Reviewed          SMALLINT    DEFAULT 0,
    Comment           TEXT,
    PRIMARY KEY (JobId)
);

INSERT into Job (JobId, Job, Name, Type, Level, JobStatus, JobTDate)
VALUES (1, 'some job', 'job-1', 'B', 'F', 'T', 0),
       (2, 'some job', 'job-2', 'B', 'D', 'T', 1),
       (3, 'some job', 'job-3', 'B', 'I', 'T', 2);
\copy File(FileIndex, JobId, PathId, LStat, name) FROM 'test.full' (DELIMITER '|', FORMAT csv);
\copy File(FileIndex, JobId, PathId, LStat, name) FROM 'test.diff' (DELIMITER '|', FORMAT csv);
\copy File(FileIndex, JobId, PathId, LStat, name) FROM 'test.incr' (DELIMITER '|', FORMAT csv);
\copy Path(PathId, Path) FROM 'test.pid' (DELIMITER '|', FORMAT csv);

COMMIT;
