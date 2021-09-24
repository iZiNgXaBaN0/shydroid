CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer PRIMARY KEY,
    Prefix DEFAULT "$"
);

CREATE TABLE IF NOT EXISTS exp (
    UserID integer PRIMARY KEY,
    xp integer DEFAULT 0,
    level integer DEFAULT 0,
    xplock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutes (
    UserID integer PIRIMARY KEY,
    RoleIDs text,
    EndTime text
);

CREATE TABLE IF NOT EXISTS reactions (
    message_id integer PRIMARY KEY,
    emoji_id integer,
    role_nale text
);