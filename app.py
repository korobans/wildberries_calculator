from flask import Flask, render_template, request
import logging

app = Flask(__name__)


# Настройка логирования
logging.basicConfig(filename='calculator.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# проверка на наличие цифр в строке
def digit_check(expression: str):
    for char in expression:
        if char.isdigit():
            return True
    return False


# проверка на наличие точки в предыдущем числе
def float_correct_check(expression: str):
    expression = expression[::-1]
    for char in expression:
        if not char.isdigit():
            if char == '.':
                return False
            return True
    return True


@app.route('/', methods=['GET', 'POST'])
def index():
    # Инициализация строки отображения как пустую
    display = ''
    if request.method == 'POST':
        current_expression = request.form['expression']  # Получение текущее выражение из формы
        new_value = request.form['value']  # Получение нового значения из формы

        # Логируем действие пользователя
        logging.info(f'User input: {current_expression}, Button pressed: {new_value}')

        # Очистка дисплея, если пользователь нажал 'C'
        if new_value == 'C':
            display = ''

        # Удаление последнего символа текущего выражения, если нажата 'DEL'
        elif new_value == 'DEL':
            if current_expression != 'Error':
                display = current_expression[:-1]
            # Если в выражении записана ошибка, то очистка всей строки
            else:
                display = ''

        # Вычисление выражения, если нажата '='
        elif new_value == '=':
            if digit_check(current_expression):
                # Попытка вычислить выражение и округлить результат до 15 знаков после запятой
                try:
                    display = str(round(eval(current_expression), 15))
                    logging.info(f'Calculation result: {display}')
                # Обрабатка ошибки деления на ноль
                except ZeroDivisionError:
                    display = 'Error'
                    logging.error('Calculation error: Division by zero')
                # Обрабатка любой другой ошибки
                except Exception as error:
                    display = current_expression
                    logging.error(f'Calculation error: {error}')
        # Проверка различных услови1 для корректного добавления нового значения к выражению
        else:
            # Если выражение пустое и новое значение - оператор, ничего не добавляем
            if (not current_expression) and (new_value in '+*/)'):
                display = ''
            # Если выражение пустое и новое значение - точка, добавляем "0."
            elif (not current_expression) and (new_value == '.'):
                display = '0.'
            # Если выражение содержит ошибку, ничего не изменяем
            elif current_expression == 'Error':
                display = current_expression
            # Не допускаем подряд два оператора в начале выражения
            elif len(current_expression) == 1 and (current_expression[-1] == '-' and new_value in '+*/-'):
                display = current_expression
            # Добавляем "0" перед точкой, если точка идет после минуса
            elif current_expression and (new_value == '.' and (current_expression[-1] == '-')):
                display = current_expression + '0' + new_value
            # Заменяем последний оператор новым, если два оператора идут подряд
            elif current_expression and (new_value in '+*/-' and current_expression[-1] in '+*/-'):
                display = current_expression[:-1] + new_value
            # Не допускаем оператор после открывающей скобки
            elif current_expression and (new_value in '+*/(' and current_expression[-1] == '('):
                display = current_expression
            # Не допускаем оператор после минуса, если минус идет после оператора
            elif current_expression and ((not new_value.isdigit() and not new_value == '(') and (current_expression[-1] == '-')):
                display = current_expression
            # Добавляем умножение перед открывающей скобкой, если перед ней число или закрывающая скобка
            elif current_expression and (new_value == '(' and (current_expression[-1].isdigit() or current_expression[-1] == ')')):
                display = current_expression + '*' + new_value
            # Добавляем умножение перед числом, если перед ним закрывающая скобка
            elif current_expression and (new_value.isdigit() and (current_expression[-1] == ')')):
                display = current_expression + '*' + new_value
            # Не допускаем закрывающую скобку, если количество закрывающих скобок не меньше количества открывающих
            elif current_expression and (new_value == ')' and (current_expression.count('(') <= current_expression.count(')'))):
                display = current_expression
            # Не допускаем несколько точек в одном числе
            elif current_expression and (new_value == '.' and not float_correct_check(current_expression)):
                display = current_expression
            # Добавляем новое значение к выражению
            else:
                display = current_expression + new_value
    # Отображение результата на веб-странице
    return render_template('index.html', display=display)


# Запускаем приложение в режиме отладки
if __name__ == '__main__':
    app.run(debug=True)
