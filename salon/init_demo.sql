-- ============================================================
-- Салон красоты — создание БД + тестовые данные
-- Запуск: в MySQL Workbench открыть файл и нажать "Run All".
-- ============================================================

DROP DATABASE IF EXISTS salon;
CREATE DATABASE salon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE salon;

-- ---------------- 3НФ-схема ----------------
CREATE TABLE Gender (
  Code CHAR(1) PRIMARY KEY,
  Name VARCHAR(10) NOT NULL
);

CREATE TABLE Service (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Title VARCHAR(100) NOT NULL UNIQUE,
  Cost DECIMAL(10,2) NOT NULL,
  DurationInSeconds INT NOT NULL,
  Description TEXT,
  Discount DOUBLE DEFAULT 0,
  MainImagePath VARCHAR(255)
);

CREATE TABLE ServicePhoto (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  ServiceID INT NOT NULL,
  PhotoPath VARCHAR(255) NOT NULL,
  FOREIGN KEY (ServiceID) REFERENCES Service(ID)
);

CREATE TABLE Client (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  Patronymic VARCHAR(50),
  Birthday DATE,
  RegistrationDate DATETIME NOT NULL,
  Email VARCHAR(255),
  Phone VARCHAR(20) NOT NULL,
  GenderCode CHAR(1) NOT NULL,
  FOREIGN KEY (GenderCode) REFERENCES Gender(Code)
);

CREATE TABLE ClientService (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  ClientID INT NOT NULL,
  ServiceID INT NOT NULL,
  StartTime DATETIME NOT NULL,
  Comment TEXT,
  FOREIGN KEY (ClientID)  REFERENCES Client(ID),
  FOREIGN KEY (ServiceID) REFERENCES Service(ID)
);

-- ---------------- Тестовые данные ----------------

INSERT INTO Gender VALUES ('М','Мужской'), ('Ж','Женский');

INSERT INTO Service (Title, Cost, DurationInSeconds, Description, Discount, MainImagePath) VALUES
  ('Женская стрижка',           1500.00, 3600, 'Классическая стрижка с укладкой',                    0.00,  NULL),
  ('Мужская стрижка',           1000.00, 1800, 'Стрижка машинкой и ножницами',                       0.10,  NULL),
  ('Окрашивание волос',         3500.00, 7200, 'Окрашивание в один тон, краска включена',            0.15,  NULL),
  ('Мелирование',               4200.00, 9000, 'Мелирование, до 3 оттенков',                         0.20,  NULL),
  ('Маникюр классический',       800.00, 2700, 'Обрезной маникюр без покрытия',                      0.00,  NULL),
  ('Маникюр + гель-лак',        1800.00, 4500, 'Маникюр с покрытием гель-лаком, до 10 цветов',       0.05,  NULL),
  ('Педикюр',                   1600.00, 4500, 'Аппаратный педикюр',                                 0.00,  NULL),
  ('Укладка вечерняя',          1200.00, 3600, 'Праздничная укладка',                                0.30,  NULL),
  ('Бритьё опасной бритвой',     900.00, 1800, 'Классическое бритьё горячим полотенцем',             0.00,  NULL),
  ('Spa-уход за лицом',         2700.00, 5400, 'Чистка + маска + массаж лица',                       0.50,  NULL),
  ('Брови: коррекция + окрашивание', 700.00, 1800, 'Коррекция формы и окрашивание',                  0.00,  NULL),
  ('Наращивание ресниц',        2500.00, 7200, 'Классическое наращивание',                           0.75,  NULL);

INSERT INTO Client (FirstName, LastName, Patronymic, Birthday, RegistrationDate, Email, Phone, GenderCode) VALUES
  ('Анна',     'Иванова',   'Сергеевна',   '1992-04-15', '2024-01-10 10:00:00', 'ivanova@mail.ru',   '+79161234567', 'Ж'),
  ('Михаил',   'Петров',    'Александрович','1988-09-23', '2024-02-05 12:30:00', 'petrov@mail.ru',    '+79161234568', 'М'),
  ('Елена',    'Смирнова',  'Викторовна',  '1995-12-01', '2024-03-20 14:15:00', 'smirnova@mail.ru',  '+79161234569', 'Ж'),
  ('Андрей',   'Кузнецов',  'Дмитриевич',  '1985-06-30', '2024-04-12 09:45:00', 'kuznetsov@mail.ru', '+79161234570', 'М'),
  ('Ольга',    'Соколова',  NULL,          '2000-02-18', '2024-05-08 11:00:00', 'sokolova@mail.ru',  '+79161234571', 'Ж'),
  ('Дмитрий',  'Морозов',   'Олегович',    '1990-08-07', '2024-06-15 16:00:00', NULL,                '+79161234572', 'М'),
  ('Татьяна',  'Волкова',   'Игоревна',    '1978-11-25', '2024-07-02 13:30:00', 'volkova@mail.ru',   '+79161234573', 'Ж');

-- Несколько записей: сегодня, завтра и в прошлом
-- Используем NOW() и интервалы — данные останутся актуальными при любой дате запуска.
INSERT INTO ClientService (ClientID, ServiceID, StartTime, Comment) VALUES
  (1, 1, DATE_ADD(NOW(), INTERVAL 30 MINUTE), 'Спросить про любимую длину'),
  (2, 2, DATE_ADD(NOW(), INTERVAL 2 HOUR),    NULL),
  (3, 6, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 11 HOUR, 'Хочет тёмно-красный'),
  (4, 9, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 13 HOUR, NULL),
  (5, 10, DATE_ADD(NOW(), INTERVAL 45 MINUTE), 'Аллергия на эфирные масла'),
  (6, 3, DATE_SUB(NOW(), INTERVAL 2 DAY), 'Прошлая запись'),
  (7, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 15 HOUR + INTERVAL 30 MINUTE, NULL);

-- Проверка
SELECT 'Услуг' AS metric, COUNT(*) AS cnt FROM Service
UNION ALL SELECT 'Клиентов', COUNT(*) FROM Client
UNION ALL SELECT 'Записей',  COUNT(*) FROM ClientService;
