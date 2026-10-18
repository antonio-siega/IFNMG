create database if not exists ep1_webapi;

use ep1_webapi;

create table if not exists cliente(
	codigo INT PRIMARY KEY AUTO_INCREMENT,
    nome_completo VARCHAR(150) NOT NULL,
    idade INT(3) NOT NULL,
    telefone VARCHAR(30) NOT NULL,
    email VARCHAR(200) NOT NULL,
    foto TEXT
);