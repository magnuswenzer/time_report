
from collections import OrderedDict
import sqlite3
from exceptions import *

class TimeReportDatabase(object):
    """
    Blueprint for database.
    """
    def __init__(self, db_name, *args, **kwargs):
        self.db_name = db_name

        # Database table info with attributes
        self.tables = dict(Employee=OrderedDict(employee_nr='INTEGER',
                                                first_name='TEXT',
                                                last_name='TEXT',
                                                department='TEXT'),
                           Project=OrderedDict(project_nr='INTEGER',
                                               ksts='INTEGER',
                                               project_name='TEXT',
                                               hours_total='INTEGER'),
                           Staffing=OrderedDict(staffing_id='INTEGER',
                                                project_id='INTEGER',
                                                employee_nr='INTEGER',
                                                hours_planed='INTEGER'),
                           TimeReport=OrderedDict(time_report_id='INTEGER',
                                                  date='TEXT',
                                                  project_nr='INTEGER',
                                                  employee_nr='INTEGER',
                                                  hours_reported='INTEGER'))
        # Autoincrement for primary keys
        self.autoincrement = ['time_report_id']

    def __str__(self):
        return f'Database: {self.db_name}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.db_name}'

    def get_tables(self):
        """
        Returns a list of the tabbels in the database.
        :return: list
        """
        return sorted(self.tables)

    def get_attributes_for_table(self, table, all=False):
        """
        Returns the attributes for the fiven table.
        If all=False autoincrements attributes ar excluded.
        :param table: str
        :param all: boolean
        :return:
        """
        return_list = self.tables.get(table)
        if not all:
            return_list = [item for item in return_list if item not in self.autoincrement]
        return return_list

    def create_database(self):
        """
        Creates the database
        :return: None
        """
        raise NotImplementedError

    def add_record_to_table(self, table, **kwargs):
        """
        Adds a record to the give table
        :param table: str
        :param kwargs: keys=attributs
        :return:
        """
        raise NotImplementedError
    
    def check_attributes(self, table, **kwargs):
        """
        Checks so that all attributes ar valid. Raises exceptions if not:
        MissingAttribute
        NonValidAttribute
        :param table:
        :param kwargs:
        :return:
        """
        if sorted(self.get_attributes_for_table(table)) == sorted(kwargs):
            return True
        attr_not_given = [a for a in self.get_attributes_for_table(table) if a not in kwargs]
        if attr_not_given:
            raise MissingAttribute(attr_not_given)
        else:
            non_valid_attr = [a for a in kwargs if a not in self.get_attributes_for_table(table)]
            raise NonValidAttribute(non_valid_attr)

    def convert_kwargs(self, table, **kwargs):

        def get_int(value):
            try:
                value = int(value)
            except:
                value = None
            return value

        def get_str(value):
            if value:
                return str(value)
            return ''

        table_dict = self.tables.get(table)
        kw = {}
        for key, val in kwargs.items():
            if table_dict.get(key) == 'INTEGER':
                val = get_int(val)
            elif table_dict.get(key) == 'TEXT':
                val = get_str(val)
            kw[key] = val
        return kw



