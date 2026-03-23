workspace {
    name "Фитнес-трекер"
    description "Вариант 14 — система учёта тренировок и упражнений (аналог MyFitnessPal)"
    !identifiers hierarchical

    model {
        properties {
            structurizr.groupSeparator "/"
        }

        user = person "Пользователь" "Зарегистрированный пользователь: создаёт тренировки, упражнения, просматривает историю и статистику" {
            tags "Customer"
        }

        email_service = softwareSystem "Email Service" "Внешний сервис email-уведомлений (напоминания, отчёты)" {
            tags "ExternalSystem"
        }

        fitness_system = softwareSystem "Фитнес-трекер" "Система учёта тренировок и упражнений" {
            url "https://www.myfitnesspal.com/"

            client_app = container "Fitness Web Portal" "Веб-приложение для работы с пользователями, упражнениями и тренировками" "HTML, JavaScript, CSS" "WebBrowser" {
                technology "Web Application"
            }

            api_gateway = container "API Gateway" "Единая точка входа для REST API" "Nginx" "Container" {
                technology "Nginx"
            }

            user_db = container "User Database" "Хранение пользователей" "PostgreSQL 14" "Database" {
                technology "PostgreSQL 14"
            }
            exercise_db = container "Exercise Database" "Хранение упражнений" "PostgreSQL 14" "Database" {
                technology "PostgreSQL 14"
            }
            workout_db = container "Workout Database" "Хранение тренировок и связей с упражнениями" "PostgreSQL 14" "Database" {
                technology "PostgreSQL 14"
            }

            cache = container "Cache Server" "Кэширование частых запросов (списки упражнений, статистика)" "Redis" "Container" {
                technology "Redis"
            }

            user_api = container "User Service" "Пользователи: регистрация, поиск по логину и маске ФИО" "Java, Spring Boot / FastAPI" "Container" {
                technology "REST API"
                user_api -> user_db "CRUD пользователей" "JDBC:5432"
                user_api -> cache "Кэш профилей" "Redis:6379"
            }

            exercise_api = container "Exercise Service" "Упражнения: создание, список" "Java, Spring Boot / FastAPI" "Container" {
                technology "REST API"
                exercise_api -> exercise_db "CRUD упражнений" "JDBC:5432"
                exercise_api -> cache "Кэш справочника" "Redis:6379"
            }

            workout_api = container "Workout Service" "Тренировки: создание, добавление упражнений, история, статистика за период" "Java, Spring Boot / FastAPI" "Container" {
                technology "REST API"
                workout_api -> workout_db "CRUD тренировок" "JDBC:5432"
                workout_api -> cache "Кэш статистики" "Redis:6379"
                workout_api -> user_api "Проверка пользователя" "HTTPS:443"
                workout_api -> exercise_api "Получение упражнений" "HTTPS:443"
                workout_api -> email_service "Отчёты и напоминания" "HTTPS:443"
            }

            user -> client_app "Управление тренировками и статистикой" "HTTPS:443"
            client_app -> api_gateway "REST API запросы" "HTTPS:443"
            api_gateway -> user_api "Маршрутизация" "HTTPS:443"
            api_gateway -> exercise_api "Маршрутизация" "HTTPS:443"
            api_gateway -> workout_api "Маршрутизация" "HTTPS:443"
        }
    }

    views {
        properties {
            plantuml.format "svg"
            structurizr.sort "created"
            structurizr.tooltips "true"
        }

        themes default

        # C1 System Context
        systemContext fitness_system "system-context" "Контекст системы (C1)" {
            include *
            autoLayout
        }

        # C2 Container
        container fitness_system "container-diagram" "Контейнеры (C2)" {
            include *
            autoLayout
        }

        # Dynamic — создание тренировки (как у товарища: короткие номера шагов + протокол)
        dynamic fitness_system "dynamic-create-workout" "Создание тренировки" {
            autoLayout
            description "Создание тренировки и загрузка списка упражнений через API Gateway (вариант 14)"

            user -> fitness_system.client_app "1" "HTTPS:443"
            fitness_system.client_app -> fitness_system.api_gateway "2" "HTTPS:443"
            fitness_system.api_gateway -> fitness_system.workout_api "3" "HTTPS:443"
            fitness_system.workout_api -> fitness_system.user_api "4" "HTTPS:443"
            fitness_system.workout_api -> fitness_system.workout_db "5" "JDBC:5432"
            fitness_system.api_gateway -> fitness_system.exercise_api "6" "HTTPS:443"
            fitness_system.exercise_api -> fitness_system.exercise_db "7" "JDBC:5432"
            fitness_system.api_gateway -> fitness_system.workout_api "8" "HTTPS:443"
            fitness_system.workout_api -> fitness_system.workout_db "9" "JDBC:5432"
        }

        styles {
            element "Person" {
                shape Person
                fontSize 22
                color #ffffff
            }
            element "Customer" {
                background #08427b
            }
            element "ExternalSystem" {
                background #c0c0c0
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "WebBrowser" {
                shape WebBrowser
            }
        }
    }
}
