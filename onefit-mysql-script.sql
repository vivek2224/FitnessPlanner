create database onefit;

use onefit;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_role INT,
    name VARCHAR(255),
    email VARCHAR(255),
    pass VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    nutritionist INT,
    feedback VARCHAR(255),
    PRIMARY KEY (user_id)
);

CREATE TABLE goals (
    user_id INT,
    date VARCHAR(10),
    category VARCHAR(255),
    amount INT,
    completion VARCHAR(255)
);

CREATE TABLE fitness (
    user_id INT,
    date VARCHAR(10),
    height INT,
    weight INT,
    BMI INT,
    BMR INT,
    waterIntake INT,
    caloriesIntake INT,
    caloriesBurned INT,
    burnGoalAmount INT
);

CREATE TABLE exercise (
    user_id INT,
    date VARCHAR(10),
    category VARCHAR(255),
    exerciseAmount INT
);

insert into users values(1, 0, "Joe Smith", "joe@gmail.com", "password", 20, "Male", 2, "I think your data looks good"); 
insert into users values(2, 1, "Pat Brown", "pat@gmail.com", "password", 27, "Female", null, null); 
insert into users values(3, 0, "Amy Davis", "amy@gmail.com", "password", 23, "Female", 2, null); 
insert into users values(4, 1, "Bob Jones", "bob@gmail.com", "password", 30, "Male", null, null); 
insert into goals values(1, "12/9/21", "Weight", 150, null); 
insert into goals values(1, "12/9/21", "Net Calories", 2000, null);
insert into goals values(1, "12/8/21", "Weight", 145, "12/9/21");  
insert into fitness values(1, "12/8/21", 70, 150, 21, 1800, 40, 2000, 1000, 800); 
insert into fitness values(1, "12/9/21", 70, 145, 19, 1600, 30, 1000, 400, 900); 
insert into fitness values(1, "12/10/21", 70, 148, 20, 1700, 50, 3000, 800, 700); 
insert into exercise values(1, "12/9/21", "miles run", 1); 
insert into exercise values(1, "12/10/21", "miles run", 2); 
insert into exercise values(1, "12/9/21", "weight lifted", 30); 
insert into exercise values(1, "12/10/21", "weight lifted", 50); 
insert into exercise values(1, "12/9/21", "cardio", 45); 
insert into exercise values(1, "12/10/21", "cardio", 60);