class TimeReportDatabaseSqlite3(TimeReportDatabase):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.file_path = file_path

    def _connect(self):
        self.conn = sqlite3.connect(self.file_path)
        self.c = self.conn.cursor()

    def _disconnect(self):
        self.conn.close()
        self.c = None

    def _create_command(self, command):
        """
        Method that creates things in database using CREATES

        :param command: str
        :return: None
        """
        try:
            self._connect()
            self.c.execute(command)
            self.conn.commit()
        except Exception as e:
            raise e
        finally:
            self._disconnect()

    def _insert_command(self, command, value_dict):
        """
        Method to insert records into the database.
        :param command:
        :param value_dict:
        :return:
        """
        try:
            self._connect()
            self.c.execute(command, value_dict)
            self.conn.commit()
        except Exception as e:
            raise e
        finally:
            self._disconnect()

    def _select_command(self, command):
        """
        Method that extracts data from the database.
        :param command:
        :param value_dict:
        :return:
        """
        data = None
        try:
            self._connect()
            self.c.execute(command)
            data = self.c.fetchall()
        except Exception as e:
            raise e
        finally:
            self._disconnect()
        return data

    def _get_select_string(self, tables=None, keys=None):
        """
        Returns a SELECT string.
        :param table_name:
        :param keys:
        :return:
        """
        # Selected keys
        if keys == '*':
            pass
        elif not keys:
            key_string = '*'
        else:
            key_string = ',\n'.join(keys)

        if type(tables) == list:
            tables = ' JOIN '.join(tables)

        select_line = f"""SELECT \n{key_string} \n\nFROM {tables}"""

        return select_line

    # ===========================================================================
    def _get_where_string(self, match, match_table=None):
        # Matching items for specific key.
        # Items is a value or list of values
        match_string = ''
        if match:
            for key, items in match.items():
                if match_table:
                    key = f'{match_table}.{key}'
                if items in ['', None, 'NULL', 'null', 'None']:
                    match_string = f"""{match_string}AND {key} IS NULL\n"""
                else:
                    if not isinstance(items, list):
                        items = [items]
                    if len(items) == 1:
                        item = items[0]
                        if type(item) == str:
                            item_str = f"('{item}')"
                        else:
                            item_str = f"({item})"
                    else:
                        item_str = str(tuple(items)).replace("'", "'")
                    match_string = f"""{match_string}AND {key} IN {item_str}\n"""
            match_string = match_string.lstrip('AND ')
            where_line = f"""\n\nWHERE\n{match_string}"""
        else:
            where_line = """"""

        return where_line

    def create_database(self):
        """
        Sets up the tables in teh database.
        :return:
        """
        for table in self.tables:
            content = ''

            for i, [attribute, datatype] in enumerate(self.tables[table].items()):
                if i == 0:
                    pk = ' PRIMARY KEY'
                    ai = ''
                    if attribute in self.autoincrement:
                        ai = ' AUTOINCREMENT'
                else:
                    pk = ''
                    ai = ''
                content = content + f'{attribute} {datatype}{pk}{ai}, '

            command = f"""CREATE TABLE {table} ({content.strip(', ')})"""
            self._create_command(command)

    def add_record_to_table(self, table, **kwargs):
        """

        :param table:
        :param kwargs:
        :return:
        """
        self.check_attributes(table, **kwargs)
        kw = self.convert_kwargs(table, **kwargs)
        values = ''
        for key in self.get_attributes_for_table(table, all=True):
            if key in self.autoincrement:
                kw[key] = None
            values = values + f':{key}, '
        command = f"""INSERT INTO {table} VALUES ({values.strip(', ')})"""
        self._insert_command(command, kw)

    def _get_data_string(self, table=None, keys=[], match={}, match_table=None, **kwargs):
        if not isinstance(keys, list):
            keys = [keys]

        # SELECT statement
        select_line = self._get_select_string(table, keys)

        # WHERE statement
        where_line = self._get_where_string(match, match_table)

        string = select_line + where_line

        # Write to database
        return string

    def _get_data(self, tables=None, columns=['*'], **kwargs):
        """
        kwargs are match criteria.
        :param table:
        :param columns:
        :param kwargs:
        :return:
        """
        match_table = None
        if type(tables) == list:
            # Add JOIN statement if match_table is given
            match_table = tables[0]
        string = self._get_data_string(table=tables, keys=columns, match=kwargs, match_table=match_table)
        data = self._select_command(string)
        return data

    def get_data(self, tables=None, columns=None, as_dict=True, **kwargs):
        """

        kwargs are match criteria.
        :param tables: str or list
        :param columns: str or list
        :param as_dict: boolean
        :param kwargs:
        :return:
        """
        data = self._get_data(tables=tables, columns=columns, **kwargs)
        if not as_dict:
            return data
        if not columns or columns == '*':
            if type(tables) == list:
                columns = []
                for table in tables:
                    columns.extend(self.get_attributes_for_table(table))
            else:
                columns = self.get_attributes_for_table(tables)
        data_dict = {item: [] for item in columns}
        for line in data:
            for item, value in zip(columns, line):
                data_dict[item].append(value)
        return data_dict

    def get_test_data(self):
        command = """SELECT * 
                     FROM Employee JOIN TimeReport
                     WHERE Employee.employee_nr=1"""
        data = self._select_command(command)
        return data
