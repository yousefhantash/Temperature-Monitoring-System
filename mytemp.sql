
-- Use the database
USE mytemp;

-- Create the switches table
CREATE TABLE switches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    switch VARCHAR(255) NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    community VARCHAR(255) NOT NULL,
    temperature VARCHAR(10) NOT NULL
);

-- Insert switch data
INSERT INTO switches (switch, ip_address, community, temperature) VALUES
('switch1', '192.168.1.1', 'public', '26C'),
('switch2', '192.168.1.2', 'public', '26C'),
('switch3', '192.168.1.3', 'public', '27C'),
('switch4', '192.168.1.4', 'public', '28C'),
('switch5', '192.168.1.5', 'public', '29C');