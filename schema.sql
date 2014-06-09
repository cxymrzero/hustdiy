DROP TABLE IF EXISTS stu_info_1;
DROP TABLE IF EXISTS stu_info_2;

CREATE TABLE stu_info_1
(
    id varchar(255),
    major varchar(255),
    grades int,
    cet int,
    PRIMARY KEY (id)
) DEFAULT CHARSET=utf8;

CREATE TABLE stu_info_2
(
    id varchar(255),
    live int,
    eat int,
    love int,
    org int,
    PRIMARY KEY (id)
) DEFAULT CHARSET=utf8;
