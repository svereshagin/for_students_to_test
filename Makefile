COMPOSE_FILE=docker-compose.yml

up:
	@docker-compose -f $(COMPOSE_FILE) up -d

down:
	@docker-compose -f $(COMPOSE_FILE) down

restart:
	@docker-compose -f $(COMPOSE_FILE) down
	@docker-compose -f $(COMPOSE_FILE) up -d

build:
	@docker-compose -f $(COMPOSE_FILE) build

ps:
	@docker-compose -f $(COMPOSE_FILE) ps

logs:
	@docker-compose -f $(COMPOSE_FILE) logs -f

clean:
	@docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans

app-shell:
	@docker-compose -f $(COMPOSE_FILE) exec app bash

postgres-shell:
	@docker-compose -f $(COMPOSE_FILE) exec postgres bash

test:
	@docker-compose -f $(COMPOSE_FILE) exec app pytest

help:
	@echo "Usage: make [command]"
	@echo "Commands:"
	@echo "  up             Поднять контейнеры"
	@echo "  down           Остановить и удалить контейнеры"
	@echo "  restart        Перезапустить контейнеры"
	@echo "  build          Собрать контейнеры"
	@echo "  ps             Показать статус контейнеров"
	@echo "  logs           Просмотр логов в реальном времени"
	@echo "  clean          Остановить контейнеры и удалить образы и тома"
	@echo "  app-shell      Запуск bash внутри контейнера app"
	@echo "  postgres-shell Запустить bash внутри контейнера postgres"
	@echo "  test           Запустить тесты"
