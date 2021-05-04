CREATE TABLE maps (
    map_id serial PRIMARY KEY,
    map_name VARCHAR(15) NOT NULL
);

CREATE TABLE contact_types (
    type_id serial PRIMARY KEY,
    longname VARCHAR(10) 
);

CREATE TABLE teams (
    team_id serial PRIMARY KEY,
    contact VARCHAR(37) NOT NULL,
    team_name VARCHAR(30) NOT NULL,
    contact_type integer REFERENCES contact_types(type_id)
);

CREATE TABLE guild_teams (
    team_id integer PRIMARY KEY REFERENCES teams(team_id),
    guild_id bigint NOT NULL,
    schedule_channel bigint,
    proposal_channel bigint
);

CREATE TABLE scrims (
    scrim_id serial PRIMARY KEY,
    team_id integer REFERENCES teams(team_id),
    played_at timestamp with time zone,
    against integer REFERENCES teams(team_id)  -- If this is NULL then we are still searching.
);

CREATE TABLE matches (
    match_id serial PRIMARY KEY,
    map_id integer REFERENCES maps(map_id),
    scrim_id integer REFERENCES scrims(scrim_id)
);

CREATE TABLE proposals (
    proposal_id serial PRIMARY KEY,
    scrim_id integer REFERENCES scrims(scrim_id),
    team_id integer REFERENCES teams(team_id)
);

CREATE TABLE proposed_matches (
    proposed_match_id serial,
    map_id integer REFERENCES maps(map_id),
    proposal_id integer REFERENCES proposals(proposal_id)
);

INSERT INTO contact_types(longname) VALUES('Discord');

INSERT INTO maps(map_name) VALUES('Not Played');
INSERT INTO maps(map_name) VALUES('Kafe');
INSERT INTO maps(map_name) VALUES('Villa');
INSERT INTO maps(map_name) VALUES('Oregon');
INSERT INTO maps(map_name) VALUES('Coastline');
INSERT INTO maps(map_name) VALUES('Chalet');
INSERT INTO maps(map_name) VALUES('Consulate');
INSERT INTO maps(map_name) VALUES('Clubhouse');

grant all on database siegescheduler TO siegescheduler;
grant all on schema public to siegescheduler;
grant all on all tables in schema public to siegescheduler;
grant all on all sequences in schema public to siegescheduler;
grant all on all functions in schema public to siegescheduler;