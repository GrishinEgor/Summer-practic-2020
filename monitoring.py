import time

class Monitoring():
    num_parts = 6
    name_parts = ["ФОРМИРОВАНИЕ ДАННЫХ МОНИТОРИНГА",
                  "ЗАНЕСЕНИЕ ДАННЫХ МОНИТОРИНГА В БД",
                  "АНАЛИЗ ДАННЫХ МОНИТОРИНГА",
                  "ОБЪЕДИНЕНИЕ ДАННЫХ И ФОРМИРОВАНИЕ ИТОГОВОЙ ИНФОРМАЦИИ",
                  "ФОРМИРОВАНИЕ ХАРАКТЕРИСТИК ФУНКЦИОНИРОВАНИЯ СИСТЕМЫ",
                  "ФОРМИРОВАНИЕ БЮЛЛЕТЕНЯ"]
    # Флаг успешного завершения подготовительных этапов работы
    flag = True
    days_d = 1
    
    def __init__(self, f_print):
        # Поток стандартного вывода
        self.f_print = f_print
        
        time_start = time.time()
        try:
            print("Выполняются подготовка и проверка путей", file=self.f_print)
            #raise Exception("Какая-то ошибка")
            time.sleep(2)
            
        except Exception as err:
            print('Неожиданная ошибка при проверке и подготовке путей: {0}'.format(err), file=self.f_print)
            print('Выполнение остальных пунктов невозможно', file=self.f_print)

            self.flag = False
            
        finally:
            time_end = time.time()
            if time_end - time_start < 1:
                print('\n--------------------------------------------------', file=self.f_print)
                print('Подготовка и проверка путей заняли: {:.3f} сек.'.format(time_end - time_start), file=self.f_print)
            else:
                print('\n--------------------------------------------------', file=self.f_print)
                print('Подготовка и проверка путей заняли: {:.3f} мин.'.format((time_end - time_start)/60), file=self.f_print)


    def __del__(self):
        print("Производится закрытие открытых файлов", file=self.f_print)
        

    def make_stat(self, arr_active_part):
        res = [True for i in range(self.num_parts)]
        func = [self.part1, self.part2, self.part3, self.part4, self.part5, self.part6]

        print('Начало выполнения запроса\n', file=self.f_print)
        
        for i in range(self.num_parts):
            if arr_active_part[i]:
                time_start = time.time()
                try:
                    print('Выполнение пункта {0}\n'.format(self.name_parts[i]), file=self.f_print)
                    func[i]()
                    
                except Exception as err:
                    print('Неожиданная ошибка при выполнении пункта {0}: {1}\n'.format(self.name_parts[i], err), file=self.f_print)
                    self.f.flush()
                    
                    res[i] = False

                finally:
                    time_end = time.time()
                    if time_end - time_start < 1:
                        print('Выполнение пункта {} заняло: {:.3f} сек.\n'.format(self.name_parts[i], time_end - time_start), file=self.f_print)
                    else:
                        print('Выполнение пункта {} заняло: {:.3f} мин.\n'.format(self.name_parts[i], (time_end - time_start)/60), file=self.f_print)
        return res
                        

    def part1(self):
        print("Выполняется формирование данных мониторинга", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part2(self):
        print("Выполняется занесение данных мониторинга в БД", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        time.sleep(2)

    def part3(self):
        print("Выполняется анализ данных мониторинга", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part4(self):
        print("Выполняется объединение данных и формирование итоговой информации", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        time.sleep(2)

    def part5(self):
        print("Выполняется формирование характеристик функционирования системы", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part6(self):
        print("Выполняется формирование бюллетеня", file=self.f_print)
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

if __name__ == "__main__":
    pass
