import tkinter as tk
import threading

from monitoring import Monitoring

# Виджет, включающий в себя многострочное текстовое поле заблокированное для редактирования
# с вертикальным скролбаром и поддерживающий вывод класса StringIO, т.е. позволяющий
# использовать конструкцию print(str, file=report_obj)
class Report(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='right', fill='y')
        self._text = tk.Text(self, state=tk.DISABLED, *args, **kwargs)
        self._text.pack(side='left', fill='both', expand=1)

        scrollbar['command'] = self._text.yview
        self._text['yscrollcommand'] = scrollbar.set

    def write(self, text):
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)
        self._text.yview_moveto('1.0')  # Прокрутка до конца вниз после вывода

    def clear(self):
        self._text.configure(state=tk.NORMAL)
        self._text.delete(0.0, tk.END)
        self._text.configure(state=tk.DISABLED)
    

# Класс окна gui
class Application(tk.Tk):
    def __init__(self, width, height):
        tk.Tk.__init__(self)
        tk.Tk.title(self, "Мониторинг")

        self.report = Report(self, width=80)

        # Объект мониторинга определяет количество независимых пунктов и их имена
        self.monitoring = Monitoring(self.report)
        self.num_parts = self.monitoring.num_parts
        self.name_parts = self.monitoring.name_parts

        # Разметка
        self.frame = tk.Frame(self)
        self.label = tk.Label(self.frame, font=("Calibri", 14),
                              text='Пункты, которые нужно выполнить:')
        self.label.pack(pady=5, anchor='w')
        self.arr_checkbutton = [0 for i in range(self.num_parts)]
        self.arr_active_part = [tk.BooleanVar() for i in range(self.num_parts)]
        for i in range(self.num_parts):
            self.arr_active_part[i].set(1)
            self.arr_checkbutton[i] = tk.Checkbutton(self.frame,
                                                     font=("Calibri", 10),
                                                     text=self.name_parts[i],
                                                     variable=self.arr_active_part[i],
                                                     onvalue=1, offvalue=0)
            self.arr_checkbutton[i].pack(anchor='w')
            if not self.monitoring.flag: # Если обязательные пункты мониторинга не были выполнены, то все чекбоксы заблокированы
                self.arr_checkbutton[i].deselect()
                self.arr_checkbutton[i]["state"] = 'disabled'
                
        self.button_start = tk.Button(self.frame, font=("Calibri", 14), text="Старт", width=30, height=1, command=self.start)
        self.button_start.pack(pady=10)
        
        self.button_clear = tk.Button(self.frame, font=("Calibri", 14), text="Очистить вывод", width=30, height=1, command=self.report.clear)
        self.button_clear.pack(pady=10)
        
        self.button_reset = tk.Button(self.frame, font=("Calibri", 14), text="Сбросить данные мониторинга", width=30, height=1, command=self.reset)
        self.button_reset.pack(pady=10)
        
        self.frame.pack(side='left', padx=10, pady=10, expand=1)
        self.report.pack(side='left', pady=10, fill='y')

    # Декоратор, запускающий функцию в отдельном потоке
    def thread(func):
        def wrapper(*args, **kwargs):
            current_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            current_thread.start()

        return wrapper

    @thread  # Применение декоратора
    def start(self):
        if self.monitoring.flag:
            # Делаем кнопки неактивными на время мониторинга
            self.set_buttons_state('disabled')
            
            # Выполняются выбранные пункты мониторинга и сообщается информация о том,
            # при выполнении каких из них произошла ошибка. Их чекбоксы становятся заблокированными
            res = self.monitoring.make_stat([i.get() for i in self.arr_active_part])
            for i in range(self.num_parts):
                if not res[i]:
                    self.arr_checkbutton[i].deselect()
                    self.arr_checkbutton[i]["state"] = 'disabled'

            # Делаем кнопки обратно рабочими после завершения мониторинга
            self.set_buttons_state('normal')


    # Заново выполняет первые обязательные пункты мониторинга
    @thread  # Применение декоратора
    def reset(self):
        self.set_buttons_state('disabled')
        
        del self.monitoring
        self.monitoring = Monitoring(self.report)
        for i in range(self.num_parts):
            if self.monitoring.flag:
                self.arr_checkbutton[i].select()
                self.arr_checkbutton[i]["state"] = 'normal'
            else:
                self.arr_checkbutton[i].deselect()
                self.arr_checkbutton[i]["state"] = 'disabled'

        self.set_buttons_state('normal')

        
    def set_buttons_state(self, state):
        self.button_start["state"] = state
        self.button_clear["state"] = state
        self.button_reset["state"] = state


if __name__ == '__main__':
    app = Application(1000, 600)
    app.mainloop()
