SELECT * FROM users; -- Standard check
SELEKT name FROM employees; 
INSERT INTO products VALUES (101, 'Laptop', 1500);
/* Systematic cleanup */ DELETE FROM logs;
CREATE TABLE (id INT); 
GRANT SELECT, UPDATE ON db TO manager;
SELECT id, price FROM items WHERE price = 50 AND status LIKE 'available';
ALTER TABLE profile UPDATE user SET bio = 'Developer';
DROP TABLE old_data, temp_records;
INSERT INTO orders (id, qty) VALUES (5, 10);
-- Typo in the next one
DELETE FROM sessions whre user_id = 99;
SELECT * FROM archive WHERE date LIKE '2025%';
REVOKE ALL ON settings FROM guest;
CREATE TABLE staff (name IDENTIFIER, age NUMBER);
DROP items_table;
/* Check if 
   multiline comments
   work here */
SELECT name FROM users WHERE id = ;
INSERT INTO basket VALUES (1, 'Apple');
GRANT FLY ON cockpit TO pilot;
ALTER TABLE inventory UPDATE stock SET qty = 100;
SELECT * FROM users WHERE active = 1 OR role LIKE 'admin';
CREATE TABLE logs (id NUMBER msg STRING); -- Missing comma
REVOKE DELETE ON finance FROM accountant;
DELETE FROM cache;
SELECT name age FROM table; -- Missing comma between columns
INSERT INTO values (1, 'error');
GRANT SELECT, INSERT, DELETE ON backup TO system;
DROP TABLE single_table;
SELECT * FROM products WHERE id = 10 AND ; -- Trailing operator



INSERT INTO users (id, name, email) VALUES (1, 'Alice'); 


INSERT INTO users (id, name) VALUES (2, 'Bob');