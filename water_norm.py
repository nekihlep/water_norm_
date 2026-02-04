def calculate_water_norm(weight_kg, activity_minutes):

    if not isinstance(weight_kg, int):
        raise ValueError("Вес должен быть числом")

    if weight_kg < 5 or weight_kg > 250:
        raise ValueError("Вес должен быть от 5 до 250 кг")

    # Проверка типа активности
    if not isinstance(activity_minutes, int):
        raise ValueError("Время активности должно быть числом")

    if activity_minutes < 0:
        raise ValueError("Время активности не может быть отрицательным")

    if activity_minutes > 720:
        raise ValueError("Время активности не может превышать 720 минут")

    # Расчет нормы
    base_norm = 30 * weight_kg
    activity_extra = (500 * activity_minutes) / 60
    total_norm = base_norm + activity_extra

    return round(total_norm, 2)


def get_user_input():

    print("Калькулятор нормы воды")

    try:
        weight = float(input("Введите вес (кг): "))
        activity = int(input("Введите активность (минуты): "))
        return weight, activity
    except ValueError:
        raise ValueError("Некорректный ввод данных")


def main():
    try:
        weight, activity = get_user_input()
        norm = calculate_water_norm(weight, activity)

        print(f"\n Ваша дневная норма воды: {norm} мл")
        print(f"   Это примерно {norm / 1000:.1f} литров")

    except ValueError as e:
        print(f" Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nПрограмма прервана")

if __name__ == "__main__":
    main()