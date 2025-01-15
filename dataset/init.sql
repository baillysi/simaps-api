CREATE EXTENSION IF NOT EXISTS POSTGIS;

CREATE TABLE hikes (
id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
distance INTEGER,
created_at DATE,
zone_id INTEGER,
gpx GEOGRAPHY,
description VARCHAR,
elevation INTEGER,
difficulty INTEGER,
journey_id INTEGER,
duration INTEGER
);

CREATE TABLE journeys (
id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL
);

CREATE TABLE zones (
id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
location GEOGRAPHY
);

ALTER TABLE hikes ADD CONSTRAINT 
fk_journey
FOREIGN KEY(journey_id)
REFERENCES journeys(id);

ALTER TABLE hikes ADD CONSTRAINT 
fk_zone
FOREIGN KEY(zone_id)
REFERENCES zones(id);

INSERT INTO journeys (name)  values ('boucle'), ('aller-retour'), ('traversée');

INSERT INTO zones (name, location) values 
('mafate', ST_SetSRID(ST_MakePoint(-21.06552268692713, 55.41060302018579),4326)), -- bronchard
('cilaos', ST_SetSRID(ST_MakePoint(-21.132974787127466, 55.45093620179954),4326)), -- chapelle
('salazie', ST_SetSRID(ST_MakePoint(-21.043330291617757, 55.502457528973466),4326)), -- anchaing
('volcan', ST_SetSRID(ST_MakePoint(-21.244991807336334, 55.71769731708017),4326)), -- dolomieu
('plaines', ST_SetSRID(ST_MakePoint(-21.189560906941306, 55.53414567309029),4326)), -- belvédère grand bassin
('piton des neiges', ST_SetSRID(ST_MakePoint(-21.095931684860805, 55.47533899257507),4326)), -- piton des neiges
('nord', ST_SetSRID(ST_MakePoint(-21.014813193273675, 55.46061069314457),4326)), -- roche écrite
('sud', ST_SetSRID(ST_MakePoint(-21.309346611479455, 55.65000271810099),4326)), -- grand galet
('est', ST_SetSRID(ST_MakePoint(-21.08870651252871, 55.614487810203116),4326)), -- takamaka
('ouest', ST_SetSRID(ST_MakePoint(-21.11611928787351, 55.42304040778952),4326)); -- grand bénare
 
INSERT INTO hikes (name, distance, created_at, zone_id, gpx, description, elevation, difficulty, journey_id, duration) values
('Canalisation des orangers', 12, CURRENT_DATE, 1, null, 'Description', 500, 2, 2, 5);



