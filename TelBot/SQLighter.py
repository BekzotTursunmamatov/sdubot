import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_timetable(self, course, group_name, day):
        print("Database ", course, group_name, day)
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute("SELECT %s FROM '%s' WHERE group_name = '%s';" % (day, course, group_name)).fetchall()

    def select_week(self, course, group_name):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute("SELECT monday, tuesday, wednesday, thursday, friday FROM '%s' WHERE group_name = '%s'"% (course, group_name)).fetchall()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM faculty').fetchall()

    def select_all_groups(self,fac):
        print(fac,"alala")
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute("SELECT group_name, advisor FROM groups WHERE group_faculty = '%s'"% (fac)).fetchall()

    def select_all_advisors(self,gname):
        print(gname,"advisor")
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute("SELECT  advisor FROM groups WHERE group_name = '%s'"% (gname)).fetchall()

    def select_single(self, rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM faculty WHERE id = ?', (rownum,)).fetchall()[0]

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM faculty').fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()