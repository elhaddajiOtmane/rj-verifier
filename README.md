# RJ Verifier

**RJ Verifier** is a powerful desktop tool for automating SheerID verifications and generating educational document proofs for ChatGPT Educator K-12. Built with **Electron**, **React**, and **Python**, it offers a seamless experience for both verification and document generation tasks.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Electron](https://img.shields.io/badge/Electron-Latest-47848F?logo=electron&logoColor=white)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/riiicil/rj-verifier/actions)
<!-- ![GitHub stars](https://img.shields.io/github/stars/riiicil/rj-verifier?style=social)
![GitHub forks](https://img.shields.io/github/forks/riiicil/rj-verifier?style=social) -->


**© Riiicil 2025**

> **Note:** This project is intended for educational and testing purposes.

## 🚀 Features

### 🔍 Verification Mode
*   **Automated Verification:** Quickly verify SheerID statuses using the underlying Python engine.
*   **School Selection:** Integrated drop-down with search for verified schools.
*   **Data Entry:** Easy-to-use form for personal details and identifiers.

### 📝 Generator Mode
*   **Document Creation:** Generate high-quality `.pdf` and `.png` payslips or teacher documents.
*   **Customization:** Supports custom logos and school details.
*   **Auto-Backup:** Automatically saves generated files to `Documents/RJ Verifier/doc_generated`.

### ✨ Engagement & UI
*   **Social Lock:** One-time "Follow to Unlock" mechanism to encourage community engagement.
*   **Donation Prompt:** Gentle "Buy me a coffee" reminder after every 5 uses.
*   **Modern UI:** Built with React for a responsive and clean dark-mode interface.

## 🛠️ Installation

### Prerequisites
*   **Node.js** (v16+)
*   **Python** (3.9+)
*   **Pip** (Python Package Installer)

### Development Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/riiicil/rj-verifier.git
    cd RJ-Verifier
    ```

2.  **Install Frontend Dependencies:**
    ```bash
    npm install
    ```

3.  **Install Backend Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Development Server:**
    ```bash
    npm run dev
    ```

### Building for Production
To create a standalone `.exe` installer:
```bash
npm run dist
```
The output will be in the `dist` folder.

## 📂 Project Structure

*   `electron/`: Main Electron process logic (`main.js`, `preload.js`).
*   `src/`: React frontend (`App.jsx`, components, styles).
*   `engine/`: Python backend logic for verification and generation.
*   `assets/`: Icons and default resources.


## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
