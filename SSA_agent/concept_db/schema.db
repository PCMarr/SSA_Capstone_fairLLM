CREATE TABLE IF NOT EXISTS sources(
    source_id INTEGER PRIMARY KEY ASC,
    title TEXT NOT NULL,
    content TEXT,
    source TEXT,
    date TEXT,
    link TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS actors(
    actor_id INTEGER PRIMARY KEY ASC,
    actor TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS concepts(
    concept_id INTEGER PRIMARY KEY ASC,
    concept TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pairs(
    pair_id INTEGER PRIMARY KEY ASC,
    source_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    FOREIGN KEY (source_id)
    REFERENCES sources (source_id)
        ON UPDATE cascade
        ON DELETE cascade,
    FOREIGN KEY (concept_id)
    REFERENCES concepts (concept_id)
        ON UPDATE cascade
        ON DELETE cascade,
    FOREIGN KEY (actor_id)
    REFERENCES actors (actor_id)
        ON UPDATE cascade
        ON DELETE cascade
);

INSERT INTO actors (actor) VALUES
                    ("United States"),
                    ("China"),
                    ("Russia"),
                    ("France"),
                    ("UK"),
                    ("NATO"),
                    ("United Nations"),
                    ("SpaceX");

INSERT INTO concepts (concept) VALUES
                    ("space as a common resource"),
                    ("governing orbital sustainability"),
                    ("profit"), 
                    ("international cooperation"),
                    ("science and innovation"),
                    ("national economic gains"),
                    ("societal development"),
                    ("diplomatic tool");