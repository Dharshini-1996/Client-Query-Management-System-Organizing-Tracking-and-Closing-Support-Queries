create database Test1;

use Test1;

create table login (
	username varchar(27),
    password varchar(255),
	role ENUM('Client', 'Support')

);
CREATE TABLE client_queries (
			id INT AUTO_INCREMENT PRIMARY KEY,
            email_id VARCHAR(255) NOT NULL,
            mobile_number VARCHAR(20) NOT NULL,
            query_heading VARCHAR(255) NOT NULL,
            query_description TEXT NOT NULL,
            query_created_time DATETIME NOT NULL,
            status VARCHAR(50) DEFAULT 'Open',
            query_closed_time DATETIME DEFAULT NULL
);

ALTER TABLE login
MODIFY COLUMN password VARCHAR(255);
select * from login;
select * from client_queries;