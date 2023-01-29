BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS user (
   id INTEGER PRIMARY KEY,
   email TEXT NOT NULL,
   password TEXT NOT NULL
   );

CREATE TABLE IF NOT EXISTS b055 (
   id INTEGER PRIMARY KEY,
   nimda TEXT NOT NULL,
   ssapnimda TEXT NOT NULL
   );

CREATE TABLE IF NOT EXISTS logons (
   id INTEGER PRIMARY KEY,
   email TEXT NOT NULL,
   logins INTEGER NOT NULL
   );



INSERT OR IGNORE INTO b055 VALUES(1,'admin@foo.com','3dm3in');


CREATE TABLE IF NOT EXISTS product (
   id INTEGER PRIMARY KEY,
   name TEXT NOT NULL,
   description TEXT NOT NULL,
   price REAL,
   image TEXT
   );

INSERT OR IGNORE INTO product VALUES(1,'Linux Basics for Hackers , Getting Started with Networking, Scripting, and Security in Kali','Many aspiring hackers are unfamiliar with Linux, having learned computer basics in a Windows or Mac environment. This can pose the single most important obstacle to mastering the skills to becoming a better hacker; while hacking can be done with Windows or OS X, nearly all hacking tools are developed specifically for Linux. Linux Basics for Hackers aims to provide you with a foundation of Linux skills that every hacker needs. As you progress, you''ll have access to numerous real-world examples and hands-on exercises to apply your new knowledge and bring yourself up to speed.',14.990000000000000213,'LinuxBasics.jpg');
INSERT OR IGNORE INTO product VALUES(2,'The Web Application Hacker′s Handbook: Finding and Exploiting Security Flaws','Web applications are the front door to most organizations, exposing them to attacks that may disclose personal information, execute fraudulent transactions, or compromise ordinary users. This practical book has been completely updated and revised to discuss the latest step-by-step techniques for attacking and defending the range of ever-evolving web applications. You''ll explore the various new technologies employed in web applications that have appeared since the first edition and review the new attack techniques that have been developed, particularly in relation to the client side.',35.0,'WebAppHackers.jpg');
INSERT OR IGNORE INTO product VALUES(3,'Gray Hat Hacking: The Ethical Hacker"s Handbook, Fifth Edition','Fortify your network and avert digital catastrophe with proven strategies from a team of security experts. Completely updated and featuring 13 new chapters, Gray Hat Hacking: The Ethical Hacker’s Handbook, Fifth Edition explains the enemy’s current weapons, skills, and tactics and offers field-tested remedies, case studies, and ready-to-try testing labs. Find out how hackers gain access, overtake network devices, script and inject malicious code, and plunder Web applications and browsers. Android-based exploits, reverse engineering techniques, and cyber law are thoroughly covered in this state-of-the-art resource.',28.989999999999998436,'GrayHat.jpg');

CREATE TABLE IF NOT EXISTS review (
  id INTEGER PRIMARY KEY,
  userID INTEGER NOT NULL,
  productID INTEGER NOT NULL,
  stars INTEGER,
  review TEXT,
  FOREIGN KEY (userID)
       REFERENCES user (id),

  FOREIGN KEY (productID)
       REFERENCES product (id) 
  );

CREATE TABLE IF NOT EXISTS purchase (
  id INTEGER PRIMARY KEY,
  userID INTEGER NOT NULL,
  productID INTEGER NOT NULL,
  date DATE
  );
COMMIT;
