import time

class Monitoring():
    num_parts = 7
    name_parts = ["СОЗДАНИЕ И ЗАНЕСЕНИЕ ВЫБОРКИ",
                  "ФОРМИРОВАНИЕ ДАННЫХ МОНИТОРИНГА",
                  "ЗАНЕСЕНИЕ ДАННЫХ МОНИТОРИНГА В БД",
                  "АНАЛИЗ ДАННЫХ МОНИТОРИНГА",
                  "ОБЪЕДИНЕНИЕ ДАННЫХ И ФОРМИРОВАНИЕ ИТОГОВОЙ ИНФОРМАЦИИ",
                  "ФОРМИРОВАНИЕ ХАРАКТЕРИСТИК ФУНКЦИОНИРОВАНИЯ СИСТЕМЫ",
                  "ФОРМИРОВАНИЕ БЮЛЛЕТЕНЯ"]
    # Флаг успешного завершения подготовительных этапов работы
    flag = True
    days_d = 1
    
    def __init__(self):
        time_start = time.time()
        try:
            print("Выполняются подготовка и проверка путей\n")
            #raise Exception("Какая-то ошибка")
            time.sleep(2)
            
        except Exception as err:
            print('Неожиданная ошибка при подготовке и проверке путей: {0}'.format(err))
            print('Выполнение остальных пунктов невозможно')

            self.flag = False
            
        finally:
            time_end = time.time()
            if time_end - time_start < 1:
                print('Подготовка и проверка путей заняли: {:.3f} сек.'.format(time_end - time_start))
            else:
                print('Подготовка и проверка путей заняли: {:.3f} мин.'.format((time_end - time_start)/60))

            print('====================================================')


    def __del__(self):
        print("Производится закрытие открытых файлов")
        

    def make_stat(self, arr_active_part):
        res = [True for i in range(self.num_parts)]
        func = [self.part1, self.part2, self.part3, self.part4, self.part5, self.part6, self.part7]

        print('\nНачало выполнения запроса\n')
        
        for i in range(self.num_parts):
            if arr_active_part[i]:
                time_start = time.time()
                try:
                    print('Выполнение пункта {0}\n'.format(self.name_parts[i]))
                    func[i]()
                    
                except Exception as err:
                    print('Неожиданная ошибка при выполнении пункта {0}: {1}'.format(self.name_parts[i], err))
                    res[i] = False

                finally:
                    time_end = time.time()
                    if time_end - time_start < 1:
                        print('\nВыполнение пункта {} заняло: {:.3f} сек.'.format(self.name_parts[i], time_end - time_start))
                    else:
                        print('\nВыполнение пункта {} заняло: {:.3f} мин.'.format(self.name_parts[i], (time_end - time_start)/60))
                    print('----------------------------------------------------')

        print('Выполнение запроса завершено')
        print('====================================================')

        return res
                        

    def part1(self):
        print("Выполняется создание и занесение выборки")
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part2(self):
        print("Выполняется формирование данных мониторинга")
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part3(self):
        print("Выполняется занесение данных мониторинга в БД")
        # raise Exception("Какая-то ошибка")
        time.sleep(2)

    def part4(self):
        print("Выполняется анализ данных мониторинга")
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part5(self):
        print("Выполняется объединение данных и формирование итоговой информации")
        # raise Exception("Какая-то ошибка")
        time.sleep(2)

    def part6(self):
        print("Выполняется формирование характеристик функционирования системы")
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

    def part7(self):
        print("Выполняется формирование бюллетеня")
        # raise Exception("Какая-то ошибка")
        # time.sleep(2)

if __name__ == "__main__":
    pass
