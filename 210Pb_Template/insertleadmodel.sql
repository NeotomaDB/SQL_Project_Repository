CREATE TABLE IF NOT EXISTS ndb.leadmodelbasis (
    pbbasisid SERIAL PRIMARY KEY,
    pbbasis text);
INSERT INTO ndb.leadmodelbasis (pbbasis) VALUES ('asymptote of alpha'),('gamma point-subtraction'),('gamma average');

CREATE TABLE IF NOT EXISTS ndb.leadmodels
(pbbasisid INT REFERENCES ndb.leadmodelbasis(pbbasisid),
 analysisunitid INT REFERENCES ndb.analysisunits(analysisunitid),
 cumulativeinventory NUMERIC CHECK (cumulativeinventory > 0));