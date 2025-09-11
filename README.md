# Secure Website

## Overview

This project is a full-featured Book Shop website built using Python (Flask) for the backend, JavaScript for dynamic frontend interactions, and HTML/CSS for the user interface. The website offers a range of features from browsing and purchasing books to managing products and users for admins.

Built using Flask, see https://flask.palletsprojects.com/en/2.2.x/

## Instructions for Installation
     
  1. Clone the Repository

      ```
	 git clone https://github.com/yourusername/bookshop.git
	 cd bookshop
	 ```
  
  2. Install Requirements
  
     ```
	 pip install -r REQUIREMENTS.txt
	 ```
	
  3. Run
  
     ```
	 flask --app app/ --debug run
	 ```

The site should now be visible on 127.0.0.1:5000


## Usage

- Browse books without an account.
- Create an account to purchase books and write reviews.
- Admins can log in to manage products and users.

  
## Features

### User Features

- Browse Products: View a list of available books with detailed descriptions and prices.
- Product Reviews: Read and write reviews for books.
- Purchase Products: Securely buy books through the website.
- User Authentication: Sign up, log in, and manage your account.

### Admin Features

- Create Product: Add new books to the inventory.
- View Users: Manage user accounts.

### Security Features

- SQL Injection Mitigation: Secure database interactions to prevent SQL injection attacks.
- Cross-Site Scripting (XSS) Protection: Safeguards to prevent malicious scripts.
- Cross-Site Request Forgery (CSRF) Prevention: Implemented CSRF tokens to protect against CSRF attacks.
- Password Encryption: Secure storage of user passwords using encryption.
- Password Strength Verification: Ensures users create strong, secure passwords.

### Technologies Used

- Backend: Python (Flask)
- Frontend: JavaScript, HTML, CSS
- Database: SQLite
- Security: Python Libraries: bcrypt, markupsafe, csrf


## Screenshots

### Home Page

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/18dbd51a-d3a6-4dd5-9431-715b1132f214)


### Login

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/e85db69e-4ab5-42ab-abdf-d0a3bdd372b5)


### Create Account

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/740b3177-3b06-4cb2-afaa-10da8d941f05)


### Products

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/4c367453-898b-4adc-9510-4a290aabd4b3)


### Product Details

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/fad201b3-e808-4746-92e5-226ce97b8dd0)


### Buy Product

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/76024b08-2839-4635-96c7-0c0d450aea39)

### User Settings

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/9d3f98e0-24d8-42ad-ad45-27377f7fff08)



### Create Product (Admin Feature)

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/fdc25a8c-c494-4225-8dbf-5b498f9d1bb9)


### View Users (Admin Feature)

![image](https://github.com/venkataprabhav/Python---Flask_Secure_Website/assets/123014399/5464a8c8-c906-4c73-92c4-d13851e6abd2)






