# Импортируем необходимые модули
import multiprocessing  # Для параллельных вычислений
import sys  # Для работы с аргументами командной строки
import os   # Для получения информации о системе

# Функция для чтения матрицы из файла
def read_matrix(filename):
    """
    Читает матрицу из файла.

    Параметры:
        filename (str): Имя файла, из которого читается матрица.

    Возвращает:
        list: Двумерный список (матрица), содержащий числа из файла.
    """
    # Открываем файл на чтение
    with open(filename, 'r') as f:
        matrix = []  # Инициализируем пустой список для хранения строк матрицы
        for line in f:
            # Убираем лишние пробелы и символы перевода строки
            line = line.strip()
            # Проверяем, не является ли строка пустой
            if not line:
                continue  # Пропускаем пустые строки
            # Разделяем строку на отдельные элементы по пробелам
            str_numbers = line.split()
            # Преобразуем каждую строку в число (float)
            row = [float(num) for num in str_numbers]
            # Добавляем полученный список чисел в матрицу
            matrix.append(row)
    # Возвращаем матрицу
    return matrix

# Функция для вычисления одного элемента произведения матриц и записи его в файл
def compute_and_write_element(args):
    """
    Вычисляет значение одного элемента результирующей матрицы и записывает его в файл.

    Параметры:
        args (tuple): Кортеж, содержащий индекс элемента, матрицы A и B, путь к файлу и Lock.

    Возвращает:
        None
    """
    # Распаковываем аргументы
    index, A, B, filename, lock = args
    i, j = index  # Индексы строки и столбца для вычисляемого элемента
    res = 0  # Инициализируем переменную для накопления суммы
    # Количество элементов для суммирования (число столбцов в A или строк в B)
    N = len(A[0])
    # Цикл по общему размеру для суммирования произведений
    for k in range(N):
        # Умножаем элемент из строки матрицы A на элемент из столбца матрицы B и добавляем к сумме
        res += A[i][k] * B[k][j]
    # Формируем строку для записи в файл
    line = f"{i} {j} {res}\n"
    # Пишем результат в файл, обеспечивая синхронизацию с помощью Lock
    with lock:
        # Открываем файл в режиме добавления
        with open(filename, 'a') as f:
            f.write(line)

# Главная функция программы
def main():
    """
    Основная функция программы.

    Выполняет чтение матриц, их проверку, умножение и запись результата.
    """
    # Проверяем наличие необходимых аргументов командной строки
    if len(sys.argv) != 3:
        print("Использование: python программа.py matrix1.txt matrix2.txt")
        sys.exit(1)  # Завершаем программу с кодом ошибки

    # Читаем имена файлов матриц из аргументов командной строки
    matrix1_file = sys.argv[1]
    matrix2_file = sys.argv[2]

    # Читаем матрицы из указанных файлов
    A = read_matrix(matrix1_file)
    B = read_matrix(matrix2_file)

    # Проверяем возможность перемножения матриц
    # Число столбцов матрицы A должно совпадать с числом строк матрицы B
    if len(A[0]) != len(B):
        print("Матрицы не могут быть перемножены: число столбцов A не равно числу строк B")
        sys.exit(1)

    # Определяем размер результирующей матрицы
    result_rows = len(A)      # Число строк результирующей матрицы
    result_cols = len(B[0])   # Число столбцов результирующей матрицы

    # Создаем список индексов элементов результирующей матрицы
    indices = []  # Инициализируем пустой список индексов
    for i in range(result_rows):
        for j in range(result_cols):
            indices.append((i, j))  # Добавляем кортеж индексов (i, j)

    # Определяем количество процессов автоматически
    # Используем количество процессоров в системе
    num_cores = multiprocessing.cpu_count()

    # Можно ограничить максимальное количество процессов, если это необходимо
    max_processes = 8  # Например, не более 8 процессов
    num_processes = min(num_cores, max_processes)

    print(f"Количество ядер в системе: {num_cores}")
    print(f"Будет использовано процессов: {num_processes}")

    # Создаем менеджер для управления общими ресурсами
    manager = multiprocessing.Manager()
    lock = manager.Lock()  # Создаем Lock для синхронизации записи в файл

    # Имя промежуточного файла для записи элементов сразу после вычисления
    intermediate_file = 'intermediate_results.txt'

    # Перед началом вычислений очищаем (если существует) или создаем новый промежуточный файл
    open(intermediate_file, 'w').close()

    # Подготавливаем аргументы для функции compute_and_write_element
    args = []  # Инициализируем список аргументов
    for index in indices:
        args.append((index, A, B, intermediate_file, lock))  # Добавляем необходимые аргументы

    # Создаем пул процессов для параллельного выполнения
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Параллельно вычисляем элементы и записываем их в файл
        pool.map(compute_and_write_element, args)

    # После вычислений необходимо собрать результаты из промежуточного файла и сформировать итоговую матрицу
    # Инициализируем пустую матрицу нужного размера
    result_matrix = []
    for i in range(result_rows):
        result_matrix.append([0] * result_cols)

    # Читаем данные из промежуточного файла
    with open(intermediate_file, 'r') as f:
        for line in f:
            # Убираем лишние пробелы и символы перевода строки
            line = line.strip()
            if not line:
                continue  # Пропускаем пустые строки
            # Разбиваем строку на индексы и значение
            i_str, j_str, value_str = line.split()
            i = int(i_str)
            j = int(j_str)
            value = float(value_str)
            # Записываем значение в соответствующую позицию результирующей матрицы
            result_matrix[i][j] = value

    # Записываем результирующую матрицу в файл
    with open('result_matrix.txt', 'w') as f:
        for row in result_matrix:
            # Преобразуем числа в строки
            str_numbers = [str(num) for num in row]
            # Объединяем числа через пробел и добавляем перевод строки
            line = ' '.join(str_numbers) + '\n'
            # Записываем строку в файл
            f.write(line)

# Проверяем, является ли данный скрипт основным (а не импортированным модулем)
if __name__ == '__main__':
    # Запускаем основную функцию
    main()