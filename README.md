# Проект “Симуляция”
Пошаговая симуляция 2D мира, населённого травоядными и хищниками. Кроме существ, мир содержит ресурсы (траву), которыми питаются травоядные, и статичные объекты.

2D мир представляет из себя матрицу NxM, каждое существо или объект занимают клетку целиком.

### Installation

1) Склонировать репозиторий
```shell
git clone https://github.com/Doworder/Simulation.git
```
2) Перейти в папку проекта
```shell
cd Simulation
```
3) Создать виртуальное окружение
```shell
python -m venv venv
```
4) Активировать виртуальное окружение
Windows

```shell
venv\Scripts\activate.bat
```

Linux и MacOS

```shell
source venv/bin/activate
```
5) Установить пакет
```shell
pip install .
```
6) (Опционально). Скопировать пример конфига в config.toml. Открыть config.toml в текстовом редакторе и изменить параметры в соответствии с [документацией](config_README.md)
```shell
cp config.example.toml config.toml
```
7) Запустить симуляцию
```shell
simulation
```

В дальнейшем - следуем указаниям на экране.
