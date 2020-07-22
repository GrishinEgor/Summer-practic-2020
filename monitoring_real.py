#!/usr/bin/python3
#coding=UTF-8
'''
	The main module for launching the functions of performing 
	a posteriori daily monitoring based 
	on measurement files in the Rinex 3 format
'''
__author__ 		= "KomissarovAV"
__copyright__	= "Copyright 2019, AO GLONASS"
__license__		= "Secret Developments"
__email__		= "av.komissarov@glonass-iac.ru"
__version__		= "0.5.0"
__data__		= "2020-03-18"

# основные требуемые библиотеки
import time
import sys
import os
import io

from dir_function import create_dir_path
# загрузка путей
dir_path = create_dir_path()

'''
				Подключение библиотек			
'''
sys.path.insert(0,dir_path['path_lib'])			# путь до каталога с функциями
from datetime_function import *					# библиотека времени
from python_dbconfig import connect_to_DB		# подключение к БД
from alarm import *								# библиотеки рабыты по остановке работы программы
from logging_file import *							# формирование лог-данных и лог-файла

'''		Этап 1 - формирование начальных данных		'''
from preparation_file import *					# функции копирование/перемещение файлов
from preparation_alm import *					# функции копирование/перемещение альманахов
from processing_file import *					# функции изменение файлов
from path_function import * 					# функции изменение и работы с директориями
from zona import zona							# функция создания зон через  CALC_ZON.exe
'''		Этап 2 - занесение данных в БД		'''
from entry_data_to_DB import *					# занесение данных мониторинга в БД
from alma import *								# занесение данных альманаха в БД

'''		Этап 3 - обработка данных в БД		'''
from heft_new import *								# создание и другие действия с весами станций
from mon_analysis import * 						# формирование выборки по мониторингу
from nav_analysis import * 						# формирование выборки по навигационным сообщениям
from sample_analysis import *					# формирование объединеной выборки и выборки для отчета
from genchar import genchar						# формирование таблицы genchar
'''		Этап 4 - формирование отчета		'''
from image import *								# создание картинок
#from russer import *                           # формирование текстового файла данных для ТИ и РС

