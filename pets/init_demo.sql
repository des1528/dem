-- ============================================================
-- ООО «Товары для животных» — создание БД + тестовые данные
-- ============================================================

DROP DATABASE IF EXISTS pets;
CREATE DATABASE pets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pets;

-- ---------------- Схема (3НФ) ----------------
CREATE TABLE Role         (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(40) UNIQUE NOT NULL);
CREATE TABLE Category     (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE Manufacturer (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE Supplier     (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE PickupPoint  (ID INT AUTO_INCREMENT PRIMARY KEY, Address VARCHAR(255) UNIQUE NOT NULL);

CREATE TABLE User (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  RoleID INT NOT NULL, FIO VARCHAR(150) NOT NULL,
  Login VARCHAR(100) UNIQUE NOT NULL, Password VARCHAR(100) NOT NULL,
  FOREIGN KEY (RoleID) REFERENCES Role(ID)
);

CREATE TABLE Product (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Article VARCHAR(20) UNIQUE NOT NULL, Name VARCHAR(150) NOT NULL,
  Unit VARCHAR(20) NOT NULL, Price DECIMAL(10,2) NOT NULL,
  SupplierID INT, ManufacturerID INT, CategoryID INT,
  Discount INT DEFAULT 0, Stock INT NOT NULL DEFAULT 0,
  Description TEXT, ImagePath VARCHAR(255),
  FOREIGN KEY (SupplierID)     REFERENCES Supplier(ID),
  FOREIGN KEY (ManufacturerID) REFERENCES Manufacturer(ID),
  FOREIGN KEY (CategoryID)     REFERENCES Category(ID)
);

CREATE TABLE AttachedProduct (
  MainProductID INT NOT NULL, AttachedProductID INT NOT NULL,
  PRIMARY KEY (MainProductID, AttachedProductID),
  FOREIGN KEY (MainProductID)     REFERENCES Product(ID),
  FOREIGN KEY (AttachedProductID) REFERENCES Product(ID)
);

CREATE TABLE `Order` (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  OrderDate DATE NOT NULL, DeliveryDate DATE,
  PickupPointID INT NOT NULL, ClientFIO VARCHAR(150),
  Code INT NOT NULL, Status VARCHAR(40) NOT NULL,
  FOREIGN KEY (PickupPointID) REFERENCES PickupPoint(ID)
);

CREATE TABLE OrderItem (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  OrderID INT NOT NULL, ProductID INT NOT NULL, Qty INT NOT NULL DEFAULT 1,
  FOREIGN KEY (OrderID)   REFERENCES `Order`(ID),
  FOREIGN KEY (ProductID) REFERENCES Product(ID)
);

-- ---------------- Справочники ----------------
INSERT INTO Role         (Name) VALUES ('Администратор'),('Менеджер'),('Клиент');
INSERT INTO Category     (Name) VALUES ('Корма'),('Игрушки'),('Аксессуары'),('Лежанки и домики'),('Ветпрепараты');
INSERT INTO Manufacturer (Name) VALUES ('Royal Canin'),('Pro Plan'),('Pedigree'),('Trixie'),('Ferplast'),('Pet Time');
INSERT INTO Supplier     (Name) VALUES ('ЗооОпт'),('Pet-Wholesale'),('Зоомир');
INSERT INTO PickupPoint  (Address) VALUES
  ('628300, г. Нефтеюганск, ул. Ленина, 12'),
  ('628303, г. Нефтеюганск, мкр. 11, д. 41'),
  ('628310, г. Нефтеюганск, пр. Победы, 5');

-- ---------------- Пользователи ----------------
INSERT INTO User (RoleID, FIO, Login, Password) VALUES
  (1, 'Сергеева Анна Викторовна',      'admin@pets.ru',   'admin123'),
  (2, 'Никифоров Олег Дмитриевич',     'manager@pets.ru', 'manager123'),
  (3, 'Кузнецова Ольга Сергеевна',     'client@pets.ru',  'client123'),
  (3, 'Морозов Андрей Петрович',       'morozov@pets.ru', 'morozov123');

-- ---------------- Товары ----------------
INSERT INTO Product (Article, Name, Unit, Price, SupplierID, ManufacturerID, CategoryID, Discount, Stock, Description, ImagePath) VALUES
  ('K001', 'Корм Royal Canin для котят 2 кг',      'шт.', 1850.00, 1, 1, 1, 0, 15, 'Сухой корм для котят возрастом 2-12 месяцев', NULL),
  ('K002', 'Корм Pro Plan для собак 3 кг',         'шт.', 2400.00, 1, 2, 1, 5, 22, 'Для взрослых собак средних пород', NULL),
  ('K003', 'Корм Pedigree влажный 100 г',          'шт.',   85.00, 2, 3, 1, 0, 60, 'Паучи с говядиной', NULL),
  ('I001', 'Мяч-пищалка Trixie',                   'шт.',  320.00, 3, 4, 2, 0, 30, 'Резиновый мяч 7 см', NULL),
  ('I002', 'Когтеточка-столбик Ferplast 60 см',    'шт.', 1950.00, 2, 5, 2, 10, 8,  'С верхушкой и шариком', NULL),
  ('A001', 'Поводок-рулетка 5 м',                  'шт.', 1100.00, 1, 4, 3, 0,  0, 'Закончилась — серый фон', NULL),
  ('A002', 'Ошейник кожаный M',                    'шт.',  650.00, 1, 6, 3, 0, 12, 'Натуральная кожа', NULL),
  ('L001', 'Лежак Pet Time круглый L',             'шт.', 2300.00, 3, 6, 4, 15, 5,  'Размер 60×60×15 см', NULL),
  ('L002', 'Домик-палатка для кошки',              'шт.', 1700.00, 3, 4, 4, 0,  3, 'Складной, на молнии', NULL),
  ('V001', 'Шампунь от блох 250 мл',               'шт.',  430.00, 2, 5, 5, 0, 18, 'Профилактический', NULL);

-- Дополнительные товары (self-many-to-many)
INSERT INTO AttachedProduct (MainProductID, AttachedProductID) VALUES
  (1, 4),    -- к корму для котят — мяч-пищалку
  (2, 7),    -- к корму Pro Plan — ошейник
  (5, 4);    -- к когтеточке — мяч

-- ---------------- Заказы ----------------
INSERT INTO `Order` (OrderDate, DeliveryDate, PickupPointID, ClientFIO, Code, Status) VALUES
  (CURDATE() - INTERVAL 40 DAY, CURDATE() - INTERVAL 35 DAY, 1, 'Кузнецова Ольга Сергеевна', 801, 'Завершен'),
  (CURDATE() - INTERVAL 7 DAY,  CURDATE() - INTERVAL 2 DAY,  2, 'Морозов Андрей Петрович',   802, 'Завершен'),
  (CURDATE() - INTERVAL 1 DAY,  NULL,                        3, 'Иванов Сергей Олегович',    803, 'В пути');

INSERT INTO OrderItem (OrderID, ProductID, Qty) VALUES
  (1, 1, 1), (1, 4, 2),   -- блокирует удаление товаров 1 и 4
  (2, 2, 1), (2, 7, 1),   -- блокирует 2 и 7
  (3, 8, 1);              -- блокирует 8

-- ---------------- Проверка ----------------
SELECT 'Товаров'      AS m, COUNT(*) AS c FROM Product
UNION ALL SELECT 'Пользователей',        COUNT(*) FROM User
UNION ALL SELECT 'Связок Attached',      COUNT(*) FROM AttachedProduct
UNION ALL SELECT 'Заказов',              COUNT(*) FROM `Order`
UNION ALL SELECT 'Позиций',              COUNT(*) FROM OrderItem;
