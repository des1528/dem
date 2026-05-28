-- ============================================================
-- Магазин обуви ООО «Обувь» — создание БД + тестовые данные
-- ============================================================

DROP DATABASE IF EXISTS shoes;
CREATE DATABASE shoes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shoes;

-- ---------------- Схема (3НФ) ----------------
CREATE TABLE Role         (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(40) UNIQUE NOT NULL);
CREATE TABLE Category     (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE Manufacturer (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE Supplier     (ID INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(80) UNIQUE NOT NULL);
CREATE TABLE PickupPoint  (ID INT AUTO_INCREMENT PRIMARY KEY, Address VARCHAR(255) UNIQUE NOT NULL);

CREATE TABLE User (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  RoleID INT NOT NULL,
  FIO VARCHAR(150) NOT NULL,
  Login VARCHAR(100) UNIQUE NOT NULL,
  Password VARCHAR(100) NOT NULL,
  FOREIGN KEY (RoleID) REFERENCES Role(ID)
);

CREATE TABLE Product (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Article VARCHAR(20) UNIQUE NOT NULL,
  Name VARCHAR(150) NOT NULL,
  Unit VARCHAR(20) NOT NULL,
  Price DECIMAL(10,2) NOT NULL,
  SupplierID INT, ManufacturerID INT, CategoryID INT,
  Discount INT DEFAULT 0, Stock INT NOT NULL DEFAULT 0,
  Description TEXT, ImagePath VARCHAR(255),
  FOREIGN KEY (SupplierID)     REFERENCES Supplier(ID),
  FOREIGN KEY (ManufacturerID) REFERENCES Manufacturer(ID),
  FOREIGN KEY (CategoryID)     REFERENCES Category(ID)
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
INSERT INTO Category     (Name) VALUES ('Женская обувь'),('Мужская обувь'),('Детская обувь'),('Спортивная обувь');
INSERT INTO Manufacturer (Name) VALUES ('Kari'),('Marco Tozzi'),('Ecco'),('Nike'),('Adidas'),('Ralf Ringer');
INSERT INTO Supplier     (Name) VALUES ('Kari'),('Обувь для вас'),('Спорт-Опт'),('РОСТ');
INSERT INTO PickupPoint  (Address) VALUES
  ('420151, г. Лесной, ул. Вишневая, 32'),
  ('125061, г. Лесной, ул. Подгорная, 8'),
  ('301234, г. Лесной, пр. Мира, 100');

-- ---------------- Пользователи (логины из 09.02.07-2 ресурсов) ----------------
INSERT INTO User (RoleID, FIO, Login, Password) VALUES
  (1, 'Никифорова Весения Николаевна', 'admin@shop.ru',   'admin123'),
  (2, 'Сидоров Иван Петрович',          'manager@shop.ru', 'manager123'),
  (3, 'Иванова Ольга Сергеевна',        'client@shop.ru',  'client123'),
  (3, 'Степанов Михаил Артёмович',      'mikhail@shop.ru', 'mikhail123');

-- ---------------- Товары ----------------
INSERT INTO Product (Article, Name, Unit, Price, SupplierID, ManufacturerID, CategoryID, Discount, Stock, Description, ImagePath) VALUES
  ('A112T4', 'Ботинки женские демисезонные', 'шт.', 4990.00, 1, 1, 1,  3,  6, 'Женские ботинки kari', NULL),
  ('F635R4', 'Ботинки женские Marco Tozzi',  'шт.', 3244.00, 2, 2, 1,  2, 13, 'Размер 39, цвет бежевый', NULL),
  ('B201E8', 'Туфли мужские Ecco',           'шт.', 8990.00, 2, 3, 2,  0,  4, 'Кожа, классика', NULL),
  ('S010N1', 'Кроссовки Nike Air',           'пара',6700.00, 3, 4, 4, 20,  0, 'Размер 42, чёрные', NULL),   -- нет на складе → серая карточка
  ('S011A1', 'Кроссовки Adidas Run',         'пара',5500.00, 3, 5, 4, 10, 15, 'Лёгкие, для бега', NULL),
  ('K005R3', 'Сапоги детские Ralf Ringer',   'пара',2890.00, 4, 6, 3,  0,  9, 'Зимние, мех', NULL),
  ('A234T5', 'Балетки женские Kari',         'пара',1990.00, 1, 1, 1, 50,  7, 'Скидка > 15% → тёмно-зелёная карточка', NULL),  -- проверка стиля М2
  ('B502R6', 'Полуботинки мужские Ralf',     'пара',6490.00, 4, 6, 2,  5, 12, 'Натуральная кожа', NULL);

-- ---------------- Заказы ----------------
INSERT INTO `Order` (OrderDate, DeliveryDate, PickupPointID, ClientFIO, Code, Status) VALUES
  (CURDATE() - INTERVAL 30 DAY, CURDATE() - INTERVAL 25 DAY, 1, 'Степанов Михаил Артёмович', 901, 'Завершен'),
  (CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 5 DAY,  2, 'Иванова Ольга Сергеевна',   902, 'Завершен'),
  (CURDATE() - INTERVAL 3 DAY,  NULL,                        2, 'Петров Иван Сергеевич',     903, 'В пути'),
  (CURDATE(),                   NULL,                        3, 'Кузнецова Анна Олеговна',   904, 'Новый');

INSERT INTO OrderItem (OrderID, ProductID, Qty) VALUES
  (1, 1, 2), (1, 2, 1),       -- этот заказ блокирует удаление товаров 1 и 2
  (2, 3, 1),
  (3, 5, 1), (3, 7, 2),
  (4, 8, 1);

-- ---------------- Проверка ----------------
SELECT 'Товаров'   AS m, COUNT(*) AS c FROM Product
UNION ALL SELECT 'Пользователей', COUNT(*) FROM User
UNION ALL SELECT 'Заказов',       COUNT(*) FROM `Order`
UNION ALL SELECT 'Позиций',       COUNT(*) FROM OrderItem;
