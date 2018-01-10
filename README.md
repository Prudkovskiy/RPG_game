RPG-game
===

**Игра в стиле RPG созданная на pygame**

## Цели проекта
* Познакомиться с инструментами Python для создания игровых процессов
* Разобраться с работой TCP/UDP – серверов
* Написать многопользовательскую сетевую игру

## Использовал
* **pygame** - библиотека Python, предназначенный для написания компьютерных игр и мультимедиа-приложений.

  ![pygame](./IMG/About_game/pygame.png)

* **pyganim** - для добавления анимаций в игру

  ![pyganim](./IMG/About_game/pyganim.png)

* **peewee** - orm для взаимодействия с БД

  ![peewee](./IMG/About_game/peewee.png)

* **sql** - СУБД для хранения информации об игроке

  ![sql](./IMG/About_game/sql.png)

## Как это выглядит
### Меню:
![menu](./IMG/About_game/Menu.png)

### Создание персонажа:
| персонаж  | повторное имя нельзя| рандомный персонаж  |
|---|---|---|
| ![person1](./IMG/About_game/person1.png)  | ![person2](./IMG/About_game/person2.png)  |  ![person3](./IMG/About_game/person3.png) |

### Настройки:
![options](./IMG/About_game/Options.png)

### Мир:
|таверна|город|внешний мир с драконами|
|---|---|---|
|![world1](./IMG/About_game/world1.png)|![world2](./IMG/About_game/world2.png)|![world3](./IMG/About_game/world3.png)|

### Битва:
![battle](./IMG/About_game/battle.png)

P.S. чтобы встретить драконов, необходимо немного потусоваться на зеленой лужайке внешнего мира :)

## Инструкция
Чтобы запустить игру, запустите server_TCP.py + server_UDP.py, а затем уже Runner.py и выбирайте offline режим.

Если вы хотите запустить игру в сети, то запустите cервера server_TCP.py и
server_UDP.py на своем хосте.
Измените поле HOST в others.py на адрес вашего хоста.
Также поменяйте порты в коде, на которых теперь крутятся эти два сервера.
Затем уже запускайте Runner.py
