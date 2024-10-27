import flet as ft

from time_report.gui.project_card import ProjectCard
from time_report import database


class PageProject(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        btn_add = ft.ElevatedButton('Lägg till project', on_click=self._on_add_project)

        # self.grid_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.grid_view = ft.GridView(
            expand=1,
            runs_count=2,
            max_extent=400,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=2,
        )

        self.controls.append(btn_add)
        self.controls.append(self.grid_view)

    def load_projects_from_database(self):
        for proj in database.get_projects():
            pc = ProjectCard(callback_delete=self._on_delete_project, project=proj, main_app=self.main_app)
            self.grid_view.controls.append(pc)
            self.grid_view.update()

    def _on_add_project(self, e=None) -> None:
        self.grid_view.controls.append(ProjectCard(callback_delete=self._on_delete_project, main_app=self.main_app))
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

    def _on_confirm_delete(self, e, proj):
        self.grid_view.controls.remove(proj)
        self.grid_view.update()
        self.page.close(self._dlg_modal)
        self.main_app.update_pages()

    def update_page(self) -> None:
        for pc in self.grid_view.controls:
            pc.update_card()
