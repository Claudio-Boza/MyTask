from db import get_task_all, get_task, delete_task, delete_task_all,finaliza_task, add_task,Task, get_task_not_finalize
import flet as ft
from datetime import datetime
from time import sleep
from winotify import Notification
from threading import Thread

class CustomCheck(ft.Checkbox):
    
    def __init__(self, taks: Task, card: ft.Card, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = taks
        self.card = card
        self.on_change = self.click
        self.value = taks.finalizada
    
    def click(self, e):
        finaliza_task(self.task) 
        self.update()
        self.card.finaliza()
      
class AddTaks(ft.AlertDialog):    
    def __init__(self, page: ft.Page, widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expand = True
        self.scrollable = True
        self.page = page
        self.widget = widget
        self.title = ft.Text('.:: Adicionar Taks ::.', expand=True)
        self.descricao = ft.TextField(multiline=True)
        self.actions = [
           ft.TextButton('Salvar', on_click=self.save),
           ft.TextButton('Cancelar', on_click=self.close_self),
            
        ]
        self.load()
    
    def load(self):
        self.content = ft.Container(
            content= ft.Column(
                controls=[
                    ft.Text('Descrição:'),
                    self.descricao
                ]                
            )
        )
    
    
    def save(self, e):
        if self.descricao.value != '':
            task = Task(
                descricao=self.descricao.value,
                data = datetime.now()
            )
            add_task(task)
        
        self.page.update()
        self.widget.load_itens()
        self.close_self(False)
                    
    
    def close_self(self, e):        
        self.page.close(self)
        self.page.update()
    
    

class ListTaks(ft.Column):
    def __init__(self, *args, page: ft.Page, **kwargs):
        super().__init__(*args, **kwargs)        
        self.controls = []
        self.load()
        self.page = page
        
    def load(self):
        lista = get_task_all()
        if lista:
            for i in lista:
                self.controls.append(CardCustom(i, self, self.page))
        else:
            self.controls.append(
                ft.Container(                   
                    alignment=ft.alignment.center,
                    content=ft.Text('Nenhuma tarefa cadastrada.')                
                    )
                )

        
    def delete_list_task(self, task_id):
        for i in self.controls:
            if i.task.id == task_id:
                self.controls.remove(i)
        self.update()
    
    def load_itens(self):
        self.controls.clear()
        self.controls = [CardCustom(item, self, self.page) for item in get_task_all()]
        self.update()

class AppBarCustom(ft.AppBar):
    def __init__(self, page: ft.Page, widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.title = ft.Text('My Task')
        self.widget = widget
        self.center_title = True
        self.button = ft.IconButton(icon=ft.icons.ADD, padding=ft.padding.all(16), on_click= self.openDialog)
        self.load()

    def load(self):
        self.actions = [
            self.button
        ]
    
    def openDialog(self, e):
        self.page.open(AddTaks(self.page, self.widget))
        self.page.update()

class CardCustom(ft.Card):
    def __init__(self, task : Task, lista: ListTaks, page, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.task = task
        self.elevation = 7
        self.lista = lista
        self.page = page
        self.variant = ft.CardVariant.OUTLINED
    
        if task.finalizada:
            self.shadow_color = ft.colors.GREEN_ACCENT
        self.load()

    
    def load(self):
        self.content = ft.Container(
            padding=ft.padding.all(16),
            content= ft.Column(
                controls=[
                    ft.Text(f'Taks: {self.task.id}', ),
                    ft.Row(
                        controls=[
                            ft.Text('Data Criação:'),
                            ft.Text(f"{self.task.data.strftime('%d/%m/%Y')}", weight=ft.FontWeight.BOLD)
                        ]
                    ),
                    ft.Divider(),                                                            
                    ft.Container(
                        padding=ft.padding.all(16),                        
                        border_radius=16,
                        bgcolor='#2e3237',
                        content=ft.Text(self.task.descricao, weight=ft.FontWeight.BOLD)
                    ),                                      
                    ft.Container(                                                
                        content=ft.Row( 
                            alignment=ft.MainAxisAlignment.END,                           
                            controls=[                            
                                ft.Row(
                                    controls=[
                                        ft.Text('Finalizada: '),
                                        CustomCheck(taks= self.task, card= self),
                                    ]
                                ),                    
                                ft.IconButton(icon=ft.icons.DELETE, on_click=self.click_delete, icon_color=ft.colors.RED)
                            ]
                        ),
                    )
                ]
            )
        )
    
    def click_delete(self, e):
        delete_task(self.task.id)
        self.lista.delete_list_task(self.task.id)

    def openDialog(self, e):
        self.page.open(AddTaks(self.page, self))
        self.page.update()
    
    def finaliza(self):
        if self.task.finalizada:
            self.shadow_color = ft.colors.GREEN_ACCENT
        else:
            self.shadow_color = None
            
        self.update()
   
class TaskNotifier(Thread):
    
    def __init__(self, running, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = running
    
    def run(self):
        try:
            while self.running:
                tasks = get_task_not_finalize()
                if tasks:
                    for i in tasks:
                        notify = Notification(
                            app_id= f'Taks: {i.json.get('id')}',
                            msg= i.json.get('descricao'),                        
                            title='Task pendente'
                        )
                        notify.show()
                    sleep(300)
                else:
                    ...
        except Exception as e:
            ...

def main(page: ft.Page):
    notify = TaskNotifier(running=True)
    notify.start()
    
    def handle_window_event(e):
        if e.data == "close":
            del notify
            notify.running = False
      
    def client_exited(e):        
        #page.pubsub.unsubscribe_all()
        #print('passou por aqui 2')
        ...
        
    # page.on_close = client_exited
    # page.window.prevent_close = True
    page.window.on_event = handle_window_event
    page.window.on_event = client_exited
    # page.window.on_event('window_close',handle_window_event)
    
    page.window_bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.with_opacity(.8, ft.colors.BLACK54)

    page.title = 'My Task '
    page.scroll = True
    lista_widgets = ListTaks(page=page)
    appbar_new  = AppBarCustom(page, lista_widgets)
    page.add(lista_widgets)
    page.appbar = appbar_new
    page.update()

             

if __name__ == '__main__':
    ft.app(main)
    # TaskNotifier().start()