# основные очистки
wine_restart()


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

    # При создании объекта выполняются первые обязательные шаги
    def __init__(self, f_print):
        # Поток стандартного вывода
        self.f_print = f_print
        
        time_start = time.time()
        try:
            self.dir_path = create_dir_path()
            '''
                    ЧАСТЬ 0 ПОДГОТОВКА
            '''
            # вычисление занчений даты
            self.year, self.month, self.day, self.day_year, self.hour, self.now_date = create_datetime_item(self.days_d)
            print(self.year, self.month, self.day, self.day_year, file=self.f_print)
            
            #дополнение путей изменяемыми данными
            self.dir_path = redefinition_dir_path(self.dir_path, self.now_date)

            #### создание файла-лога
            self.name_log_file = '/logs_{0}.txt'.format(self.now_date.strftime('%d.%m.%Y'))
            self.f = create_log_file(self.dir_path, self.now_date, self.name_log_file)
            file_log_header(self.f, self.now_date, self.day_year, self.hour, 1)
            ## подключение к БД
            try:
                self.cnx = connect_to_DB(self.f, 'ConnectDailyMonDB.cfg')
            except:
                raise Exception("Нет бодключения к БД")

            '''
                    Часть 1 ПРОВЕРКА ПУТЕЙ
            '''			
            ## пути глобальные
            print('--- checkglobpath', file=self.f_print)
            self.flag_path = check_glob_path(self.f, dir_path)
            
            ## пути локальные
            print('--- checklocpath', file=self.f_print)
            check_loc_path(self.f, dir_path)
            
        except Exception as err:
            self.f.write('Неожиданная ошибка при проверке и подготовке путей: {0}\n'.format(err))
            self.f.write(u'Выполнение остальных пунктов невозможно\n')
            self.f.flush()
            print('Неожиданная ошибка при проверке и подготовке путей: {0}'.format(err), file=self.f_print)
            print('Выполнение остальных пунктов невозможно\n', file=self.f_print)

            self.flag = False
            
        finally:
            time_end = time.time()
            if time_end - time_start < 1:
                self.f.write(u'Подготовка и проверка путей заняли: {:.3f} сек.\n'.format(time_end - time_start))
                print('Подготовка и проверка путей заняли: {:.3f} сек.'.format(time_end - time_start), file=self.f_print)
            else:
                self.f.write(u'Подготовка и проверка путей заняли: {:.3f} мин.\n'.format((time_end - time_start)/60))
                print('Подготовка и проверка путей заняли: {:.3f} мин.'.format((time_end - time_start)/60), file=self.f_print)
        
            self.f.write(u'====================================================\n')
            self.f.flush()
            print('====================================================', file=self.f_print)

    def __del__(self):
        now_date = datetime.datetime.now()
        self.f.write(u'Окончание работы: {0}\n==========================================================================\n'.format(now_date.strftime('%H:%M:%S')))
        self.f.close()
        

    def make_stat(self, arr_active_part):
        res = [True for i in range(self.num_parts)]
        func = [self.part1, self.part2, self.part3, self.part4, self.part5, self.part6, self.part7]
        
        self.f.write('\nНачало выполнения запроса\n\n')
        self.f.flush()
        print('\nНачало выполнения запроса\n', file=self.f_print)
        
        for i in range(self.num_parts):
            if arr_active_part[i]:
                time_start = time.time()
                try:
                    self.f.write('Выполнение пункта {0}\n\n'.format(self.name_parts[i]))
                    self.f.flush()
                    print('Выполнение пункта {0}\n'.format(self.name_parts[i]), file=self.f_print)
                    func[i]()
                    
                except Exception as err:
                    self.f.write('Неожиданная ошибка при выполнении пункта {0}: {1}\n'.format(self.name_parts[i], err))
                    self.f.flush()
                    print('Неожиданная ошибка при выполнении пункта {0}: {1}'.format(self.name_parts[i], err), file=self.f_print)
                    res[i] = False

                finally:
                    time_end = time.time()
                    if time_end - time_start < 1:
                        self.f.write(u'Выполнение пункта {} заняло: {:.3f} сек.\n'.format(self.name_parts[i], time_end - time_start))
                        print('Выполнение пункта {} заняло: {:.3f} сек.'.format(self.name_parts[i], time_end - time_start), file=self.f_print)
                    else:
                        self.f.write(u'Выполнение пункта {} заняло: {:.3f} мин.\n'.format(self.name_parts[i], (time_end - time_start)/60))
                        print('Выполнение пункта {} заняло: {:.3f} мин.'.format(self.name_parts[i], (time_end - time_start)/60), file=self.f_print)
                    self.f.flush()
                    print('----------------------------------------------------', file=self.f_print)
        
        self.f.write(u'Выполнение запроса завершено\n')
        self.f.write(u'====================================================\n')
        self.f.flush()
        print('Выполнение запроса завершено', file=self.f_print)
        print('====================================================', file=self.f_print)
        
        return res


    def part1(self):
        '''
                ЧАСТЬ 2	СОЗДАНИЕ И ЗАНЕСЕНИЕ ВЫБОРКИ
        '''
        print("--- osremove", file=self.f_print)
        ## удаление файлов в рабочей папке
        osremove(self.dir_path['path_izm_bef_file'], self.f, 0)
        osremove(self.dir_path['path_bds'], self.f, 1)
        f.flush()
                
        print("--- copy_measurement_files", file=self.f_print)
        #### копирование данных на localmachin
        copy_measurement_files(self.cnx, self.f, self.dir_path, self.day_year, self.year)
        f.flush()
        
        print("--- del_rn2", file=self.f_print)
        #### удаления повторяющихся файлов во 2ом rinex
        del_file_rn2(self.dir_path['path_izm_bef_file'], self.f)
        f.flush()
                
        print('--- copy_nav_file', file=self.f_print)
        #### копирование навигационных данных
        ''' flag_efm возвращение 
                        0 - данных нет от внутренней склейки
                        1 - данные есть от внутренней склейки'''
        self.flag_efm = copy_nav_file(self.dir_path, self.day_year, self.year, self.f)
        self.f.flush()
        if (self.flag_path == False and self.flag_efm != 1):
            raise Exception('ОШИБКА: Навигационных данных нет - Завершение работы')

        print('--- unpacking', file=self.f_print)
        #### разархивирование архивов измерений
        unpacking_file(self.f, self.dir_path['path_izm_bef_file'], self.dir_path['path_add_pro'])
        self.f.flush()

        print('--- mov_almanach', file=self.f_print)
        #### копирование альманхов
        copy_almanach_file(self.f, self.day, self.month, self.year, self.dir_path)

        if (int(self.hour) < 10):
            osremove(self.dir_path['path_zona'], self.f, 0)

            print('--- zona', file=self.f_print)
            #### создание зон
            zona(self.cnx, self.dir_path, self.year, self.month, self.day, self.day_year, self.f)
            self.f.flush()

    def part2(self):
        '''
                ЧАСТЬ 3	ФОРМИРОВАНИЕ ДАННЫХ МОНИТОРИНГА
        '''
        print('--- sat_sol_create', file=self.f_print)
        #### распаковка файла в файлы с расширением SAT и SOL программой BDS_BDS.exe
        self.f.write(u'----------sat_sol_create\n')
        sat_sol_create(self.dir_path['path_izm_bef_file'], self.dir_path['path_bds'], self.f)
        
        ####удаление данных с измерениями
        osremove(self.dir_path['path_izm_bef_file'], self.f, 0)
        self.f.flush()          
        
        print('--- copy_sat_sol_file', file=self.f_print)
        #### перемещение файлов sat и sol
        self.f.write(u'----------copy_sat_sol_file\n')            
        copy_sat_sol_file(self.f, self.dir_path['path_bds'], self.dir_path['path_sat_sol'], self.day_year)
        self.f.flush()  

    def part3(self):
        '''
                ЧАСТЬ 4 ЗАНЕСЕНИЕ ДАННЫХ МОНИТОРИНГА В БД
        '''
        if self.flagConnect:
                self.f.write(u'\nВыполнение пункта невозможно, так как нет подключения к БД\n')
                self.f.flush()
                print(u'\nВыполнение пункта невозможно, так как нет подключения к БД\n', file=self.f_print)
                return

        print('--- mass_data_enter_into_DB', file=self.f_print)
        #### занесение данных в БД
        mass_data_enter_into_DB(self.cnx, self.f, self.day, self.month, self.year, self.dir_path['path_sat_sol'], self.dir_path['path_sql_input_data'])
        self.f.flush()
        
        print('--- almanach', file=self.f_print)
        #### занесение данных-альманаха в БД
        almanach(self.cnx, self.f, self.day, self.month, self.year, self.day_year, self.dir_path)
        self.f.flush()

    def part4(self):
        '''
                ЧАСТЬ 5.2 АНАЛИЗ ДАННЫХ МОНИТОРИНГА
        '''
        
        print('--- int_acc_insert', file=self.f_print)
        #### процесс формирование выборки (занесение данных в таблицу int_acc_sat)
        int_acc_sat_insert(self.year, self.month, self.day, self.cnx, self.f)
        self.f.flush()
        
        print('--- mon_int_acc', file=self.f_print)
        #### формирование признаков на эпоху
        mon_int_acc(self.cnx, self.f, self.year, self.month, self.day, self.dir_path['path_sql_input_data'])
                   
        print('--- mon_int_acc_upd', file=self.f_print)
        #### изменение признаков на эпоху
        mon_int_acc_upd(self.cnx, self.f, self.year, self.month, self.day)
        self.f.flush()
        
        print('--- mon_spans', file=self.f_print)
        #### формирование промежутков точности
        create_spans(self.cnx, 'mon_spans', self.f, self.year, self.month, self.day)
        
        if self.flag_efm == 0:
                print('--- mon_spans_met', file=self.f_print)
                ##### промежутков состояния точности на основе нав.файла от (МИТРИКАС)
                mon_spans_met(self.cnx, self.f, self.year, self.month, self.day)
        

    def part5(self):
        '''
                ЧАСТЬ 5.3 ОБЪЕДИНЕНИЕ ДАННЫХ И ФОРМИРОВАНИЕ ИТОГОВОЙ ИНФОРМАЦИИ
        '''
        print('--- mon_nav_int_acc', file=self.f_print)
        #### формирование признаков на эпоху
        mon_nav_int_acc(self.cnx, self.f, self.year, self.month, self.day)
        
        print('--- mon_nav_spans', file=self.f_print)
        #### формирование промежутков точности
        create_spans(self.cnx, 'mon_nav_spans', self.f, self.year, self.month, self.day)
        
        print('--- daily_mon', file=self.f_print)
        ###занесение почасового состояния спутников в БД для Бюллютеня
        daily_mon(self.cnx, self.f, self.year, self.month, self.day)
        self.f.flush()  

        ###print('--- blt_spans') -- не реализовано blt_int_acc
        ##### формирование промежутков точности
        ###сreate_spans(cnx,'blt_spans',f,year,month,day)

    def part6(self):
        '''
                ЧАСТЬ 6	ФОРМИРОВАНИЕ ХАРАКТЕРИСТИК ФУНКЦИОНИРОВАНИЯ СИСТЕМЫ
        '''
        print('--- genchar', file=self.f_print) 
        # занесение Обобщённые характеристики функционирования систем за сутки для бюллютеня
        genchar(self.cnx, self.f, self.year, self.month, self.day)
        
        ###print('russer') 
        ##### формирование текстового файла данных для ТИ и РС
        ####russer(cursor,f,cnx,year,month,day,day_year,path_root,path_pdf+'/doctext')
        ###print('russer_end')

    def part7(self):
        '''
                ЧАСТЬ 7	ФОРМИРОВАНИЕ БЮЛЛЕТЕНЯ
        '''
        print('--- image_main', file=self.f_print)
        #### создание графиков
        image_main( self.year, self.month, self.day, self.cnx, self.f, self.dir_path['path_image'])
        self.f.flush()
        
        print('--- otch_create', file=self.f_print)
        #### вызов программы-порадителя pdf
        print("Начали создание pdf", file=self.f_print)
        timpdfop = time.time()
        self.cnx.commit()
        print(self.dir_path['path_NewOtchPDF'] + '/NewOtchPDF {0}'.format(self.days_d), file=self.f_print)
        self.f.write(u'Идет процесс формирования pdf ...\n')
        cmd = "{0}/NewOtchPDF {1}".format(self.dir_path['path_NewOtchPDF'], self.days_d)
        self.f.write(u'{0}\n'.format(cmd))
        print('ST_____', file=self.f_print)
        os.system(cmd)  
        print('END_____', file=self.f_print)          
        timpdfex = time.time() 
        
        print('pdf_copy_to_loc', file=self.f_print)
        #### перемещение файла-лога pdf-файла
        pdf_copy_to_loc(self.year, self.month, self.day, self.dir_path['path_main'], self.dir_path['path_logs_NewOtchPDF'])
        self.f.write(u'Создание pdf-файла заняло {0} сек.\n'.format(timpdfex - timpdfop))
        self.f.flush()
        
        print('pdf_copy', file=self.f_print)
        ### перемещение файла pdf
        self.f.write('----------pdf_copy\n')
        print(self.dir_path['path_pdf'], file=self.f_print)
        pdf_copy(self.f, self.year, self.month, self.day, self.dir_path['path_pdf_loc'], self.dir_path['path_pdf'], 0)
        self.f.flush()

        self.cnx.commit()
        self.cnx.close()

if __name__ == "__main__":
    pass
    
