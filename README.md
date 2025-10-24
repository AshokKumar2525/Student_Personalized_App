# 🎓 Student Personalized App (SPA)

The **Student Personalized App (SPA)** is an AI-powered mobile application designed to assist students in academics, fitness, personal growth, **finance management**, and career opportunities.  
It combines smart recommendations, personalized alerts, and real-time integrations to help students stay productive and balanced in their daily lives.

---

## 🚀 Features

- 📱 **Personalized Dashboard** – unified view of academic, health, finance, and personal progress.  
- 📰 **Tech Updates** – latest curated tech news & trends.  
- 💪 **Body Fitness Tracking** – integrates with Google Fit / device sensors to track steps, calories, workouts.  
- 📊 **Academic Performance Monitoring** – track grades, progress charts, and predictions.  
- ⏰ **Medical Alerts** – health reminders and notifications.  
- 🗣️ **English Communication Support** – daily tips, vocabulary, and AI-driven grammar feedback.  
- 📚 **Domain Topic Suggestions** – AI-powered topic recommendations for study and projects.  
- 🎓 **Scholarship Finder** – notifications on relevant scholarship opportunities.  
- 📧 **Email Summarization** – integrates with Gmail/Outlook for quick summaries of important mails.  
- 💰 **Finance Tracker** – helps students manage expenses, budgets, and savings with visual insights.  
- 🔍 **Discover Section** – personalized suggestions for courses, events, and opportunities.  

---

## 🛠️ Tech Stack

- **Frontend:** Flutter (Dart)
- **Backend:** Node.js + Express.js  
- **Database:** MongoDB  
- **AI/ML:** OpenAI / Gemini LLMs for summarization & topic generation  
- **APIs:** 
  - Gmail API (for email summarization)  
  - Google Fit API (for fitness data)  
  - News API (for tech updates)  
  - Scholarship databases  
  - Currency/Finance API (for expense tracking & analytics)
- **Auth:** Google Firebase

---

## 📋 Requirements

### Functional
- User login & profile management  
- Fetch and store academic, fitness, and finance data  
- Summarize emails & news content  
- AI-based topic, finance, and scholarship recommendations  

### Non-Functional
- 🔒 Secure authentication (OAuth2 for Gmail, JWT for app)  
- ⚡ Fast API responses (<3 sec for summarization)  
- 🌐 Cross-platform (Android/iOS)  

---

## 📸 Screens (Planned)

- 🏠 **Home Dashboard** – quick overview  
- 📊 **Performance Tab** – academic + fitness reports  
- 💰 **Finance Tab** – expense tracker, budget goals, charts  
- 📰 **Tech Tab** – latest news  
- 📚 **Learning Tab** – English + topic suggestions  
- 🎓 **Scholarships Tab** – opportunities feed   

---

## 🏗️ Installation & Setup

### 1️⃣ Prerequisites
Before running the app, make sure you have installed:

- Flutter SDK ≥ 3.9 ([Flutter installation guide](https://docs.flutter.dev/get-started/install))  
- Android Studio / VS Code with Flutter plugin  
- Node.js ≥ 18.x  
- Git  
- Firebase CLI (optional, for adding Firebase services locally)  

---

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/<your username>/Student_Personalized_App.git
cd Student_Personalized_App
```
### 3️⃣ Backend Setup
```bash
cd backend
npm install
npm start
```
### 4️⃣ Flutter Frontend Setup
```bash
cd spa
flutter pub get
```

### 5️⃣ Firebase Setup
```bash
dart pub global activate flutterfire_cli
flutterfire configure

# next run
keytool -list -v -alias androiddebugkey -keystore %USERPROFILE%\.android\debug.keystore
# if it asks password enter ==> android
# For Google Sign-In, register your debug SHA-1 key in Firebase (Android) to avoid auth errors:  
```
### 6️⃣ Run
```bash
# Before running check whether you have all dependencies
flutter doctor

# List available devices:
flutter devices

# Run the app:
flutter run -d <device_id>
```
---

## 👨‍💻 Contributors

- **Ashok Kumar Malineni**
- **Jyothi Reddy Nangamangalam**
- **S.Dev Deepak**
- **C.V.S.Mahendra**
---

## 📌 Future Scope

- Group study rooms with AI support  
- Mentor–student chat integration  
- Voice-based assistant mode  
- Smart finance suggestions based on spending behavior

  
## 📜 License
This project is licensed under the MIT License.
