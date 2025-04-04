# AEDA: Proxy Re-Encrypted Key for AES Encryption Model

This repository contains the source code for our final year BTech project. Our work focuses on implementing a proxy re-encryption scheme for the AES encryption model. In this project, we have combined AES encryption with a re-encryption mechanism (using principles inspired by ElGamal encryption) to securely manage and transform keys between parties without exposing the underlying data.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture and File Structure](#architecture-and-file-structure)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Project Details](#project-details)
- [Collaborators](#collaborators)
- [Acknowledgments](#acknowledgments)

## Introduction

In today’s digital world, ensuring data confidentiality and secure key management is critical. This project demonstrates a novel approach by integrating AES—a robust symmetric encryption algorithm—with a proxy re-encryption scheme. Proxy re-encryption allows a semi-trusted proxy to transform ciphertexts from one key to another without learning anything about the underlying plaintext. This can be particularly useful in scenarios where secure key delegation or data sharing is required.

## Features

- **AES Encryption**: Implements the widely used AES algorithm for data encryption.
- **Proxy Re-Encryption**: Incorporates a mechanism to re-encrypt the AES key, inspired by ElGamal, allowing secure delegation of decryption rights.
- **Web Interface**: Includes a simple web-based interface (HTML, CSS, JavaScript) for user interaction, login, and message management.
- **Modular Code**: The project is structured into front-end (HTML/CSS/JS) and back-end (Python) components, enabling ease of development and potential future enhancements.

## Architecture and File Structure

The repository is organized into several directories and files:

- **css/**: Contains the stylesheet files used for styling the web interface.
- **js/**: Holds JavaScript files for client-side functionality.
- **images/**: Includes any images or icons used in the web application.
- **python/**: Contains the Python scripts which implement the core logic for encryption, decryption, and key re-encryption.
- **index.html**: The landing page for the project.
- **login.html**: Provides the login interface for user authentication.
- **message.html**: The page where encrypted messages can be viewed or managed.
- **users.db** and **users.db.backup**: Database files used for storing user credentials and related data.

## Installation and Setup

To set up the project locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Alphy777/AEDA.git
   cd AEDA
   ```

2. **Install Dependencies:**

   Make sure you have Python installed. You may need additional packages. For example, if the project uses specific libraries, install them using pip:

   ```bash
   pip install -r requirements.txt
   ```

   *(If there isn’t a requirements file, refer to the code comments or documentation for any additional dependencies.)*

3. **Run the Application:**

   Depending on how the backend is set up, you might run the Python script from the terminal:

   ```bash
   python python/main.py
   ```

4. **Access the Web Interface:**

   Open your browser and navigate to `http://localhost:8000` (or the port specified in your Python server configuration) to start using the web application.

## Usage

- **User Authentication:** Use the login page (`login.html`) to authenticate yourself. User credentials are stored in the provided database file (`users.db`).
- **Encryption/Decryption:** The application demonstrates the process of AES encryption combined with a proxy re-encryption method. Users can encrypt messages, and the proxy component will securely re-encrypt the AES key when needed.
- **Message Management:** Navigate to the message page (`message.html`) to view encrypted messages and test the encryption/decryption workflow.

## Project Details

This project was designed and developed as part of our final year BTech curriculum. It explores the practical application of proxy re-encryption in a modern encryption model. By securely re-encrypting AES keys, the project aims to address key management challenges and enhance data security when delegation is required. The methodology combines the efficiency of AES with the robust key transformation properties inspired by ElGamal.

## Collaborators

- **Alphy Jose**
- **Edwin Baby**
- **Donin C James**

We worked collaboratively to design, implement, and test this project, ensuring a balance between theoretical insights and practical application.


## Acknowledgments

We would like to express our heartfelt gratitude to our mentors and the academic community for their invaluable guidance and support throughout this project. We are also deeply thankful to our department for providing the necessary resources and encouragement that enabled us to bring this work to fruition. A special thanks to our parents and friends for their unwavering support and inspiration during this journey. Lastly, we extend our appreciation to the developers and maintainers of the open source modules and libraries that contributed significantly to the implementation of our project.

---
