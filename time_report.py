import os
import json

import database
from exceptions import *
import datetime

class TimeReportHandler(object):
    """
    Main class to handle information about projects and Employees ("using" projects)
    """
    def __init__(self):
        self.db = get_db_connection()
        self.active_employee = None
        self._get_lists()

    def _get_lists(self):
        # Employee
        employee_data = self.db.get_data('Employee', '*')
        self.employee_nr_list = employee_data['employee_nr']
        self.employee_name_list = []
        self.employee_name_to_nr = {}
        for fi, la, nr in zip(employee_data['first_name'], employee_data['last_name'], self.employee_nr_list):
            name = f'{fi} {la}'
            self.employee_name_list.append(name)
            self.employee_name_to_nr[name] = nr

        # Projects
        project_data = self.db.get_data('Project', '*')
        self.project_nr_list = project_data['project_nr']
        self.project_name_list = project_data['project_name']
        self.project_name_to_mr = dict(zip(self.project_name_list, self.project_nr_list))

    def create_database(self):
        self.db.create_database()

    def add_employees_from_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'input', 'employees.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError('No employees.txt file in input')
        data = load_data_from_file(file_path)
        for item in data:
            self.add_employee(**item)

    def add_projects_from_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'input', 'projects.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError('No projects.txt file in input')
        data = load_data_from_file(file_path)
        for item in data:
            self.add_project(**item)

    def add_employee(self, **kwargs):
        """
        Adds an employee to the database
        :param kwargs:
        :return:
        """
        self.db.add_record_to_table('Employee', **kwargs)

    def add_project(self, **kwargs):
        """
        Adds an employee to the database
        :param kwargs:
        :return:
        """
        self.db.add_record_to_table('Project', **kwargs)

    def get_report_time_attributes(self):
        return self.db.get_attributes_for_table('TimeReport')

    def get_project_attributes(self):
        return self.db.get_attributes_for_table('Project')

    def get_employee_attributes(self):
        return self.db.get_attributes_for_table('Employee')

    def get_staffing_attributes(self):
        return self.db.get_attributes_for_table('Staffing')

    def get_employee(self, employee_nr):
        if employee_nr not in self.employee_nr_list:
            raise EmployeeDoesNotExist(employee_nr)
        return Employee(employee_nr)

    def _check_valid_employee(self, employee):
        self.db.get_data()


class Employee(object):

    def __init__(self, employee_nr):
        self.employee_nr = employee_nr
        self.db = get_db_connection()

    def __str__(self):
        return f'Employee: {self.employee_nr}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.employee_nr}'

    def get_report_time_attributes(self):
        return self.db.get_attributes_for_table('TimeReport')

    def report_time(self, **kwargs):
        kwargs['employee_nr'] = self.employee_nr
        date = kwargs.get('date')
        if date:
            if len(date) != 8:
                raise InvalidTimeFormat(f'{date}, should be in format %Y%m%d')
        else:
            date = datetime.datetime.now().strftime('%Y%m%d')
            kwargs['date'] = date
        self.db.add_record_to_table('TimeReport', **kwargs)

    def get_hours_reported(self, project=None):
        if project:
            data = self.db.get_data(tables='TimeReport', columns=['hours_reported'],
                                    employee_nr=self.employee_nr, project_nr=project)
        else:
            data = self.db.get_data(tables='TimeReport', columns=['hours_reported'],
                                    employee_nr=self.employee_nr)
        return sum(data['hours_reported'])


def load_data_from_file(file_path):
    data = []
    with open(file_path) as fid:
        for row, line in enumerate(fid):
            line = line.strip('\n\r')
            if not line:
                continue
            split_line = [item.strip() for item in line.split('\t')]
            if not split_line[0]:
                # Primary key not present
                continue
            if row == 0:
                header = split_line
            else:
                data.append(dict(zip(header, split_line)))
    return data


def get_db_connection():
    db_file_path = os.path.join(os.path.dirname(__file__), 'time_report.db')
    db = database.TimeReportDatabaseSqlite3(db_file_path)
    return db


if __name__ == "__main__":
    handler = TimeReportHandler()
    if 1:
        db_file_path = os.path.join(os.path.dirname(__file__), 'time_report.db')
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
    handler.create_database()
    handler.add_employees_from_file()
    handler.add_projects_from_file()

    emp = handler.get_employee(1)

    emp.report_time(project_nr=192007,
                        employee_nr=1,
                        hours_reported=3)

    # data = handler.get_data(tables=['Employee', 'TimeReport', 'Staffing'], columns='*', employee_nr=1)
    # data = handler.db.get_test_data()
    # print(data)




