import sqlite3

__all__ = ['DB']


class DB:
    def __init__(self):
        self.char = 'DataBase/Characters.sqlite'
        self.save = 'Save/Save.sqlite'

    def init_life(self, key):
        conn = sqlite3.connect(self.char)
        cur = conn.cursor()
        key = key.lower()
        cur.execute("SELECT * FROM characters WHERE id LIKE '%s'" % (key,))
        out = cur.fetchone()
        cur.close()
        conn.close()
        return out[1:8]

    def init_hero(self, key):
        conn = sqlite3.connect(self.char)
        cur = conn.cursor()
        cur.execute("SELECT * FROM characters WHERE id LIKE '%s'" % (key,))
        out = cur.fetchone()
        cur.close()
        conn.close()
        return out[8:]

    def all_save(self) -> list:
        conn = sqlite3.connect(self.save)
        cur = conn.cursor()
        cur.execute("SELECT * FROM save")
        out = []
        row = cur.fetchone()
        while row is not None:
            out.append(row)
            row = cur.fetchone()
        cur.close()
        conn.close()
        return out

    def delete(self, key):
        conn = sqlite3.connect(self.save)
        cur = conn.cursor()
        cur.execute("""DELETE FROM save WHERE key = {}""".format(key))
        conn.commit()
        cur.close()
        conn.close()

    def override(self, key, data):
        conn = sqlite3.connect(self.save)
        cur = conn.cursor()
        cur.execute("""DELETE FROM save WHERE key = {}""".format(key))
        cur.execute("""
                INSERT INTO save
                VALUES (
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}'
                )
                """.format(key, *data))
        conn.commit()
        cur.close()
        conn.close()

    def new_save(self, key, data):
        conn = sqlite3.connect(self.save)
        cur = conn.cursor()
        cur.execute("""
                INSERT INTO save
                VALUES (
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                    '{}', '{}', '{}'
                )
                """.format(key, *data))
        conn.commit()
        cur.close()
        conn.close()


# if __name__ == '__main__':
#     d = DB()
#     conn = sqlite3.connect(d.save)
#     cur = conn.cursor()
#     cur.execute("""
# CREATE TABLE save (
#     [key]               INT,
#     time                TEXT,
#     map                 TEXT,
#     pos_x               INT,
#     pos_y               INT,
#     name_1              TEXT,
#     id_1                TEXT,
#     hp_1                INT,
#     hp_max_1            INT,
#     mp_1                INT,
#     mp_max_1            INT,
#     sp_1                INT,
#     sp_max_1            INT,
#     attack_name_1_1     TEXT,
#     attack_size_1_1     INT,
#     attack_cost_1_1     INT,
#     attack_atr_type_1_1 TEXT,
#     attack_defence_1_1  TEXT,
#     attack_name_2_1     TEXT,
#     attack_size_2_1     INT,
#     attack_cost_2_1     INT,
#     attack_atr_type_2_1 TEXT,
#     attack_defence_2_1  TEXT,
#     defense_name_1_1    TEXT,
#     defense_size_1_1    TEXT,
#     defense_name_2_1    TEXT,
#     defense_size_2_1    TEXT,
#     name_2              TEXT,
#     id_2                TEXT,
#     hp_2                INT,
#     hp_max_2            INT,
#     mp_2                INT,
#     mp_max_2            INT,
#     sp_2                INT,
#     sp_max_2            INT,
#     attack_name_1_2     TEXT,
#     attack_size_1_2     INT,
#     attack_cost_1_2     INT,
#     attack_atr_type_1_2 TEXT,
#     attack_defence_1_2  TEXT,
#     attack_name_2_2     TEXT,
#     attack_size_2_2     INT,
#     attack_cost_2_2     INT,
#     attack_atr_type_2_2 TEXT,
#     attack_defence_2_2  TEXT,
#     defense_name_1_2    TEXT,
#     defense_size_1_2    TEXT,
#     defense_name_2_2    TEXT,
#     defense_size_2_2    TEXT,
#     name_3              TEXT,
#     id_3                TEXT,
#     hp_3                INT,
#     hp_max_3            INT,
#     mp_3                INT,
#     mp_max_3            INT,
#     sp_3                INT,
#     sp_max_3            INT,
#     attack_name_1_3     TEXT,
#     attack_size_1_3     INT,
#     attack_cost_1_3     INT,
#     attack_atr_type_1_3 TEXT,
#     attack_defence_1_3  TEXT,
#     attack_name_2_3     TEXT,
#     attack_size_2_3     INT,
#     attack_cost_2_3     INT,
#     attack_atr_type_2_3 TEXT,
#     attack_defence_2_3  TEXT,
#     defense_name_1_3    TEXT,
#     defense_size_1_3    TEXT,
#     defense_name_2_3    TEXT,
#     defense_size_2_3    TEXT,
#     name_4              TEXT,
#     id_4                TEXT,
#     hp_4                INT,
#     hp_max_4            INT,
#     mp_4                INT,
#     mp_max_4            INT,
#     sp_4                INT,
#     sp_max_4            INT,
#     attack_name_1_4     TEXT,
#     attack_size_1_4     INT,
#     attack_cost_1_4     INT,
#     attack_atr_type_1_4 TEXT,
#     attack_defence_1_4  TEXT,
#     attack_name_2_4     TEXT,
#     attack_size_2_4     INT,
#     attack_cost_2_4     INT,
#     attack_atr_type_2_4 TEXT,
#     attack_defence_2_4  TEXT,
#     defense_name_1_4    TEXT,
#     defense_size_1_4    TEXT,
#     defense_name_2_4    TEXT,
#     defense_size_2_4    TEXT
# )
#     """)
#     conn.commit()
#     cur.close()
#     conn.close()
