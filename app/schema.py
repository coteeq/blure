schema_up = [
    '''
    CREATE TABLE IF NOT EXISTS pics (
        id SERIAL PRIMARY KEY UNIQUE,
        src_url VARCHAR(1024),
        content_type VARCHAR(256),
        deleted BOOLEAN
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS tags (
        id SERIAL NOT NULL PRIMARY KEY,
        tag_name VARCHAR(128)
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS tags_pics (
        pic_id INT NOT NULL,
        tag_id INT NOT NULL,
        PRIMARY KEY (pic_id, tag_id),
        FOREIGN KEY (pic_id) REFERENCES pics(id) ON UPDATE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON UPDATE CASCADE
    );
    '''
]

schema_down = [
    'DROP TABLE tags_pics',
    'DROP TABLE tags',
    'DROP TABLE pics'
]

schema_delete = [
    'DELETE * FROM tags_pics'
    'DELETE * FROM tags'
    'DELETE * FROM pics'
]
