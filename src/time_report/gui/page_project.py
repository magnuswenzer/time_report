import datetime

import flet as ft

from time_report.gui.project_card import ProjectCard
from time_report import database, utils, controller
from time_report.gui.sum_times import SumTimes
from time_report.settings import settings
from time_report.gui.date_selection import DateSelection

COLUMN_WIDTH = 200
COLUMN_WIDTH_INFO = 250


class PageProject(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        btn_add = ft.ElevatedButton('Lägg till project', on_click=self._on_add_project)

        # self.grid_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)
        #mself.grid_view = ft.Column(expand=1, spacing=10, auto_scroll=True, scroll=True)
        self.expand = True
        self.grid_view = ft.GridView(
            expand=1,
            runs_count=2,
            max_extent=500,
            child_aspect_ratio=0.9,
            spacing=5,
            run_spacing=2,
        )

        row_projects = ft.Column(expand=True)
        row_projects.controls.append(btn_add)
        row_projects.controls.append(ft.Column([self.grid_view], expand=True, scroll=True))

        col_sum = self._get_summarize_column()

        self._tabs = ft.Tabs(
            expand=True,
            selected_index=1,
            animation_duration=300,
            # on_change=self._on_change_tab,
            tabs=[
                ft.Tab(
                    text="Projekt",
                    icon=ft.icons.NOTE,
                    content=row_projects,
                ),
                ft.Tab(
                    text="Sammanfattning",
                    icon=ft.icons.SUMMARIZE,
                    content=col_sum,
                ),
            ]
        )

        self.controls.append(self._tabs)
        # self.controls.append(btn_add)
        # self.controls.append(ft.Column([self.grid_view], expand=True, scroll=True))

    def load_projects_from_database(self):
        self.grid_view.controls = []
        for proj in sorted(database.get_projects(year=settings.year), key=lambda x: x.name):
            pc = ProjectCard(callback_delete=self._on_delete_project, project=proj, main_app=self.main_app)
            self.grid_view.controls.append(pc)
        self.grid_view.update()

    def _on_add_project(self, e=None) -> None:
        self.grid_view.controls.insert(0, ProjectCard(callback_delete=self._on_delete_project, main_app=self.main_app))
        self.grid_view.update()

    def _on_delete_project(self, proj: "ProjectControl"):
        self._dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Bekräfta borttagning"),
            content=ft.Text(f"Vill du verkligen ta bort projekt {proj.name}?"),
            actions=[
                ft.TextButton("Ja", on_click=lambda e, p=proj: self._on_confirm_delete(e, p)),
                ft.TextButton("Nej", on_click=lambda _: self.page.close(self._dlg_modal)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda _: self.page.close(self._dlg_modal),
            )
        self.page.open(self._dlg_modal)

    def _get_summarize_column(self) -> ft.Column:
        self._summarize_posts = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

        #option_row = ft.Row([
        #    ft.ElevatedButton('Ladda om', on_click=self.update_page),
        #])

        self._date_selection = DateSelection(callback_change_date=self._on_select_date)

        header_row = ft.Row([
            ft.Text('Projekt', width=COLUMN_WIDTH),
            ft.Text('Planerad tid', width=COLUMN_WIDTH),
            ft.Text('Arbetad tid', width=COLUMN_WIDTH),
            ft.Text('Rapporterad tid', width=COLUMN_WIDTH),
            ft.Text('Arbetad minus rapporterad', width=COLUMN_WIDTH),
        ])

        self._sum_row = ft.Row()
        #
        # self._tot_worked_time = ft.Text()
        # self._tot_scheduled_time = ft.Text()
        # self._tot_submitted_time = ft.Text()
        # self._tot_worked_minus_scheduled_time = ft.Text()
        # self._tot_worked_minus_submitted_time = ft.Text()
        # self._tot_scheduled_minus_submitted_time = ft.Text()
        #
        # self._tot_times_column = ft.Column([
        #     ft.Row([ft.Text("Total arbetad tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_time]),
        #     ft.Row([ft.Text("Total schemalagd tid:", width=COLUMN_WIDTH_INFO), self._tot_scheduled_time]),
        #     ft.Row([ft.Text("Total rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_submitted_time]),
        #     ft.Row([ft.Text("Arbetad minus schemalagd tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_minus_scheduled_time]),
        #     ft.Row([ft.Text("Arbetad minus rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_minus_submitted_time]),
        #     ft.Row([ft.Text("Schemalagd minus rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_scheduled_minus_submitted_time]),
        # ])

        self._sum_times = SumTimes(self.main_app)

        col = ft.Column([
            self._date_selection,
            ft.Divider(),
            ft.Row([
                ft.Column([
                    header_row,
                    ft.Divider(),
                    self._summarize_posts,
                    ft.Divider(),
                    self._sum_row,

                ], expand=True),
                ft.VerticalDivider(),
                self._sum_times,
                # self._tot_times_column

            ], expand=True),

        ])
        return col
        #return ft.Row([
        #    col_sum,
        #    info_row
        #])

    def _on_select_date(self):
        date = self._date_selection.date
        if not date:
            return
        self._update_sum(date)

    def _on_confirm_delete(self, e, proj):
        self.grid_view.controls.remove(proj)
        self.grid_view.update()
        self.page.close(self._dlg_modal)
        self.main_app.update_pages()

    def update_page(self) -> None:
        self.load_projects_from_database()
        for pc in self.grid_view.controls:
            pc.update_card()
        date = self._date_selection.date
        print(f"{date=}")
        self._update_sum(date)
        # self._sum_times.update_times(date)

    def _update_sum(self, end_date: datetime.date = None) -> None:
        self._summarize_posts.controls = []
        self._sum_row.controls = []

        sum_planned = utils.TimeDelta()
        sum_worked = utils.TimeDelta()
        sum_submitted = utils.TimeDelta()

        for proj in sorted(controller.get_projects(), key=lambda x: x.name):
            time_planned = utils.TimeDelta()
            h_planned = proj.hours_in_plan
            if h_planned:
                time_planned = utils.TimeDelta(datetime.timedelta(hours=h_planned))
            time_worked = controller.get_total_time_for_project(proj,
                                                                date_stop=end_date)
            time_submitted = controller.get_sum_of_submitted_time(proj=proj,
                                                                  date_stop=end_date)

            worked_minus_submitted = time_worked - time_submitted

            sum_planned += time_planned
            sum_worked += time_worked
            sum_submitted += time_submitted

            row = ft.Row()
            row.controls.append(ft.Text(str(proj.name), width=COLUMN_WIDTH))
            row.controls.append(ft.Text(utils.get_h_str(time_planned), width=COLUMN_WIDTH))
            row.controls.append(ft.Text(utils.get_hm_str(time_worked), width=COLUMN_WIDTH))
            row.controls.append(ft.Text(utils.get_h_str(time_submitted), width=COLUMN_WIDTH))
            row.controls.append(ft.Text(utils.get_hm_str(worked_minus_submitted).rsplit(":", 1)[0], width=COLUMN_WIDTH))
            self._summarize_posts.controls.append(row)
        self._summarize_posts.update()

        self._sum_row.controls.append(ft.Text("TOTALT", width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(utils.get_h_str(sum_planned), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(utils.get_hm_str(sum_worked), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(utils.get_h_str(sum_submitted), width=COLUMN_WIDTH))

        # sum_scheduled = controller.get_sum_of_scheduled_time(date_stop=end_date)
        #
        # self._tot_worked_time.value = utils.get_h_str(sum_worked)
        # self._tot_scheduled_time.value = utils.get_hm_str(sum_scheduled)
        # self._tot_submitted_time.value = utils.get_hm_str(sum_submitted)
        # self._tot_worked_minus_scheduled_time.value = utils.get_hm_str(sum_worked - sum_scheduled)
        # self._tot_worked_minus_submitted_time.value = utils.get_hm_str(sum_worked - sum_submitted)
        # self._tot_scheduled_minus_submitted_time.value = utils.get_hm_str(sum_scheduled - sum_submitted)
        # self._tot_times_column.update()

        self._sum_row.update()
        self._sum_times.update_times(end_date)

        # self._sum_row.controls.append(ft.Text(str(''), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(ft.Text(str(tot_worked), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(ft.Text(str(tot_submitted), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(ft.Text(str(tot_scheduled), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(
        #     ft.Text(str(tot_worked_minus_scheduled), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(
        #     ft.Text(str(tot_worked_minus_submitted), width=COLUMN_WIDTH))
        # self._sum_row.controls.append(
        #     ft.Text(str(tot_submitted_minus_scheduled), width=COLUMN_WIDTH))
        # self._sum_row.update()
